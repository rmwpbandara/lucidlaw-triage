"""Constants and prompt-composition tests (offline — no API key required)."""

from __future__ import annotations

from app.schemas import Category
from app.triage.categories import (
    CATEGORY_GUIDE,
    JURISDICTION_DEFAULT,
    JURISDICTIONS,
)
from app.triage.prompt import SYSTEM_PROMPT
from app.triage.tool import TRIAGE_TOOL


def test_category_guide_covers_every_enum_value() -> None:
    assert set(CATEGORY_GUIDE) == {c.value for c in Category}


def test_tool_enum_matches_category_enum() -> None:
    tool_categories = set(TRIAGE_TOOL["input_schema"]["properties"]["category"]["enum"])
    assert tool_categories == {c.value for c in Category}


def test_default_jurisdiction_present_in_prompt() -> None:
    assert JURISDICTION_DEFAULT in SYSTEM_PROMPT


def test_prompt_includes_every_category() -> None:
    for name in CATEGORY_GUIDE:
        assert name in SYSTEM_PROMPT


def test_all_states_are_distinct() -> None:
    assert len(JURISDICTIONS) == len(set(JURISDICTIONS)) == 8
