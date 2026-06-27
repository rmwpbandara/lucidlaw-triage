"""The structured-output tool definition.

Rather than asking Claude for JSON in prose and parsing it (brittle), we define
a tool and force the model to call it via ``tool_choice``. Claude then returns a
JSON object that already conforms to this schema — the reliable, production way
to get structured data out of an LLM.
"""

from __future__ import annotations

from typing import Any

TOOL_NAME = "provide_triage_result"

TRIAGE_TOOL: dict[str, Any] = {
    "name": TOOL_NAME,
    "description": "Return the structured triage assessment for the described situation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": [
                    "tenancy_and_housing",
                    "employment",
                    "consumer_rights",
                    "family_law",
                ],
                "description": "The single closest category.",
            },
            "jurisdiction": {
                "type": "string",
                "description": (
                    "Australian state/territory, or 'Australia — state not specified'."
                ),
            },
            "confidence": {
                "type": "number",
                "description": "Confidence in the classification, from 0.0 to 1.0.",
            },
            "urgency": {
                "type": "string",
                "enum": ["low", "medium", "high"],
            },
            "summary": {
                "type": "string",
                "description": (
                    "One plain-language sentence in LucidLaw's warm, non-combative voice."
                ),
            },
            "suggested_next_step": {
                "type": "string",
                "description": "One supportive, practical next step in LucidLaw's voice.",
            },
            "escalate_to_professional": {
                "type": "boolean",
                "description": "True if the person should speak with a professional soon.",
            },
            "needs_clarification": {
                "type": "boolean",
                "description": (
                    "True when the situation is ambiguous or may fall outside the four areas."
                ),
            },
            "clarifying_question": {
                "type": ["string", "null"],
                "description": (
                    "A gentle question to narrow things down when needs_clarification is true."
                ),
            },
        },
        "required": [
            "category",
            "jurisdiction",
            "confidence",
            "urgency",
            "summary",
            "suggested_next_step",
            "escalate_to_professional",
            "needs_clarification",
        ],
    },
}
