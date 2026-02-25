"""
Scorer Calculations Module
Pure scoring math — each function calculates one component score.

📌 TEACHING NOTE — What does this file do?
    This file contains ONLY number-crunching — no feedback text, no UI calls,
    no caching logic. Every function takes data in and returns a float.

    This is the "Model" in an MVC pattern — pure business logic.
    It's also the most unit-testable part of the system:
    assert calculate_formatting_score(sections, text) == 15.0
    No Streamlit, no spaCy, no network — just math.

📌 TEACHING NOTE — Score composition (must add up to 100):
    calculate_formatting_score()        → max 20 pts
    calculate_keywords_score()          → max 25 pts
    calculate_content_score()           → max 25 pts
    calculate_skill_validation_score()  → max 15 pts
    calculate_ats_compatibility_score() → max 15 pts
    Total:                                  100 pts

    apply_penalties_and_bonuses() then adjusts this total
    up or down before clamping to [0, 100].

📌 TEACHING NOTE — Consistent pattern in every calculator:
    score = 0.0                    ← start from zero
    if condition: score += N       ← add points for each criterion
    return min(MAX, max(0.0, score)) ← clamp to valid range

    This pattern makes each function predictable and safe.
"""

from typing import Dict, List, Optional, Tuple
import re
import streamlit as st
import hashlib


def calculate_formatting_score(sections: Dict[str, str], text: str) -> float:
    """
    Score resume formatting quality out of 20 points.

    📌 TEACHING NOTE — Three criteria measured (max 20 pts total):

        Criterion 1: Section presence (up to 10 pts)
            Each section that exists and has meaningful content:
            experience (>50 chars) → +3.0
            education  (>20 chars) → +2.0
            skills     (>10 chars) → +2.0
            summary    (>30 chars) → +1.5
            projects   (>30 chars) → +1.5
            Total if all present:    10.0 pts

            📌 The minimum length thresholds (>50, >20, >10) filter out
            false positives — a section header detected with no real content.
            "Experience" (10 chars) is just a header, not a real section.

        Criterion 2: Bullet point usage (up to 5 pts)
            ≥15 bullets → +5.0   (heavily structured)
            ≥10 bullets → +4.0
            ≥5  bullets → +3.0
            ≥3  bullets → +2.0
            ≥1  bullet  → +1.0

        Criterion 3: Number of filled sections (up to 5 pts)
            ≥4 sections → +5.0
            ≥3 sections → +4.0
            ≥2 sections → +3.0
            ≥1 section  → +2.0

    📌 TEACHING NOTE — Why count bullet points and section count separately?
        Bullet count rewards DENSITY of structure within sections.
        Section count rewards BREADTH of the resume (having all standard sections).
        A resume with 20 bullets all in one section should score differently
        than one with 5 bullets spread across 4 well-rounded sections.

    📌 TEACHING NOTE — min(20.0, max(0.0, score)):
        Score accumulates as we add points.
        If somehow the math produces a value outside [0, 20], we clamp it.
        This is a safety net — shouldn't be needed with this additive logic,
        but defensive programming prevents surprises.

    Args:
        sections: Dict of section name → section content strings
        text: Full resume text (for bullet counting)

    Returns:
        Float score between 0.0 and 20.0
    """
    score = 0.0

    # ── Criterion 1: Section presence with content length threshold ───────
    # Each section earns points only if it has enough content (not just a header)
    if sections.get('experience') and len(sections['experience']) > 50:
        score += 3.0  # Most important section — highest points
    if sections.get('education') and len(sections['education']) > 20:
        score += 2.0
    if sections.get('skills') and len(sections['skills']) > 10:
        score += 2.0
    if sections.get('summary') and len(sections['summary']) > 30:
        score += 1.5
    if sections.get('projects') and len(sections['projects']) > 30:
        score += 1.5  # Optional section — same weight as summary

    # ── Criterion 2: Bullet point count ──────────────────────────────────
    # Bullet patterns: •, -, *, ◦ at line start OR numbered "1."
    bullet_patterns = [r'^\s*[•\-\*\◦]', r'^\s*\d+\.']
    bullet_count = 0
    for line in text.split('\n'):
        for pattern in bullet_patterns:
            if re.match(pattern, line):
                bullet_count += 1
                break  # Don't double-count a line that matches both patterns

    if bullet_count >= 15:
        score += 5.0
    elif bullet_count >= 10:
        score += 4.0
    elif bullet_count >= 5:
        score += 3.0
    elif bullet_count >= 3:
        score += 2.0
    elif bullet_count >= 1:
        score += 1.0

    # ── Criterion 3: Number of sections present ───────────────────────────
    # 📌 TEACHING NOTE — Checking all 5 known section names:
    #   section_headers_found counts how many sections have ANY content.
    #   (unlike Criterion 1, no minimum length — just present or not)
    #   This rewards breadth — having more sections of any size.
    section_headers_found = 0
    for section_name in ['experience', 'education', 'skills', 'summary', 'projects']:
        if sections.get(section_name):
            section_headers_found += 1

    if section_headers_found >= 4:
        score += 5.0
    elif section_headers_found >= 3:
        score += 4.0
    elif section_headers_found >= 2:
        score += 3.0
    elif section_headers_found >= 1:
        score += 2.0

    return min(20.0, max(0.0, score))  # Clamp to valid range


