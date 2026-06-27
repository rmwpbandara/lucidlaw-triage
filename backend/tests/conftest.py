"""Shared test fixtures.

The five required inputs from the brief are exposed as a fixture so both the
offline structural tests and the live integration test use the same cases.
"""

from __future__ import annotations

import pytest

# The five test inputs the deployed prototype must handle (from the brief).
REQUIRED_CASES: list[str] = [
    "My landlord in Adelaide is refusing to return my bond even though I left "
    "the place clean. It's been 6 weeks.",
    "I was made redundant last week with no notice and they haven't paid out "
    "my leave. I've worked there for four years.",
    "I bought a laptop three months ago and the screen has completely failed. "
    "The store is refusing to refund or replace it.",
    "My partner and I are separating. We have two kids and we can't agree on where they'll live.",
    "Someone keeps parking in my driveway and I can't get them to stop.",
]


@pytest.fixture
def required_cases() -> list[str]:
    return REQUIRED_CASES
