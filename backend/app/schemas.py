"""The API data contract.

These Pydantic models are the single source of truth for what the service
accepts and returns. Validating Claude's structured output against
``TriageResult`` guarantees the API can never emit a malformed response — an
invalid ``confidence`` or an unknown ``category`` is rejected at the boundary.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Category(StrEnum):
    """The four launch categories LucidLaw triages at MVP stage."""

    tenancy_and_housing = "tenancy_and_housing"
    employment = "employment"
    consumer_rights = "consumer_rights"
    family_law = "family_law"


class Urgency(StrEnum):
    """How time-sensitive the person's situation appears to be."""

    low = "low"
    medium = "medium"
    high = "high"


class TriageRequest(BaseModel):
    """A plain-language description of the person's situation."""

    description: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description="What's going on, in the person's own words.",
        examples=["My landlord in Adelaide won't return my bond after 6 weeks."],
    )


class TriageResult(BaseModel):
    """The structured triage assessment returned for every request."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "tenancy_and_housing",
                "jurisdiction": "South Australia",
                "confidence": 0.92,
                "urgency": "medium",
                "summary": (
                    "You may be able to recover your bond if your landlord can't show "
                    "evidence of damage beyond normal wear and tear."
                ),
                "suggested_next_step": (
                    "We can help you put together a clear bond-recovery application for "
                    "SACAT — it usually takes about 10 minutes."
                ),
                "escalate_to_professional": False,
                "needs_clarification": False,
                "clarifying_question": None,
            }
        }
    )

    # --- Mandatory fields (required by the brief) --------------------------
    category: Category = Field(..., description="The single closest area of law.")
    jurisdiction: str = Field(
        ...,
        description="Australian state/territory, or 'Australia — state not specified'.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How confident the classification is, from 0 to 1.",
    )
    urgency: Urgency = Field(..., description="low, medium, or high.")
    summary: str = Field(..., description="One plain-language sentence in LucidLaw's voice.")
    suggested_next_step: str = Field(
        ..., description="One supportive, practical next step in LucidLaw's voice."
    )
    escalate_to_professional: bool = Field(
        ..., description="True if the person should speak with a professional soon."
    )

    # --- Added fields — honest ambiguity handling (brief welcomes extras) --
    needs_clarification: bool = Field(
        default=False,
        description="True when the situation is ambiguous or may fall outside the four areas.",
    )
    clarifying_question: str | None = Field(
        default=None,
        description="A gentle question to narrow things down when clarification is needed.",
    )


class HealthResponse(BaseModel):
    """Liveness response for the /health endpoint."""

    status: str = "ok"
    model: str
    triage_available: bool
