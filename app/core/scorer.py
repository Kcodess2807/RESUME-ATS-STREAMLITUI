"""
Scorer Orchestrator Module
Coordinates all scoring calculations and returns the final scores dict.

📌 TEACHING NOTE — What does this file do?
    This is the SCORING ENGINE entry point — it takes all the processed
    resume data and produces the final 0-100 ATS score.

    Input:  processed resume data (sections, skills, keywords, grammar results...)
    Output: complete scores dict with overall score, 5 component scores,
            interpretation text, penalties, bonuses, and per-component messages

📌 TEACHING NOTE — Three-file scoring system:
    scorer.py          ← YOU ARE HERE (orchestrator + caching)
    scorer_calc.py     → pure number-crunching functions
    scorer_feedback.py → text/interpretation generation functions

    This split keeps calculation logic separate from presentation logic.
    If the scoring formula needs to change, only scorer_calc.py is touched.
    If feedback messages need to change, only scorer_feedback.py is touched.

📌 TEACHING NOTE — Score composition (100 total points):
    Formatting Score        → max 20 pts (calculated by scorer_calc.py)
    Keywords & Skills Score → max 25 pts
    Content Quality Score   → max 25 pts
    Skill Validation Score  → max 15 pts
    ATS Compatibility Score → max 15 pts
    Subtotal:                   100 pts
    ± Penalties/Bonuses     → applied AFTER (grammar, location, excellent skills)
    Final clamped to [0, 100]
"""

from typing import Dict, List, Optional, Tuple
import re
import streamlit as st
import hashlib

# Import calculation functions (pure math — no side effects)
from app.core.scorer_calc import (
    calculate_formatting_score,
    calculate_keywords_score,
    calculate_content_score,
    calculate_skill_validation_score,
    calculate_ats_compatibility_score,
    apply_penalties_and_bonuses
)

# Import feedback/interpretation generators (text output — no math)
from app.core.scorer_feedback import (
    generate_score_interpretation,
    generate_score_breakdown_messages,
    generate_strengths,
    generate_critical_issues,
    generate_improvements
)


def _compute_overall_score(
    text: str,
    sections: Dict[str, str],
    skills: List[str],
    keywords: List[str],
    action_verbs: List[str],
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    jd_keywords: Optional[List[str]] = None
) -> Dict:
    """
    Internal function — compute all scores and assemble the result dict.
    No caching here — that's handled by the public calculate_overall_score().

    📌 TEACHING NOTE — Scoring Pipeline:
        This function runs a 5-step pipeline:

        Step 1: Calculate each of 5 component scores independently
                (each reads only the data it needs — no interdependencies)

        Step 2: Sum components → base_score
                (raw total before any adjustments)

        Step 3: Apply penalties and bonuses → overall_score
                (grammar errors reduce score; excellent validation adds bonus)

        Step 4: Generate interpretation text
                ("Great! Your resume should perform well...")

        Step 5: Generate per-component messages
                ("Excellent structure" / "Needs more keywords" etc.)

        The pipeline is strictly sequential — each step feeds the next.

    📌 TEACHING NOTE — round(score, 1):
        Scores like 82.666... become 82.7 in the output dict.
        round(value, 1) rounds to 1 decimal place.
        We do this in the return statement — the calculations use full
        precision internally, rounding only happens in the final output.
        This avoids rounding errors accumulating across calculation steps.

    📌 TEACHING NOTE — base_score vs overall_score:
        base_score    = sum of all 5 component scores (raw total, ≤ 100)
        overall_score = base_score ± penalties ± bonuses (final, clamped to [0,100])

        Keeping them separate means we can show the user what the base was
        AND what was added/subtracted. Transparency builds trust in the score.

    Args:
        text: Full resume text
        sections: Dict of section names → section content
        skills: List of extracted skills
        keywords: List of extracted keywords
        action_verbs: List of detected action verbs
        skill_validation_results: From the skill validator
        grammar_results: From the grammar checker
        location_results: From the location detector
        jd_keywords: Optional JD keywords (for JD match bonus)

    Returns:
        Dict with all scores, messages, penalties, and bonuses — fully rounded
    """
    # ── Step 1: Calculate each component score independently ─────────────
    formatting_score        = calculate_formatting_score(sections, text)
    keywords_score          = calculate_keywords_score(keywords, skills, jd_keywords)
    content_score           = calculate_content_score(text, action_verbs, grammar_results)
    skill_validation_score  = calculate_skill_validation_score(skill_validation_results)
    ats_compatibility_score = calculate_ats_compatibility_score(text, location_results, sections)

    # ── Step 2: Sum all components for base score ─────────────────────────
    # Max possible: 20 + 25 + 25 + 15 + 15 = 100
    base_score = (
        formatting_score +
        keywords_score +
        content_score +
        skill_validation_score +
        ats_compatibility_score
    )

    # ── Step 3: Apply penalties (grammar, location) and bonuses (excellent validation) ──
    overall_score, penalties, bonuses = apply_penalties_and_bonuses(
        base_score, grammar_results, location_results, skill_validation_results
    )

    # ── Step 4: Generate overall interpretation text ──────────────────────
    overall_interpretation = generate_score_interpretation(overall_score)

    # ── Step 5: Generate per-component status messages ────────────────────
    component_messages = generate_score_breakdown_messages(
        formatting_score, keywords_score, content_score,
        skill_validation_score, ats_compatibility_score
    )

    # ── Assemble and return the full results dict (scores rounded to 1dp) ──
    return {
        'overall_score':           round(overall_score, 1),
        'overall_interpretation':  overall_interpretation,
        'formatting_score':        round(formatting_score, 1),
        'keywords_score':          round(keywords_score, 1),
        'content_score':           round(content_score, 1),
        'skill_validation_score':  round(skill_validation_score, 1),
        'ats_compatibility_score': round(ats_compatibility_score, 1),
        'component_messages':      component_messages,   # Dict of per-component strings
        'penalties':               penalties,             # Dict of {category: points}
        'bonuses':                 bonuses                # Dict of {category: points}
    }


