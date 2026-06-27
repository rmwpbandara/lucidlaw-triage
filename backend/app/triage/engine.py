"""The triage engine.

Encapsulates the full classification flow:

    description -> Claude (forced tool use) -> brand-voice check -> validate

The engine is a class with its dependencies injected (the Anthropic client and
settings), which keeps it testable and free of module-level global state.
"""

from __future__ import annotations

from typing import Any

import anthropic

from app.config import Settings
from app.logging_config import get_logger
from app.schemas import TriageResult
from app.triage.guardrails import find_violations
from app.triage.prompt import SYSTEM_PROMPT
from app.triage.tool import TOOL_NAME, TRIAGE_TOOL

logger = get_logger(__name__)


class TriageEngineError(RuntimeError):
    """Raised when the engine cannot produce a valid result."""


class TriageUnavailableError(TriageEngineError):
    """Raised when the engine is not configured (e.g. missing API key)."""


class TriageCreditError(TriageEngineError):
    """Raised when the Anthropic account has no remaining credit/billing access."""


def _is_credit_error(exc: Exception) -> bool:
    """True when an Anthropic error indicates the account is out of credit.

    The API returns HTTP 400 with the message "Your credit balance is too low
    to access the Anthropic API." when billing is exhausted. We match on that
    text (the reliable signal) and, as a fallback, a 400 mentioning billing.
    """
    text = str(exc).lower()
    if "credit balance is too low" in text:
        return True
    status_code = getattr(exc, "status_code", None)
    return status_code == 400 and ("credit" in text or "billing" in text)


class TriageEngine:
    """Classifies a plain-language description into a structured triage result."""

    def __init__(self, client: anthropic.Anthropic, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    @classmethod
    def from_settings(cls, settings: Settings) -> TriageEngine:
        """Build an engine from settings, or raise if it cannot be configured."""
        if not settings.anthropic_api_key:
            raise TriageUnavailableError(
                "ANTHROPIC_API_KEY is not set. Add it to the environment to enable triage."
            )
        client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.request_timeout_seconds,
        )
        return cls(client=client, settings=settings)

    # -- internal ----------------------------------------------------------
    def _call_claude(self, description: str, extra_system: str = "") -> dict[str, Any]:
        """Call Claude with forced tool use and return the raw tool input dict."""
        try:
            response = self._client.messages.create(
                model=self._settings.model,
                max_tokens=self._settings.max_tokens,
                system=SYSTEM_PROMPT + extra_system,
                tools=[TRIAGE_TOOL],
                tool_choice={"type": "tool", "name": TOOL_NAME},
                messages=[{"role": "user", "content": description}],
            )
        except anthropic.APIError as exc:  # network / auth / rate limit / billing
            if _is_credit_error(exc):
                logger.error("Anthropic account out of credit: %s", exc)
                raise TriageCreditError(str(exc)) from exc
            logger.error("Anthropic API error: %s", exc)
            raise TriageEngineError(f"Upstream model error: {exc}") from exc

        for block in response.content:
            if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
                return dict(block.input)

        raise TriageEngineError("The model did not return the expected tool call.")

    # -- public ------------------------------------------------------------
    def run(self, description: str) -> TriageResult:
        """Triage a description and return a validated result."""
        data = self._call_claude(description)

        # Brand-voice guardrail: if combative language slipped through, retry
        # once with a reinforced instruction before giving up on the wording.
        violations = find_violations(data.get("summary", ""), data.get("suggested_next_step", ""))
        if violations and self._settings.brand_voice_retries > 0:
            logger.info("Brand-voice retry triggered for terms: %s", violations)
            reminder = (
                "\n\nIMPORTANT: Your previous wording used forbidden combative words "
                f"({', '.join(violations)}). Rewrite summary and suggested_next_step "
                "with warm, resolution-first language and none of those words."
            )
            data = self._call_claude(description, extra_system=reminder)

        # Validate at the boundary — guarantees a well-formed contract.
        return TriageResult(**data)
