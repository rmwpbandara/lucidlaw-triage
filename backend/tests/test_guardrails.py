"""Brand-voice guardrail tests (offline — no API key required)."""

from __future__ import annotations

from app.triage.guardrails import find_violations


def test_detects_combative_words() -> None:
    violations = find_violations(
        "You should sue your landlord.",
        "This dispute may go to litigation.",
    )
    assert "sue" in violations
    assert "dispute" in violations
    assert "litigation" in violations


def test_clean_text_has_no_violations() -> None:
    violations = find_violations(
        "You may be able to recover your bond.",
        "We can help you write a clear letter to your landlord.",
    )
    assert violations == []


def test_word_boundaries_avoid_false_positives() -> None:
    # "pursue" and "issue" contain "sue" but must not match.
    violations = find_violations("We can pursue a clear path on this issue.")
    assert violations == []
