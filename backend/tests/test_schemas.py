"""Schema validation tests (offline — no API key required)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import Category, TriageRequest, TriageResult, Urgency

VALID_RESULT = {
    "category": "tenancy_and_housing",
    "jurisdiction": "South Australia",
    "confidence": 0.9,
    "urgency": "medium",
    "summary": "You may be able to recover your bond.",
    "suggested_next_step": "We can help you put together an application.",
    "escalate_to_professional": False,
    "needs_clarification": False,
}


def test_valid_result_parses() -> None:
    result = TriageResult(**VALID_RESULT)
    assert result.category is Category.tenancy_and_housing
    assert result.urgency is Urgency.medium
    assert result.clarifying_question is None


def test_confidence_out_of_range_is_rejected() -> None:
    bad = {**VALID_RESULT, "confidence": 1.4}
    with pytest.raises(ValidationError):
        TriageResult(**bad)


def test_unknown_category_is_rejected() -> None:
    bad = {**VALID_RESULT, "category": "criminal_law"}
    with pytest.raises(ValidationError):
        TriageResult(**bad)


def test_request_rejects_empty_description() -> None:
    with pytest.raises(ValidationError):
        TriageRequest(description="")


def test_request_accepts_normal_text() -> None:
    req = TriageRequest(description="My landlord won't return my bond.")
    assert "bond" in req.description
