"""Brand-voice guardrail.

LucidLaw's voice is a hard requirement, not a preference: every user-facing
sentence must be warm and resolution-first, never combative or legalistic.
Prompts can drift, so this small detector enforces the rule in code. When a
banned term slips through, the engine retries once with a reinforced instruction.
"""

from __future__ import annotations

import re

# Combative / adversarial / legalistic words that violate LucidLaw's voice.
BANNED_TERMS: tuple[str, ...] = (
    "dispute",
    "litigation",
    "lawsuit",
    "sue",
    "suing",
    "opposing party",
    "victim",
    "fight",
    "battle",
    "pursue them",
    "against them",
    "claimant",
    "adversary",
    "plaintiff",
    "defendant",
)


def find_violations(*texts: str) -> list[str]:
    """Return any banned terms found in the given user-facing strings.

    Matching is word-boundary aware and case-insensitive, so "sue" matches in
    "sue them" but not inside "issue" or "pursue".
    """
    blob = " ".join(text.lower() for text in texts if text)
    hits: list[str] = []
    for term in BANNED_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", blob):
            hits.append(term)
    return hits