def calculate_keywords_score(
    resume_keywords: List[str],
    skills: List[str],
    jd_keywords: Optional[List[str]] = None
) -> float:
    """
    Score keyword and skills optimization out of 25 points.

    📌 TEACHING NOTE — Three sub-scores combined (max 25 pts):

        Sub-score 1: Keyword count (up to 10 pts)
            Rewards having many relevant terms in the resume.

        Sub-score 2: Skills count (up to 10 pts)
            Rewards having many listed skills.

        Sub-score 3a: JD keyword overlap (up to 5 pts) — when JD provided
            Rewards matching the specific job description's keywords.
            Uses set intersection (&) to count overlapping keywords.

        Sub-score 3b: Keyword density bonus (up to 3 pts) — when NO JD
            A simpler bonus just for having many keywords overall.

    📌 TEACHING NOTE — JD overlap calculation:
        resume_kw_set = set(kw.lower() for kw in resume_keywords)
        jd_kw_set     = set(kw.lower() for kw in jd_keywords)
        overlap       = len(resume_kw_set & jd_kw_set)  ← & = set intersection
        match_percentage = overlap / len(jd_kw_set)

        We lowercase both sets before intersecting — "Python" and "python"
        should count as a match. This is the same logic as comparator.py.

        The & operator on sets = intersection (elements in BOTH sets).
        It's equivalent to resume_kw_set.intersection(jd_kw_set).

    📌 TEACHING NOTE — Optional[List[str]] = None for jd_keywords:
        The jd_keywords parameter is optional — the user may not have
        provided a job description. When it's None, we skip the JD overlap
        check and use the simpler keyword density bonus instead.
        This is the "two operating modes" pattern we saw in generators2.py.

    Args:
        resume_keywords: Keywords extracted from resume
        skills: Skills list from resume
        jd_keywords: Optional JD keywords (None if no JD provided)

    Returns:
        Float score between 0.0 and 25.0
    """
    score = 0.0

    # ── Sub-score 1: Keyword count (max 10 pts) ───────────────────────────
    keyword_count = len(resume_keywords)
    if keyword_count >= 20:
        score += 10.0
    elif keyword_count >= 15:
        score += 8.0
    elif keyword_count >= 10:
        score += 6.0
    elif keyword_count >= 5:
        score += 4.0
    elif keyword_count >= 3:
        score += 2.0

    # ── Sub-score 2: Skills count (max 10 pts) ────────────────────────────
    skills_count = len(skills)
    if skills_count >= 15:
        score += 10.0
    elif skills_count >= 10:
        score += 8.0
    elif skills_count >= 7:
        score += 6.0
    elif skills_count >= 5:
        score += 4.0
    elif skills_count >= 3:
        score += 2.0

    # ── Sub-score 3a: JD keyword overlap (max 5 pts) — when JD provided ──
    if jd_keywords:
        resume_kw_set = set(kw.lower() for kw in resume_keywords)
        jd_kw_set     = set(kw.lower() for kw in jd_keywords)
        if jd_kw_set:
            overlap          = len(resume_kw_set & jd_kw_set)   # & = set intersection
            match_percentage = overlap / len(jd_kw_set)
            if match_percentage >= 0.7:
                score += 5.0
            elif match_percentage >= 0.5:
                score += 4.0
            elif match_percentage >= 0.3:
                score += 3.0
            elif match_percentage >= 0.2:
                score += 2.0
            elif match_percentage >= 0.1:
                score += 1.0

    # ── Sub-score 3b: Keyword density bonus (max 3 pts) — no JD ──────────
    # Simpler bonus when no JD is available to compare against
    elif keyword_count >= 10:
        score += 3.0

    return min(25.0, max(0.0, score))


