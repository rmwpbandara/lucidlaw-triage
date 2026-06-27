"""FastAPI application.

Uses the application-factory pattern so the app can be constructed cleanly for
both serving and testing. The triage engine is created once at startup and
shared via application state; routes depend on it through a small dependency.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import Settings, get_settings
from app.logging_config import configure_logging, get_logger
from app.schemas import HealthResponse, TriageRequest, TriageResult
from app.triage.engine import (
    TriageCreditError,
    TriageEngine,
    TriageEngineError,
    TriageUnavailableError,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure logging and build the engine on startup."""
    settings = get_settings()
    configure_logging(settings.log_level)

    try:
        app.state.engine = TriageEngine.from_settings(settings)
        logger.info("Triage engine ready (model=%s).", settings.model)
    except TriageUnavailableError as exc:
        # Boot anyway so /health and /docs work; /api/triage returns 503.
        app.state.engine = None
        logger.warning("Triage engine not configured: %s", exc)

    yield


def get_engine(request: Request) -> TriageEngine:
    """Dependency that returns the live engine or a clean 503."""
    engine = getattr(request.app.state, "engine", None)
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Triage is not configured. Set ANTHROPIC_API_KEY and restart.",
        )
    return engine


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings: Settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "Plain-language legal triage for everyday Australians. "
            "Describe a situation; receive a structured, supportive assessment."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    def health() -> HealthResponse:
        """Liveness check, including whether triage is configured."""
        engine = getattr(app.state, "engine", None)
        return HealthResponse(
            status="ok",
            model=settings.model,
            triage_available=engine is not None,
        )

    @app.post("/api/triage", response_model=TriageResult, tags=["triage"])
    def triage(
        payload: TriageRequest,
        engine: Annotated[TriageEngine, Depends(get_engine)],
    ) -> TriageResult:
        """Classify a plain-language description into a structured triage result."""
        try:
            return engine.run(payload.description)
        except TriageCreditError as exc:
            logger.error("Triage unavailable — Anthropic account out of credit: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Our triage assistant is temporarily unavailable because the Claude API "
                    "account is out of credit. Please add credit to the API key and try again."
                ),
            ) from exc
        except TriageEngineError as exc:
            logger.error("Triage failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="We couldn't assess that just now. Please try again in a moment.",
            ) from exc

    return app


app = create_app()
