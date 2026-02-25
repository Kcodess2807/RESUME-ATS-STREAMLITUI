"""
Recommendation Generator — Orchestrator Module
Combines all recommendation sources, prioritizes, and formats them.

📌 TEACHING NOTE — What does this file do?
    This is the ORCHESTRATOR for the recommendation system.
    It answers the question: "Given all the analysis results, what should
    the candidate prioritize to improve their resume?"

    Four separate sub-generators each focus on one domain:
        generate_skill_recommendations()    → from recommendation_generators1.py
        generate_grammar_recommendations()  → from recommendation_generators1.py
        generate_location_recommendations() → from recommendation_generators2.py
        generate_keyword_recommendations()  → from recommendation_generators2.py
        generate_formatting_recommendations() → from recommendation_generators2.py

    This file:
    1. Calls all five generators (collect)
    2. Sorts by priority then impact score (prioritize)
    3. Groups by priority level (organize)
    4. Calculates estimated improvement (summarize)
    5. Provides formatting helpers for the UI (present)

📌 TEACHING NOTE — Data Classes and Enums:
    The Recommendation dataclass and Priority enum (defined in generators1.py)
    are the SHARED DATA TYPES used by all files in this system.
    This file imports and uses them but doesn't define them.
    This is a common pattern: define shared types in one place, import everywhere.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import generators from the two sub-files
from app.core.recommendation_generators1 import (
    generate_skill_recommendations,
    generate_grammar_recommendations,
    Priority,           # The Enum class
    Recommendation      # The dataclass
)
from app.core.recommendation_generators2 import (
    generate_location_recommendations,
    generate_keyword_recommendations,
    generate_formatting_recommendations
)


def prioritize_recommendations(recommendations: List[Recommendation]) -> List[Recommendation]:
    """
    Sort recommendations by priority level, then by impact score within each level.

    📌 TEACHING NOTE — sorted() with a lambda key function:
        sorted(recommendations, key=lambda r: (priority_order[r.priority], -r.impact_score))

        The key function returns a TUPLE for each item.
        Python sorts tuples element by element:
        1. First sort by priority_order[r.priority] (0=critical, 1=high, 2=medium, 3=low)
        2. Within same priority, sort by -r.impact_score (negative = highest impact first)

        Why negative? sorted() always sorts ASCENDING.
        For impact score, we want DESCENDING (highest impact first).
        Negating the value flips ascending to effectively descending.

        Example:
        (0, -8.0) < (0, -6.0)  → 8.0 impact comes before 6.0 impact ✓
        (0, ...) < (1, ...)     → CRITICAL always before HIGH ✓

    📌 TEACHING NOTE — priority_order dict maps Enum → int:
        {Priority.CRITICAL: 0, Priority.HIGH: 1, ...}
        Enums can't be sorted directly (no natural ordering).
        We map each to an integer to give them a sortable order.
        Lower integer = higher priority.

    Args:
        recommendations: Unsorted list of Recommendation objects

    Returns:
        Sorted list: critical first, then high/medium/low; within each level, highest impact first
    """
    priority_order = {
        Priority.CRITICAL: 0,
        Priority.HIGH:     1,
        Priority.MEDIUM:   2,
        Priority.LOW:      3
    }
    sorted_recommendations = sorted(
        recommendations,
        key=lambda r: (priority_order[r.priority], -r.impact_score)
        # Tuple key: sort by priority first, then by negative impact (highest first)
    )
    return sorted_recommendations


def generate_all_recommendations(
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    score_results: Dict,
    sections: Dict[str, str],
    keyword_analysis: Optional[Dict] = None,
    resume_keywords: Optional[List[str]] = None
) -> Dict:
    """
    Main entry point — collect all recommendations and return a structured summary.

    📌 TEACHING NOTE — Aggregator Pattern:
        This function is an AGGREGATOR — it calls all 5 generator functions
        and combines their output into one unified result.

        Aggregators don't do work themselves — they delegate.
        This separation means:
        - Each generator can be tested independently
        - Adding a new generator = one new .extend() call here
        - Removing a generator = delete one .extend() call

    📌 TEACHING NOTE — Estimating improvement potential:
        estimated_improvement = sum(r.impact_score for r in prioritized)
        estimated_improvement = min(estimated_improvement, 30.0)

        Each recommendation has an impact_score (how much it could improve the total).
        Summing them estimates total possible improvement.

        We cap at 30.0 because:
        - Impact scores might overlap (fixing grammar also helps ATS compatibility)
        - Over-promising improvement looks unprofessional
        - 30 points is already a significant improvement

        min(value, 30.0) clamps the estimate to a realistic maximum.

    📌 TEACHING NOTE — Returning grouped recommendations:
        The result dict includes BOTH all_recommendations (flat sorted list)
        AND separate lists by priority (critical, high, medium, low).

        Why duplicate? Different parts of the UI use different views:
        - "Show top 3 critical issues" → use critical_recommendations
        - "Show all recommendations in order" → use all_recommendations
        Pre-grouping avoids filtering in the UI layer.

    Args:
        skill_validation_results: From skill validator
        grammar_results: From grammar checker
        location_results: From location detector
        score_results: Full scores dict (for formatting recommendations)
        sections: Resume sections dict (for missing section detection)
        keyword_analysis: JD comparison results (optional, None if no JD provided)
        resume_keywords: All resume keywords (for keyword density check)

    Returns:
        Dict with prioritized recommendations, grouped lists, counts, and improvement estimate
    """
    all_recommendations = []

    # ── Collect from all generators ───────────────────────────────────────
    all_recommendations.extend(generate_skill_recommendations(skill_validation_results))
    all_recommendations.extend(generate_grammar_recommendations(grammar_results))
    all_recommendations.extend(generate_location_recommendations(location_results))
    all_recommendations.extend(generate_keyword_recommendations(keyword_analysis, resume_keywords))
    all_recommendations.extend(generate_formatting_recommendations(score_results, sections))

    # ── Sort by priority and impact ───────────────────────────────────────
    prioritized = prioritize_recommendations(all_recommendations)

    # ── Group by priority level ───────────────────────────────────────────
    critical = [r for r in prioritized if r.priority == Priority.CRITICAL]
    high     = [r for r in prioritized if r.priority == Priority.HIGH]
    medium   = [r for r in prioritized if r.priority == Priority.MEDIUM]
    low      = [r for r in prioritized if r.priority == Priority.LOW]

    # ── Estimate total improvement potential ──────────────────────────────
    # Sum impact scores, but cap at 30 (realistic maximum improvement)
    estimated_improvement = sum(r.impact_score for r in prioritized)
    estimated_improvement = min(estimated_improvement, 30.0)

    return {
        'all_recommendations':      prioritized,
        'critical_recommendations': critical,
        'high_recommendations':     high,
        'medium_recommendations':   medium,
        'low_recommendations':      low,
        'total_count':              len(prioritized),
        'estimated_improvement':    estimated_improvement
    }


def format_recommendation_for_display(recommendation: Recommendation) -> Dict:
    """
    Convert a Recommendation object into a plain dict for UI display.

    📌 TEACHING NOTE — Object to dict conversion (serialization):
        The Recommendation is a dataclass OBJECT with typed attributes.
        But Streamlit UI components (and JSON/databases) work with DICTS.

        This function converts: Recommendation object → display-ready dict

        The dict adds UI-specific fields that the dataclass doesn't have:
        - priority_icon: emoji for the risk level (🔴, 🟠, etc.)
        - priority_label: human-readable label ("Critical", "High Priority")
        - priority_value: lowercase string ('critical', 'high', etc.)

        These are VIEW CONCERNS (how to display) — they don't belong in
        the Recommendation dataclass (which is a DATA concern).
        Keeping them separate is good MVC/separation of concerns design.

    📌 TEACHING NOTE — recommendation.priority.value:
        Priority is an Enum: Priority.CRITICAL, Priority.HIGH etc.
        .value gives the string: 'critical', 'high', 'medium', 'low'
        This is used as the 'priority_value' in the returned dict.

    Args:
        recommendation: A Recommendation dataclass instance

    Returns:
        Dict with all recommendation fields plus UI-specific display fields
    """
    # Map Enum values to display elements
    priority_colors = {
        Priority.CRITICAL: '🔴',
        Priority.HIGH:     '🟠',
        Priority.MEDIUM:   '🟡',
        Priority.LOW:      '🟢'
    }
    priority_labels = {
        Priority.CRITICAL: 'Critical',
        Priority.HIGH:     'High Priority',
        Priority.MEDIUM:   'Medium Priority',
        Priority.LOW:      'Low Priority'
    }

    return {
        'title':          recommendation.title,
        'description':    recommendation.description,
        'priority_icon':  priority_colors[recommendation.priority],   # 🔴
        'priority_label': priority_labels[recommendation.priority],   # "Critical"
        'priority_value': recommendation.priority.value,              # 'critical'
        'impact_score':   recommendation.impact_score,
        'category':       recommendation.category,
        'action_items':   recommendation.action_items
    }


def format_all_recommendations_for_display(recommendations_result: Dict) -> List[Dict]:
    """
    Convert all recommendations to display-ready dicts.

    📌 TEACHING NOTE — List transformation with a helper function:
        This function applies format_recommendation_for_display()
        to every recommendation in the list.

        Equivalent to:
            [format_recommendation_for_display(rec) for rec in all_recs]

        The function form is cleaner because:
        - It handles the .get() with default
        - The helper function is reusable elsewhere
        - The intent is clear: "format all recommendations for display"

    Args:
        recommendations_result: Dict returned by generate_all_recommendations()

    Returns:
        List of display-ready dicts
    """
    formatted = []
    for rec in recommendations_result.get('all_recommendations', []):
        formatted.append(format_recommendation_for_display(rec))
    return formatted


def generate_action_items_list(recommendations_result: Dict) -> List[Dict]:
    """
    Flatten all recommendations into a unified list of individual action items.

    📌 TEACHING NOTE — Nested loop to flatten:
        Each Recommendation has a LIST of action_items strings.
        This function "flattens" the two-level structure
        (list of recommendations, each with a list of items)
        into a single flat list.

        for rec in recommendations:          ← outer loop
            for item in rec.action_items:    ← inner loop
                flat_list.append(...)

        Each item in the output is enriched with its parent recommendation's
        priority, category, and title — so the flat list items are self-contained.

        This flat structure is useful for the checklist view: you want
        one consolidated list, not grouped by recommendation.

    📌 TEACHING NOTE — rec.priority.value:
        We convert the Enum to its string value for the output dict,
        because dicts are often serialized to JSON — Enum objects aren't
        JSON-serializable, but strings are.

    Args:
        recommendations_result: Dict from generate_all_recommendations()

    Returns:
        Flat list of action item dicts, each with item text, priority, category
    """
    action_items = []
    for rec in recommendations_result.get('all_recommendations', []):
        for item in rec.action_items:
            action_items.append({
                'item':         item,
                'priority':     rec.priority.value,   # Enum → string for JSON safety
                'category':     rec.category,
                'parent_title': rec.title
            })
    return action_items


def get_recommendation_summary(recommendations_result: Dict) -> str:
    """
    Generate a single-line summary string of the overall recommendation status.

    📌 TEACHING NOTE — Tiered summary messages:
        The function returns ONE of four possible messages based on the state:

        no recommendations    → "✅ Excellent! No major recommendations..."
        has critical issues   → "🔴 Found N recommendation(s) including X critical..."
        has high priority     → "🟠 Found N recommendation(s) including X high-priority..."
        only medium/low       → "🟡 Found N recommendation(s) for improvement..."

        The order of if/elif checks matters:
        - Check for zero total first (most positive case)
        - Check for critical next (most urgent case)
        - Check for high next
        - Default to medium/low (catch-all)

        This produces the MOST URGENT relevant message.
        If there are both critical and high issues, the critical message is shown.

    📌 TEACHING NOTE — f-string with :.0f:
        f'up to {improvement:.0f} points'
        :.0f = format as float with 0 decimal places.
        30.3 → "30"  (rounded to nearest integer)

    Args:
        recommendations_result: Dict from generate_all_recommendations()

    Returns:
        Single human-readable summary string with emoji
    """
    total       = recommendations_result.get('total_count', 0)
    critical    = len(recommendations_result.get('critical_recommendations', []))
    high        = len(recommendations_result.get('high_recommendations', []))
    improvement = recommendations_result.get('estimated_improvement', 0.0)

    if total == 0:
        return '✅ Excellent! No major recommendations. Your resume is well-optimized.'

    if critical > 0:
        return (
            f'🔴 Found {total} recommendation(s) including {critical} critical issue(s). '
            f'Addressing these could improve your score by up to {improvement:.0f} points.'
        )
    elif high > 0:
        return (
            f'🟠 Found {total} recommendation(s) including {high} high-priority item(s). '
            f'Addressing these could improve your score by up to {improvement:.0f} points.'
        )
    else:
        return (
            f'🟡 Found {total} recommendation(s) for improvement. '
            f'Addressing these could improve your score by up to {improvement:.0f} points.'
        )