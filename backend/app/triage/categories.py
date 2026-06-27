"""Domain constants for the triage engine.

Keeping the category definitions and jurisdiction data in one place makes the
taxonomy easy to review and extend (the production system would load this from
a database keyed by jurisdiction).
"""

from __future__ import annotations

# Plain-language description of what each category covers. These mirror the
# brief's taxonomy and are injected into the system prompt.
CATEGORY_GUIDE: dict[str, str] = {
    "tenancy_and_housing": (
        "Renting and housing: bond recovery, repairs and maintenance, entry "
        "without notice, strata/body corporate, and neighbour issues."
    ),
    "employment": (
        "Work: unfair dismissal, redundancy, unpaid wages or entitlements, and "
        "employment contract questions."
    ),
    "consumer_rights": (
        "Buying goods or services: faulty products, refunds and replacements, "
        "Australian Consumer Law guarantees, and subscription traps."
    ),
    "family_law": (
        "Relationships and family: separation, parenting arrangements, and property settlement."
    ),
}

# Australian states and territories used for jurisdiction detection.
JURISDICTIONS: list[str] = [
    "New South Wales",
    "Victoria",
    "Queensland",
    "South Australia",
    "Western Australia",
    "Tasmania",
    "Australian Capital Territory",
    "Northern Territory",
]

# The exact string to use when no jurisdiction can be determined.
JURISDICTION_DEFAULT = "Australia — state not specified"