def calculate_content_score(
    text: str,
    action_verbs: List[str],
    grammar_results: Dict
) -> float:
    """
    Score content quality out of 25 points.

    📌 TEACHING NOTE — Three components:

        Component 1: Action verb count (max 10 pts)
            Rewards strong, active writing at the start of bullet points.
            Uses the detected verbs from processor_extractors.detect_action_verbs().

        Component 2: Quantified achievements (max 5 pts)
            Counts patterns like "30%", "$50K", "10 users", "reduced by 3"
            Same regex patterns as in analyzer.py — counts evidence of impact.

        Component 3: Grammar-adjusted base score (up to 10 pts)
            Starts at 10.0 and subtracts half the grammar penalty.
            grammar_score = max(0, 10.0 - penalty / 2.0)

    📌 TEACHING NOTE — Grammar incorporated into content score:
        Grammar penalty is applied TWICE:
        1. Here: penalty/2 reduces the content score (max -10 pts)
        2. In apply_penalties_and_bonuses(): full penalty reduces overall score

        This means grammar issues have double impact on the final score.
        The design rationale: grammar quality IS part of content quality
        (a well-written resume has good grammar) AND it separately impacts
        the overall ATS compatibility score.

        ⚠️ This is worth discussing with students — double-counting penalties
        can feel unfair and is a design choice that might need revisiting.

    📌 TEACHING NOTE — max(0.0, 10.0 - grammar_penalty / 2.0):
        If grammar_penalty = 20 (very bad):
        grammar_score = max(0, 10 - 10) = max(0, 0) = 0  ← bottoms out at 0

        If grammar_penalty = 0 (perfect):
        grammar_score = max(0, 10 - 0) = 10  ← full marks

        The max(0.0, ...) prevents negative grammar_score from reducing
        the overall content score below what action verbs earned.

    Args:
        text: Full resume text
        action_verbs: List of detected action verbs
        grammar_results: Dict with penalty_applied

    Returns:
        Float score between 0.0 and 25.0
    """
    score = 0.0

    # ── Component 1: Action verb count (max 10 pts) ───────────────────────
    action_verb_count = len(action_verbs)
    if action_verb_count >= 15:
        score += 10.0
    elif action_verb_count >= 10:
        score += 8.0
    elif action_verb_count >= 7:
        score += 6.0
    elif action_verb_count >= 5:
        score += 4.0
    elif action_verb_count >= 3:
        score += 2.0

    # ── Component 2: Quantified achievements (max 5 pts) ─────────────────
    number_patterns = [
        r'\d+%',                                             # Percentages: 30%
        r'\$\d+',                                            # Dollars: $50K
        r'\d+[kKmMbB]',                                     # Abbreviated: 10K, 2M
        r'\d+\s*(?:users|customers|clients|projects|hours|days|months|years)',
        r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+'
    ]
    achievement_count = 0
    for pattern in number_patterns:
        achievement_count += len(re.findall(pattern, text, re.IGNORECASE))

    if achievement_count >= 10:
        score += 5.0
    elif achievement_count >= 7:
        score += 4.0
    elif achievement_count >= 5:
        score += 3.0
    elif achievement_count >= 3:
        score += 2.0
    elif achievement_count >= 1:
        score += 1.0

    # ── Component 3: Grammar-adjusted base (max 10 pts) ───────────────────
    # grammar_penalty comes from grammar.py's penalty calculation
    # Dividing by 2 means the grammar component penalizes at half rate
    grammar_penalty = grammar_results.get('penalty_applied', 0.0)
    grammar_score   = max(0.0, 10.0 - grammar_penalty / 2.0)
    score          += grammar_score

    return min(25.0, max(0.0, score))


