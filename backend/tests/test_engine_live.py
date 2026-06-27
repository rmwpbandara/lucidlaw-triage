"""Live integration test (requires ANTHROPIC_API_KEY).

Runs the five required inputs against the real Claude API and asserts on the
*structure* of each result — never the exact wording, which the model writes.
Skipped automatically when no key is present so the offline suite stays green.

Run explicitly with:  pytest -s -m live
"""

from __future__ import annotations

import os

import pytest

from app.config import get_settings
from app.schemas import TriageResult
from app.triage.engine import TriageEngine
from app.triage.guardrails import find_violations

pytestmark = pytest.mark.live

requires_key = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set; skipping live API test.",
)


@requires_key
def test_five_required_cases(required_cases: list[str]) -> None:
    engine = TriageEngine.from_settings(get_settings())

    for text in required_cases:
        result = engine.run(text)

        # Contract holds for every input.
        assert isinstance(result, TriageResult)
        assert 0.0 <= result.confidence <= 1.0

        # Brand voice holds for every output.
        assert find_violations(result.summary, result.suggested_next_step) == []

        print(f"\nINPUT: {text}\n{result.model_dump_json(indent=2)}")
