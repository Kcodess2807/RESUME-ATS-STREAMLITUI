"""
Recommendation Generators 1 — Shared Types + Skill & Grammar Recommendations
Defines the core data structures (Priority, Recommendation) and the first
two generator functions.

📌 TEACHING NOTE — Why are Priority and Recommendation defined HERE?
    recommendation_generators1.py is imported by:
    - recommendation_generators2.py  (needs Priority + Recommendation)
    - recommendation_generator.py    (needs Priority + Recommendation)

    Defining the shared types in generators1.py and importing them
    everywhere else means there's ONE source of truth.
    If you need to add a new priority level or a new field to Recommendation,
    you change it in ONE place and all files get the update automatically.

    This is the DRY principle for type definitions.

📌 TEACHING NOTE — Two Python features introduced here:
    1. Enums  (class Priority)    → fixed set of named constants
    2. Dataclasses (@dataclass)   → simple data container classes

    Both are standard library features — no extra installs needed.

⚠️ TEACHING NOTE — Duplicate imports flagged:
    The imports at the top (Dict, List, Optional, dataclass, Enum) are
    repeated again in the middle of the file. This is a copy-paste error
    that should be cleaned up. All imports should appear ONCE at the top.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


# ── Priority Enum ─────────────────────────────────────────────────────────────

class Priority(Enum):
    """
    Represents the urgency level of a recommendation.

    📌 TEACHING NOTE — What is an Enum?
        An Enum (Enumeration) is a set of named constants.
        Instead of using raw strings like 'critical', 'high', 'medium', 'low'
        (which can be mistyped anywhere in the code), we use:
            Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW

        Benefits over raw strings:
        1. Typo-proof: Priority.CRTIICAL would raise AttributeError immediately
           vs 'crtiical' silently never matching anything
        2. Autocomplete: IDEs suggest valid values
        3. Comparison: Priority.CRITICAL == Priority.CRITICAL is always reliable
        4. Iterable: you can iterate all Priority values: list(Priority)

    📌 TEACHING NOTE — .value attribute:
        Priority.CRITICAL.value → 'critical'
        The .value gives the underlying string.
        Used when you need the string form (e.g., for JSON output, dict keys).

    📌 TEACHING NOTE — Enum vs constants module:
        Alternative: a module with PRIORITY_CRITICAL = 'critical'
        Enum is better because it groups related constants together
        and provides type safety — you can't pass a random string where
        Priority is expected if your code uses type hints properly.
    """
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"


# ── Recommendation Dataclass ──────────────────────────────────────────────────

@dataclass
class Recommendation:
    """
    A single recommendation with all fields needed for display and prioritization.

    📌 TEACHING NOTE — What is a dataclass?
        @dataclass is a decorator that auto-generates boilerplate for a class
        meant to hold data. Without @dataclass, you'd write:

            class Recommendation:
                def __init__(self, title, description, priority, impact_score, category, action_items):
                    self.title        = title
                    self.description  = description
                    self.priority     = priority
                    self.impact_score = impact_score
                    self.category     = category
                    self.action_items = action_items

        With @dataclass:
            @dataclass
            class Recommendation:
                title:        str
                description:  str
                priority:     Priority
                impact_score: float
                category:     str
                action_items: List[str]

        @dataclass also generates __repr__ (for print()) and __eq__ (for == comparison).

    📌 TEACHING NOTE — Field types as documentation:
        priority: Priority    → must be a Priority enum value
        impact_score: float   → a number representing potential improvement
        action_items: List[str] → list of specific things to do

        These type annotations don't enforce types at runtime in Python,
        but they serve as documentation AND enable type checkers (mypy, pyright)
        to catch errors at development time.

    📌 TEACHING NOTE — Recommendation vs dict:
        We could use a plain dict {'title': ..., 'priority': ...} instead.
        Dataclass advantages:
        - Attribute access: rec.title (cleaner) vs rec['title'] (noisier)
        - Type hints per field
        - Auto-generated __repr__ for debugging
        - Type checking tools can verify correct usage
    """
    title:        str           # Short name: "Fix Critical Grammar Errors"
    description:  str           # Full explanation for the user
    priority:     Priority      # Priority enum value
    impact_score: float         # Estimated score improvement (e.g., 8.0 points)
    category:     str           # 'grammar', 'skills', 'location', 'keywords', 'formatting'
    action_items: List[str]     # Specific steps the candidate should take


# ── Skill Recommendations Generator ──────────────────────────────────────────

def generate_skill_recommendations(skill_validation_results: Dict) -> List[Recommendation]:
    """
    Generate recommendations for unvalidated skills.

    📌 TEACHING NOTE — Tiered priority based on validation percentage:
        validation_percentage = (validated_skills / total_skills)
        e.g., 3 of 10 skills validated → 0.30 → CRITICAL

        Thresholds:
        < 0.4  (less than 40% validated) → CRITICAL, impact 8.0
        < 0.6  (40-59% validated)        → HIGH,     impact 6.0
        < 0.8  (60-79% validated)        → MEDIUM,   impact 4.0
        ≥ 0.8  (80%+ validated)          → LOW,      impact 2.0

        Even if most skills are validated, a few unvalidated ones are still
        worth mentioning — hence LOW (not skipped entirely).

        Early return if no unvalidated skills:
        if not unvalidated_skills: return recommendations  (= return [])
        This guard prevents adding a recommendation when there's no issue.

    📌 TEACHING NOTE — Building action items for up to 5 unvalidated skills:
        for skill in unvalidated_skills[:5]:
            action_items.append(f"Add a project... '{skill}'")
        if len(unvalidated_skills) > 5:
            action_items.append(f'... and {len(...) - 5} more')

        We show max 5 specific skills (avoids overwhelming the user).
        Then a summary "...and N more" if there are additional ones.
        This pattern balances specificity vs brevity.

    📌 TEACHING NOTE — Single Recommendation object created:
        This function always creates AT MOST ONE Recommendation object.
        All unvalidated skills are grouped into one recommendation.
        (Not one recommendation per skill — that would be overwhelming)

    Args:
        skill_validation_results: Dict with 'unvalidated_skills' and 'validation_percentage'

    Returns:
        List with 0 or 1 Recommendation objects
    """
    recommendations     = []
    unvalidated_skills  = skill_validation_results.get('unvalidated_skills', [])
    validation_percentage = skill_validation_results.get('validation_percentage', 0.0)

    # Guard: no unvalidated skills → no recommendation needed
    if not unvalidated_skills:
        return recommendations

    # ── Determine priority and impact based on validation rate ────────────
    if validation_percentage < 0.4:
        priority = Priority.CRITICAL
        impact   = 8.0
    elif validation_percentage < 0.6:
        priority = Priority.HIGH
        impact   = 6.0
    elif validation_percentage < 0.8:
        priority = Priority.MEDIUM
        impact   = 4.0
    else:
        priority = Priority.LOW
        impact   = 2.0

    # ── Build specific action items (max 5 + overflow summary) ───────────
    action_items = []
    for skill in unvalidated_skills[:5]:
        action_items.append(
            f"Add a project or experience demonstrating '{skill}', or remove it from skills"
        )
    if len(unvalidated_skills) > 5:
        action_items.append(f'... and {len(unvalidated_skills) - 5} more unvalidated skill(s)')

    # ── Create and return the single Recommendation ───────────────────────
    recommendations.append(Recommendation(
        title       = 'Validate Your Listed Skills',
        description = (
            f"{len(unvalidated_skills)} skill(s) are not demonstrated in your projects or experience. "
            f"ATS systems and recruiters look for evidence that you've actually used the skills you claim."
        ),
        priority     = priority,
        impact_score = impact,
        category     = 'skill_validation',
        action_items = action_items
    ))
    return recommendations


# ── Grammar Recommendations Generator ────────────────────────────────────────

def generate_grammar_recommendations(grammar_results: Dict) -> List[Recommendation]:
    """
    Generate recommendations for grammar and spelling errors.

    📌 TEACHING NOTE — Up to THREE separate Recommendation objects:
        Unlike generate_skill_recommendations() which always creates at most ONE,
        this function can create up to THREE — one per error severity level:

        1. Critical errors → Recommendation (Priority.CRITICAL)
        2. Moderate errors → Recommendation (Priority.HIGH)
        3. Minor errors    → Recommendation (Priority.LOW) — only if ≥ 3 errors

        Each is independent — a resume could have recommendations for all three,
        or just one, or none (if total_errors == 0).

    📌 TEACHING NOTE — min() to cap impact score:
        impact_score = min(10.0, len(critical_errors) * 2.0)

        1 critical error → min(10.0, 2.0)  = 2.0
        3 critical errors → min(10.0, 6.0)  = 6.0
        7 critical errors → min(10.0, 14.0) = 10.0  (capped!)

        Without min(), 10 critical errors would give impact_score=20 —
        unrealistically high. The cap keeps estimates credible.

    📌 TEACHING NOTE — Threshold for minor errors (>= 3):
        if minor_errors and len(minor_errors) >= 3:
        Minor style issues (1-2 occurrences) aren't worth a recommendation —
        they're too trivial. Only worth mentioning if there are 3+ instances,
        suggesting a consistent style problem.

    📌 TEACHING NOTE — suggestion_text conditional:
        suggestion_text = f" → '{suggestions[0]}'" if suggestions else ''
        "Fix 'experiance' → 'experience': Possible spelling mistake"
        vs just:
        "Fix 'grammarr': Possible spelling mistake" (no suggestion available)

    Args:
        grammar_results: Dict with critical_errors, moderate_errors, minor_errors lists

    Returns:
        List of 0-3 Recommendation objects, one per error severity level
    """
    recommendations = []
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors    = grammar_results.get('minor_errors', [])
    penalty         = grammar_results.get('penalty_applied', 0.0)

    total_errors = len(critical_errors) + len(moderate_errors) + len(minor_errors)

    # Guard: no errors at all → return empty list
    if total_errors == 0:
        return recommendations

    # ── Critical grammar errors → CRITICAL priority recommendation ────────
    if critical_errors:
        action_items = []
        for error in critical_errors[:5]:   # Max 5 specific examples
            error_text      = error.get('error_text', 'unknown')
            suggestions     = error.get('suggestions', [])
            suggestion_text = f" → '{suggestions[0]}'" if suggestions else ''
            action_items.append(
                f"Fix '{error_text}'{suggestion_text}: {error.get('message', '')}"
            )
        if len(critical_errors) > 5:
            action_items.append(f'... and {len(critical_errors) - 5} more critical error(s)')

        recommendations.append(Recommendation(
            title       = 'Fix Critical Spelling/Grammar Errors',
            description = (
                f'{len(critical_errors)} critical error(s) found. These are spelling mistakes or '
                f'major grammar issues that will make your resume look unprofessional.'
            ),
            priority     = Priority.CRITICAL,
            impact_score = min(10.0, len(critical_errors) * 2.0),  # Cap at 10
            category     = 'grammar',
            action_items = action_items
        ))

    # ── Moderate errors → HIGH priority recommendation ─────────────────────
    if moderate_errors:
        action_items = []
        for error in moderate_errors[:3]:   # Max 3 examples for moderate
            error_text      = error.get('error_text', 'unknown')
            suggestions     = error.get('suggestions', [])
            suggestion_text = f" → '{suggestions[0]}'" if suggestions else ''
            action_items.append(
                f"Fix '{error_text}'{suggestion_text}: {error.get('message', '')}"
            )
        if len(moderate_errors) > 3:
            action_items.append(f'... and {len(moderate_errors) - 3} more moderate error(s)')

        recommendations.append(Recommendation(
            title       = 'Address Punctuation and Capitalization Issues',
            description = (
                f'{len(moderate_errors)} moderate error(s) found. '
                f'These are punctuation or capitalization issues that should be corrected.'
            ),
            priority     = Priority.HIGH,
            impact_score = min(6.0, len(moderate_errors) * 1.0),  # Cap at 6
            category     = 'grammar',
            action_items = action_items
        ))

    # ── Minor errors → LOW priority recommendation (only if 3+) ──────────
    if minor_errors and len(minor_errors) >= 3:
        action_items = [
            f'Review {len(minor_errors)} style suggestion(s) for improved readability',
            'Consider using consistent formatting throughout'
        ]
        recommendations.append(Recommendation(
            title       = 'Consider Style Improvements',
            description = (
                f'{len(minor_errors)} minor style suggestion(s) found. '
                f'These are optional improvements for better readability.'
            ),
            priority     = Priority.LOW,
            impact_score = 1.0,   # Fixed low impact — style is optional
            category     = 'grammar',
            action_items = action_items
        ))

    return recommendations