def calculate_skill_validation_score(validation_results: Dict) -> float:
    """
    Score skill validation quality out of 15 points.

    📌 TEACHING NOTE — Thin wrapper pattern:
        This function simply reads 'validation_score' from the results dict
        and clamps it to [0, 15].

        The actual validation_score calculation happens in validator.py
        (in app/ai/). This function just retrieves it and enforces the max.

        Why a wrapper at all? It keeps the scoring interface consistent:
        ALL component scores are calculated by calling a calculate_*() function.
        The caller (scorer.py) doesn't need to know which scores are
        "computed here" vs "retrieved from elsewhere."

        This is the Facade Pattern — a uniform interface hiding different
        implementations behind it.

    📌 TEACHING NOTE — validation_results.get('validation_score', 0.0):
        If skill validation didn't run (e.g., no skills section), this
        key might be missing. .get() with default 0.0 returns zero
        instead of crashing with KeyError.

    Args:
        validation_results: Dict from the skill validator

    Returns:
        Float score between 0.0 and 15.0
    """
    score = validation_results.get('validation_score', 0.0)
    return min(15.0, max(0.0, score))  # Clamp to [0, 15]


def calculate_ats_compatibility_score(
    text: str,
    location_results: Dict,
    sections: Dict[str, str]
) -> float:
    """
    Score ATS compatibility out of 15 points.

    📌 TEACHING NOTE — Starts at 15, deducts for problems (inverse scoring):
        Unlike other calculators that start at 0 and add points,
        this one starts at the MAXIMUM (15.0) and SUBTRACTS for issues.

        Rationale: ATS compatibility is about AVOIDING problems.
        Start with "fully compatible" and penalize each issue found.

        This is called "starts at full marks, deduct for errors" scoring —
        common for compliance-based criteria (safety, accessibility, etc.)

        Compare to calculate_formatting_score():
        - Starts at 0, adds points for good things (reward model)
        vs calculate_ats_compatibility_score():
        - Starts at 15, subtracts for bad things (penalty model)

    📌 TEACHING NOTE — Three ATS compatibility issues penalized:

        Issue 1: Location privacy penalty (from location_results)
            location_penalty = location_results.get('penalty_applied', 0.0)
            Full penalty applied — privacy issues directly hurt ATS scores.

        Issue 2: Special box-drawing characters
            ATS parsers can't handle these Unicode box chars:
            │┤├┼┴┬╔╗╚╝═║╠╣╦╩╬
            They're sometimes used in fancy resume templates.
            > 20 chars → -2.0 pts   > 10 chars → -1.0 pts

        Issue 3: Sections that are too short
            A section present but with fewer than 20 chars is nearly useless.
            "Empty" core sections hurt ATS parsing of key info.
            ≥ 2 short sections → -2.0   ≥ 1 short section → -1.0

        Bonus: Well-populated experience AND skills sections → +1.0
            If experience > 100 chars AND skills > 20 chars, grant a small bonus.

    📌 TEACHING NOTE — Why box-drawing characters hurt ATS?
        Real ATS systems (Workday, Greenhouse, Taleo) process text.
        Box characters are Unicode but many ATS parsers strip them,
        turning structured content into garbled characters.
        Modern resume best practice: use plain text, no special formatting.

    Args:
        text: Full resume text
        location_results: Dict from location detector
        sections: Dict of section name → content

    Returns:
        Float score between 0.0 and 15.0
    """
    score = 15.0   # Start at maximum — deduct for problems

    # ── Penalty 1: Location privacy issues ────────────────────────────────
    location_penalty = location_results.get('penalty_applied', 0.0)
    score -= location_penalty   # Full location penalty applied here

    # ── Penalty 2: Box-drawing characters (ATS parsing problems) ──────────
    special_char_count = len(re.findall(r'[│┤├┼┴┬╔╗╚╝═║╠╣╦╩╬]', text))
    if special_char_count > 20:
        score -= 2.0
    elif special_char_count > 10:
        score -= 1.0

    # ── Penalty 3: Core sections with too little content ──────────────────
    short_sections = 0
    for section_name, content in sections.items():
        if section_name in ['experience', 'education', 'skills']:
            if content and len(content) < 20:  # Present but nearly empty
                short_sections += 1

    if short_sections >= 2:
        score -= 2.0
    elif short_sections >= 1:
        score -= 1.0

    # ── Bonus: Well-populated experience AND skills ────────────────────────
    if (len(sections.get('experience', '')) > 100 and
            len(sections.get('skills', '')) > 20):
        score += 1.0   # Small reward for having substantial key sections

    return min(15.0, max(0.0, score))  # Clamp to [0, 15]


