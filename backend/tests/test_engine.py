"""Triage engine error-mapping tests (offline — no API key required).

These verify that an out-of-credit Anthropic response is recognised and surfaced
as a distinct ``TriageCreditError`` (so the API can return a clear message),
while unrelated upstream errors stay generic.
"""

from __future__ import annotations

import anthropic
import httpx
import pytest

from app.config import Settings
from app.triage.engine import (
    TriageCreditError,
    TriageEngine,
    TriageEngineError,
    _is_credit_error,
)

_CREDIT_MESSAGE = "Your credit balance is too low to access the Anthropic API."


class _RaisingMessages:
    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def create(self, **_: object) -> None:
        raise self._exc


class _FakeClient:
    """Stand-in Anthropic client whose ``messages.create`` always raises."""

    def __init__(self, exc: Exception) -> None:
        self.messages = _RaisingMessages(exc)


def _engine_raising(exc: Exception) -> TriageEngine:
    return TriageEngine(client=_FakeClient(exc), settings=Settings())


def _api_error(message: str) -> anthropic.APIError:
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return anthropic.APIError(message, request, body=None)


def test_is_credit_error_matches_billing_message() -> None:
    assert _is_credit_error(Exception(_CREDIT_MESSAGE))


def test_is_credit_error_ignores_unrelated_errors() -> None:
    assert not _is_credit_error(Exception("Connection timed out"))


def test_engine_maps_out_of_credit_to_credit_error() -> None:
    engine = _engine_raising(_api_error(_CREDIT_MESSAGE))
    with pytest.raises(TriageCreditError):
        engine.run("My landlord won't return my bond.")


def test_engine_maps_other_api_errors_to_generic_error() -> None:
    engine = _engine_raising(_api_error("Overloaded"))
    with pytest.raises(TriageEngineError) as info:
        engine.run("My landlord won't return my bond.")
    assert not isinstance(info.value, TriageCreditError)
