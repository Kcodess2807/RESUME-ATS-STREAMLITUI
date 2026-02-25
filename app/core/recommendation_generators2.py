"""
Recommendation Generators 2 — Location, Keyword, and Formatting Recommendations
Third and final group of recommendation generator functions.

📌 TEACHING NOTE — Why is this a separate file from generators1.py?
    generators1.py defines the shared types (Priority, Recommendation)
    AND the first two generators (skills, grammar).

    This file imports those types and adds three more generators:
    - generate_location_recommendations()   → privacy issues
    - generate_keyword_recommendations()    → JD match gaps
    - generate_formatting_recommendations() → resume structure

    The split keeps each file under 200 lines — readable and focused.
    A developer fixing location recommendations only needs to look here.

📌 TEACHING NOTE — Import chain:
    generators1.py    defines Priority, Recommendation
    generators2.py    imports from generators1.py
    generator.py      imports from BOTH generators1.py and generators2.py

    This is a linear dependency chain — no circular imports.
    Circular imports (A imports B, B imports A) cause errors in Python.
    Always design import chains to flow in ONE direction.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import the shared data types from generators1.py
from app.core.recommendation_generators1 import Priority, Recommendation


def generate_location_recommendations(location_results: Dict) -> List[Recommendation]:
    """
    Generate recommendations for location/privacy issues.

    📌 TEACHING NOTE — Early return for no issues:
        if privacy_risk == 'none' or not detected_locations:
            return recommendations  (= return [])

        If there are no privacy problems, there's nothing to recommend.
        This guard prevents adding empty or meaningless recommendations.

    📌 TEACHING NOTE — Conditional action items build up:
        We start with an empty action_items list, then add items conditionally:
        - If addresses found → add "Remove address: '...'" for each
        - If ZIP codes found → add "Remove zip code: '...'" for each
        - Always add → "Keep only 'City, State' in your contact header"

        This produces specific, actionable items tailored to what was found.
        A resume with only ZIP codes gets different items than one with addresses.

    📌 TEACHING NOTE — Three privacy_risk levels → three description strings:
        'high'   → addresses/zips found   → CRITICAL priority, impact 5.0
        'medium' → many location mentions → HIGH priority,     impact 3.0
        'low'    → minor issues           → MEDIUM priority,   impact 2.0

        The description explains WHY the level was assigned.
        The priority and impact_score are set based on severity — same
        tiered approach as skill and grammar recommendations.

    Args:
        location_results: Dict from detect_location_info() in detector.py

    Returns:
        List with 0 or 1 Recommendation objects
    """
    recommendations    = []
    detected_locations = location_results.get('detected_locations', [])
    privacy_risk       = location_results.get('privacy_risk', 'none')
    penalty            = location_results.get('penalty_applied', 0.0)

    # Guard: no privacy issues → no recommendation
    if privacy_risk == 'none' or not detected_locations:
        return recommendations

    # Separate different location types for specific action items
    addresses       = [loc for loc in detected_locations if loc.get('type') == 'address']
    zip_codes       = [loc for loc in detected_locations if loc.get('type') == 'zip']
    other_locations = [loc for loc in detected_locations if loc.get('type') not in ['address', 'zip']]

    # ── Build specific action items ───────────────────────────────────────
    action_items = []
    if addresses:
        for addr in addresses[:2]:   # Show max 2 address examples
            action_items.append(f"Remove full address: '{addr.get('text', '')}'")
    if zip_codes:
        for zip_code in zip_codes[:2]:   # Show max 2 ZIP examples
            action_items.append(f"Remove zip code: '{zip_code.get('text', '')}'")

    # This action item is always relevant if any location issue exists
    action_items.append("Keep only 'City, State' in your contact header")

    # ── Set priority, impact, and description based on risk level ─────────
    if privacy_risk == 'high':
        priority    = Priority.CRITICAL
        impact      = 5.0
        description = (
            'Your resume contains detailed location information that poses a privacy risk. '
            'Full addresses and zip codes are unnecessary and can be used to identify your location.'
        )
    elif privacy_risk == 'medium':
        priority    = Priority.HIGH
        impact      = 3.0
        description = (
            "Your resume contains multiple location mentions. Consider simplifying to just "
            "'City, State' in your contact header."
        )
    else:   # 'low'
        priority    = Priority.MEDIUM
        impact      = 2.0
        description = (
            'Minor location information detected. Consider reviewing for unnecessary location details.'
        )

    recommendations.append(Recommendation(
        title        = 'Protect Your Location Privacy',
        description  = description,
        priority     = priority,
        impact_score = impact,
        category     = 'location',
        action_items = action_items
    ))
    return recommendations


def generate_keyword_recommendations(
    keyword_analysis: Optional[Dict] = None,
    resume_keywords: Optional[List[str]] = None
) -> List[Recommendation]:
    """
    Generate recommendations for keyword matching — both JD-specific and general.

    📌 TEACHING NOTE — Two operating modes based on input:
        Mode 1: JD provided (keyword_analysis is not None)
            - Compare resume keywords against JD keywords
            - Show missing keywords and skills gap
            - Priority depends on current match_percentage

        Mode 2: No JD provided (keyword_analysis is None)
            - Fall back to checking general keyword density
            - If resume has < 10 keywords, suggest adding more
            - No specific "missing" keywords to show

        The elif at the bottom handles Mode 2:
        elif resume_keywords is not None:
            if len(resume_keywords) < 10: ...

        This two-mode design means the function is useful both when the
        user provides a JD (specific gaps) and when they don't (general advice).

    📌 TEACHING NOTE — Two separate Recommendations for JD mode:
        1. Missing Keywords recommendation (if any missing)
        2. Skills Gap recommendation (if any gap)

        These are separate because they require different actions:
        - Missing keywords → "Add the word to your resume in relevant sections"
        - Skills gap → "Consider adding the skill if you have it" (softer language)

        Combining them would mix two different types of advice in one recommendation.

    📌 TEACHING NOTE — Match percentage determines missing keyword priority:
        match_percentage < 40  → CRITICAL, impact 8.0
        match_percentage < 60  → HIGH,     impact 6.0
        match_percentage ≥ 60  → MEDIUM,   impact 4.0

        If your resume only matches 30% of the JD keywords, that's critical —
        ATS will likely filter you out before a human ever reads the resume.
        At 70% match, adding a few keywords is still worth doing but not urgent.

    Args:
        keyword_analysis: JD comparison results dict (None if no JD provided)
        resume_keywords: All keywords from resume (used for density check if no JD)

    Returns:
        List of 0-2 Recommendation objects
    """
    recommendations = []

    # ── Mode 1: JD comparison available ──────────────────────────────────
    if keyword_analysis:
        missing_keywords  = keyword_analysis.get('missing_keywords', [])
        skills_gap        = keyword_analysis.get('skills_gap', [])
        match_percentage  = keyword_analysis.get('match_percentage', 0.0)

        # Missing keywords recommendation
        if missing_keywords:
            # Priority based on how bad the current match is
            if match_percentage < 40:
                priority = Priority.CRITICAL
                impact   = 8.0
            elif match_percentage < 60:
                priority = Priority.HIGH
                impact   = 6.0
            else:
                priority = Priority.MEDIUM
                impact   = 4.0

            action_items = []
            for keyword in missing_keywords[:7]:   # Max 7 specific keywords
                action_items.append(f"Add '{keyword}' to your resume in a relevant section")
            if len(missing_keywords) > 7:
                action_items.append(f'... and {len(missing_keywords) - 7} more missing keyword(s)')

            recommendations.append(Recommendation(
                title        = 'Add Missing Job Description Keywords',
                description  = (
                    f'{len(missing_keywords)} keyword(s) from the job description are missing from '
                    f'your resume. Your current match is {match_percentage:.0f}%.'
                ),
                priority     = priority,
                impact_score = impact,
                category     = 'keywords',
                action_items = action_items
            ))

        # Skills gap recommendation (separate from keyword recommendation)
        if skills_gap:
            action_items = []
            for skill in skills_gap[:5]:   # Max 5 skills
                action_items.append(f"Consider adding '{skill}' if you have this skill")
            if len(skills_gap) > 5:
                action_items.append(f'... and {len(skills_gap) - 5} more skill(s) mentioned in the job')

            recommendations.append(Recommendation(
                title        = 'Address Skills Gap',
                description  = (
                    f'The job description mentions {len(skills_gap)} skill(s) not found in your resume. '
                    f'Add these skills if you have them, or consider gaining them.'
                ),
                priority     = Priority.HIGH,
                impact_score = 5.0,   # Fixed impact — skills gap is always moderately important
                category     = 'keywords',
                action_items = action_items
            ))

    # ── Mode 2: No JD — check general keyword density ────────────────────
    elif resume_keywords is not None:
        if len(resume_keywords) < 10:
            recommendations.append(Recommendation(
                title        = 'Increase Keyword Density',
                description  = (
                    f'Your resume contains only {len(resume_keywords)} keywords. '
                    f'Adding more relevant keywords will improve ATS matching.'
                ),
                priority     = Priority.MEDIUM,
                impact_score = 4.0,
                category     = 'keywords',
                action_items = [
                    "Add more technical skills and tools you've used",
                    'Include industry-specific terminology',
                    'Mention relevant certifications and methodologies'
                ]
            ))

    return recommendations


def generate_formatting_recommendations(
    score_results: Dict,
    sections: Dict[str, str]
) -> List[Recommendation]:
    """
    Generate recommendations for missing sections and poor formatting.

    📌 TEACHING NOTE — Two types of section issues:
        core_missing    → essential sections (experience, education, skills)
        optional_missing → nice-to-have sections (summary, projects)

        Core missing → CRITICAL (ATS systems expect these sections)
        Optional missing + low formatting score → LOW (beneficial but not required)

        By separating them, we avoid over-alarming candidates who simply
        don't have a projects section (that's fine for many resumes).

    📌 TEACHING NOTE — section_recommendations dict as a lookup table:
        section_recommendations = {
            'experience': "Add a clear 'Experience' section",
            'education':  "Add an 'Education' section",
            ...
        }
        for section_name, recommendation in section_recommendations.items():
            if not sections.get(section_name) or len < 20:
                missing_sections.append(...)

        Iterating a dict to build another list is cleaner than:
            if not sections.get('experience'): missing.append(...)
            if not sections.get('education'): missing.append(...)
            ...

        Adding a new section = one new dict entry, not a new if-block.

    📌 TEACHING NOTE — len < 20 check for "exists but is too short":
        A section might exist but have less than 20 characters — perhaps
        just the header line was matched and no real content was captured.
        We treat "section exists but is nearly empty" the same as "section missing."

    📌 TEACHING NOTE — Formatting score threshold for structure recommendation:
        if formatting_score < 12:
            add HIGH priority "Improve Resume Structure" recommendation

        12/20 = 60% — below this, the structure is poor enough to warrant
        explicit recommendations about bullet points and section headers.
        Above 12, structure is acceptable and this recommendation is skipped.

    Args:
        score_results: Scores dict from the main analysis pipeline
        sections: Dict of section names → section text content

    Returns:
        List of 0-3 Recommendation objects
    """
    recommendations = []
    formatting_score = score_results.get('formatting_score', 0.0)

    # ── Check which sections are missing or too short ─────────────────────
    missing_sections = []

    # What we recommend for each missing section
    section_recommendations = {
        'experience': "Add a clear 'Experience' or 'Work History' section",
        'education':  "Add an 'Education' section with your qualifications",
        'skills':     "Add a 'Skills' section listing your technical and soft skills",
        'summary':    "Consider adding a 'Summary' or 'Objective' section at the top",
        'projects':   "Consider adding a 'Projects' section to showcase your work"
    }

    for section_name, recommendation in section_recommendations.items():
        section_text = sections.get(section_name, '')
        # "missing" = absent OR present but too short to be meaningful
        if not section_text or len(section_text) < 20:
            missing_sections.append((section_name, recommendation))

    # ── Separate core vs optional missing sections ────────────────────────
    core_missing     = [s for s in missing_sections if s[0] in ['experience', 'education', 'skills']]
    optional_missing = [s for s in missing_sections if s[0] in ['summary', 'projects']]

    if core_missing:
        # Core sections missing → CRITICAL — ATS systems require these
        action_items = [rec for _, rec in core_missing]  # Extract just the rec strings
        recommendations.append(Recommendation(
            title        = 'Add Missing Core Sections',
            description  = (
                f'Your resume is missing {len(core_missing)} essential section(s). '
                f'ATS systems expect standard resume sections.'
            ),
            priority     = Priority.CRITICAL,
            impact_score = 7.0,
            category     = 'formatting',
            action_items = action_items
        ))

    if optional_missing and formatting_score < 15:
        # Optional sections missing AND score is below 75% → worth mentioning
        action_items = [rec for _, rec in optional_missing]
        recommendations.append(Recommendation(
            title        = 'Consider Adding Optional Sections',
            description  = 'Adding a summary and projects section can strengthen your resume.',
            priority     = Priority.LOW,
            impact_score = 2.0,
            category     = 'formatting',
            action_items = action_items
        ))

    # ── Poor overall formatting structure ─────────────────────────────────
    if formatting_score < 12:   # Below 60% of max (20 pts)
        recommendations.append(Recommendation(
            title        = 'Improve Resume Structure',
            description  = (
                f'Your formatting score is {formatting_score:.1f}/20. '
                f'Better structure will improve ATS parsing and readability.'
            ),
            priority     = Priority.HIGH,
            impact_score = 5.0,
            category     = 'formatting',
            action_items = [
                'Use bullet points to list achievements and responsibilities',
                'Add clear section headers (Experience, Education, Skills)',
                'Ensure consistent formatting throughout',
                'Use a clean, single-column layout'
            ]
        ))

    return recommendations