def apply_penalties_and_bonuses(
    base_score: float,
    grammar_results: Dict,
    location_results: Dict,
    skill_validation_results: Dict
) -> Tuple[float, Dict, Dict]:
    """
    Apply final adjustments to the base score and return the result with tracking.

    📌 TEACHING NOTE — Tuple return type: Tuple[float, Dict, Dict]:
        Returns THREE values:
        1. adjusted_score (float) — the final score after all adjustments
        2. penalties (dict)       — {category: points_deducted}
        3. bonuses (dict)         — {category: points_added}

        The penalties and bonuses dicts serve as an AUDIT TRAIL:
        - The user can see exactly what was added or removed and why
        - The PDF report displays these as "+2 (excellent skill validation)"
        - Transparent scoring builds user trust

    📌 TEACHING NOTE — Note: penalties are TRACKED but not subtracted here:
        grammar_penalty = grammar_results.get('penalty_applied', 0.0)
        if grammar_penalty > 0:
            penalties['grammar'] = grammar_penalty
            # ← But we never do: adjusted_score -= grammar_penalty!

        The grammar and location penalties are RECORDED in the dict
        but the actual deductions were already applied in:
        - calculate_content_score() (grammar penalty / 2)
        - calculate_ats_compatibility_score() (location penalty)

        This function ONLY applies the BONUS adjustments.
        The penalties dict is populated purely for display/audit purposes.

        ⚠️ This is a subtle design point worth discussing — students might
        expect penalties to be subtracted here. The actual subtraction
        happened inside the component score calculators.

    📌 TEACHING NOTE — Bonuses applied here:
        Bonus 1: validation_percentage >= 0.9 → +2.0 ("excellent_skill_validation")
        Bonus 2: validation_percentage >= 0.8 → +1.0 ("good_skill_validation")
        Bonus 3: zero grammar errors          → +2.0 ("perfect_grammar")

        These reward exceptional quality above and beyond the base scoring.
        A candidate with perfect grammar AND excellent skill validation
        can earn up to 4 bonus points on top of 100 base points.
        The final clamp: min(100.0, ...) ensures this doesn't exceed 100.

    Args:
        base_score: Sum of all 5 component scores (≤ 100 before bonuses)
        grammar_results: Dict with total_errors and penalty_applied
        location_results: Dict with penalty_applied
        skill_validation_results: Dict with validation_percentage

    Returns:
        Tuple of (adjusted_score, penalties_dict, bonuses_dict)
    """
    penalties       = {}     # Audit trail of deductions (for display)
    bonuses         = {}     # Audit trail of additions (for display)
    adjusted_score  = base_score

    # ── Record penalties (already applied in component scores) ───────────
    # These are NOT subtracted here — they were already subtracted inside
    # calculate_content_score() and calculate_ats_compatibility_score()
    grammar_penalty = grammar_results.get('penalty_applied', 0.0)
    if grammar_penalty > 0:
        penalties['grammar'] = grammar_penalty  # Record for display only

    location_penalty = location_results.get('penalty_applied', 0.0)
    if location_penalty > 0:
        penalties['location_privacy'] = location_penalty  # Record for display only

    # ── Apply skill validation bonuses (extra reward for excellence) ──────
    validation_percentage = skill_validation_results.get('validation_percentage', 0.0)

    if validation_percentage >= 0.9:
        bonus = 2.0
        bonuses['excellent_skill_validation'] = bonus
        adjusted_score += bonus       # ← Actual addition to score

    elif validation_percentage >= 0.8:
        bonus = 1.0
        bonuses['good_skill_validation'] = bonus
        adjusted_score += bonus       # ← Actual addition to score

    # ── Apply perfect grammar bonus ───────────────────────────────────────
    if grammar_results.get('total_errors', 0) == 0:
        bonus = 2.0
        bonuses['perfect_grammar'] = bonus
        adjusted_score += bonus       # ← Actual addition to score

    # Clamp final score to valid range [0, 100]
    adjusted_score = min(100.0, max(0.0, adjusted_score))

    return adjusted_score, penalties, bonuses