def calculate_overall_score(
    text: str,
    sections: Dict[str, str],
    skills: List[str],
    keywords: List[str],
    action_verbs: List[str],
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    jd_keywords: Optional[List[str]] = None,
    use_cache: bool = True
) -> Dict:
    """
    Public entry point — calculate the overall score, using session state cache.

    📌 TEACHING NOTE — Why use session state cache here instead of @st.cache_data?
        The scoring function takes MANY arguments of different types:
        - dicts (sections, skill_validation_results, grammar_results...)
        - lists (skills, keywords, action_verbs...)

        @st.cache_data would need ALL of these to be hashable/serializable.
        Dicts with nested dicts and lists are complex to hash reliably.

        Instead, this function manually builds a cache key using:
        - SHA-256 hash of the text (stable, compact)
        - Python's hash() of sorted tuples of skills/keywords/jd_keywords

        This gives a custom, controlled cache key that's fast to compute.

    📌 TEACHING NOTE — Streamlit environment detection:
        try:
            from streamlit.runtime.state import SessionState
            in_streamlit = isinstance(st.session_state, SessionState)
        except Exception:
            in_streamlit = False

        st.session_state only works inside a running Streamlit app.
        If this code runs in a unit test or plain Python script,
        st.session_state will fail. The try/except detects this and
        sets in_streamlit = False so caching is gracefully skipped.

        This makes the function testable outside of Streamlit.

    📌 TEACHING NOTE — Cache key construction:
        text_hash    = SHA-256 of resume text, truncated to 16 chars (collision-safe shorthand)
        skills_key   = sorted tuple of skills (sorted = same order regardless of input order)
        keywords_key = sorted tuple of keywords
        jd_key       = sorted tuple of jd_keywords (or empty tuple if None)

        All combined: f'score_{text_hash}_{hash((skills_key, keywords_key, jd_key))}'

        Sorted tuples are used because ("Python", "AWS") and ("AWS", "Python")
        should produce the SAME cache key — order doesn't matter for scoring.
        Without sorting, ["Python", "AWS"] ≠ ["AWS", "Python"] as cache keys.

    📌 TEACHING NOTE — Manual FIFO eviction (max 20 entries):
        if len(st.session_state.score_cache) > 20:
            oldest_key = next(iter(st.session_state.score_cache))
            del st.session_state.score_cache[oldest_key]

        Dicts in Python 3.7+ maintain insertion order.
        next(iter(dict)) gives the FIRST (oldest) key.
        Deleting it keeps the cache from growing unboundedly.

        This is a manual FIFO (First In, First Out) eviction strategy.
        Simple but effective for a small cache. Real production systems
        use LRU (Least Recently Used) which is more sophisticated.

    📌 TEACHING NOTE — import json inside the function:
        The import statement is inside the cache block but json is never
        actually used! This is dead code — likely a leftover from an earlier
        version that used json for cache key serialization.
        ⚠️ This should be removed.

    Args:
        (same as _compute_overall_score, plus:)
        use_cache: Whether to use session-state caching (default True)

    Returns:
        Complete scores dict from _compute_overall_score()
    """
    # ── Detect if we're running inside a Streamlit app ────────────────────
    try:
        from streamlit.runtime.state import SessionState
        in_streamlit = isinstance(st.session_state, SessionState)
    except Exception:
        in_streamlit = False   # Running in tests or plain Python — skip caching

    if use_cache and in_streamlit:
        import json   # ⚠️ Dead import — 'json' is never used below. Should be removed.

        # ── Build cache key from all relevant inputs ──────────────────────
        # Truncate hash to 16 chars (still collision-resistant for small caches)
        text_hash    = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

        # Sort lists before converting to tuple — order-independent cache key
        skills_key   = tuple(sorted(skills))   if skills   else ()
        keywords_key = tuple(sorted(keywords)) if keywords else ()
        jd_key       = tuple(sorted(jd_keywords)) if jd_keywords else ()

        # Hash the combined tuple for a compact, stable cache key suffix
        cache_key = f'score_{text_hash}_{hash((skills_key, keywords_key, jd_key))}'

        # ── Initialize cache dict in session state if needed ──────────────
        if 'score_cache' not in st.session_state:
            st.session_state.score_cache = {}

        # ── Cache hit: return stored result immediately ───────────────────
        if cache_key in st.session_state.score_cache:
            return st.session_state.score_cache[cache_key]

        # ── Cache miss: compute and store ─────────────────────────────────
        result = _compute_overall_score(
            text, sections, skills, keywords, action_verbs,
            skill_validation_results, grammar_results, location_results, jd_keywords
        )
        st.session_state.score_cache[cache_key] = result

        # ── FIFO eviction: keep max 20 entries ────────────────────────────
        if len(st.session_state.score_cache) > 20:
            # next(iter(dict)) = first (oldest) key in insertion order
            oldest_key = next(iter(st.session_state.score_cache))
            del st.session_state.score_cache[oldest_key]

        return result

    else:
        # Not in Streamlit OR caching disabled — compute directly
        return _compute_overall_score(
            text, sections, skills, keywords, action_verbs,
            skill_validation_results, grammar_results, location_results, jd_keywords
        )