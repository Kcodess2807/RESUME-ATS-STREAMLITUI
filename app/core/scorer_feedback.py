"""
Scorer Feedback Module
Generates human-readable text from numeric scores — interpretation, messages, strengths, issues.

📌 TEACHING NOTE — What does this file do?
    scorer_calc.py computes NUMBERS.
    THIS file turns those numbers into WORDS the user can understand.

    This is the "View" layer in MVC thinking:
    - Model (scorer_calc.py):    calculates scores → numbers
    - Controller (scorer.py):    coordinates everything
    - View (scorer_feedback.py): presents numbers → text

    Keeping these separate means:
    - Scoring formulas can change in scorer_calc.py without touching feedback text
    - Feedback wording can be updated here without touching math
    - Each file has a single, clear responsibility

📌 TEACHING NOTE — All functions here are PURE FUNCTIONS:
    They take data in and return data out.
    No side effects, no API calls, no Streamlit calls.
    This makes them trivially testable:
        assert generate_score_interpretation(95.0) starts with '🌟'
        assert 'grammar' in generate_critical_issues(bad_scores, grammar, loc)
"""

from typing import Dict, List


def generate_score_interpretation(overall_score: float) -> str:
    """
    Convert a 0-100 score into a one-line summary message with emoji.

    📌 TEACHING NOTE — Score tier thresholds (6 tiers):
        ≥ 90 → 🌟 Excellent   (top 10%)
        ≥ 80 → ✅ Great        (good)
        ≥ 70 → 👍 Good         (above average)
        ≥ 60 → ⚠️ Fair         (below average — needs work)
        ≥ 50 → ❌ Below Average (significant gaps)
        <  50 → 🔴 Poor         (major revision needed)

        These thresholds are business decisions, not math.
        Different ATS systems use different pass/fail cut-offs.
        Typical ATS systems filter out resumes below 70-75.

    📌 TEACHING NOTE — Emoji as status indicators:
        🌟 ✅ 👍 → positive/green family (score is fine)
        ⚠️      → warning/yellow (attention needed)
        ❌ 🔴   → negative/red family (action required)

        These match the color system used in the PDF:
        green (46, 125, 50) / orange (245, 124, 0) / red (198, 40, 40)
        Visual consistency across text and PDF outputs.

    📌 TEACHING NOTE — elif chain vs dict lookup:
        This could be rewritten as a list of (threshold, message) pairs:
            tiers = [(90, '🌟 Excellent...'), (80, '✅ Great...'), ...]
            for threshold, message in tiers:
                if overall_score >= threshold: return message

        The elif chain is more readable for students learning Python.
        The list approach is more scalable if thresholds change frequently.
        Both produce identical results — choose based on readability.

    Args:
        overall_score: Float 0.0–100.0

    Returns:
        Single-line interpretation string with emoji
    """
    if overall_score >= 90:
        return '🌟 Excellent! Your resume is highly optimized for ATS systems.'
    elif overall_score >= 80:
        return '✅ Great! Your resume should perform well with most ATS systems.'
    elif overall_score >= 70:
        return '👍 Good! Your resume is ATS-friendly with room for minor improvements.'
    elif overall_score >= 60:
        return '⚠️ Fair. Your resume needs some improvements to be fully ATS-compatible.'
    elif overall_score >= 50:
        return '❌ Below Average. Significant improvements needed for ATS compatibility.'
    else:
        return '🔴 Poor. Your resume requires major revisions to pass ATS screening.'


def generate_score_breakdown_messages(
    formatting_score: float,
    keywords_score: float,
    content_score: float,
    skill_validation_score: float,
    ats_compatibility_score: float
) -> Dict[str, str]:
    """
    Generate one short status message per component score.

    📌 TEACHING NOTE — Per-component thresholds (percentage-based):
        Each component has its own max, so thresholds are absolute values
        calibrated as percentages of the max:

        Formatting (max 20):
            ≥18 (90%)  → Excellent
            ≥15 (75%)  → Good
            ≥12 (60%)  → Adequate
            <12        → Needs improvement

        Keywords (max 25):
            ≥22 (88%)  → Excellent
            ≥18 (72%)  → Good
            ≥14 (56%)  → Adequate
            <14        → Needs more

        Content (max 25):
            ≥22 (88%)  → Excellent
            ≥18 (72%)  → Good
            ≥14 (56%)  → Adequate
            <14        → Needs improvement

        Skill Validation (max 15):
            ≥13 (87%)  → Excellent
            ≥10 (67%)  → Good
            ≥7  (47%)  → Some lacking
            <7         → Many lacking

        ATS Compatibility (max 15):
            ≥13 (87%)  → Excellent
            ≥11 (73%)  → Good
            ≥9  (60%)  → Adequate
            <9         → Needs improvement

    📌 TEACHING NOTE — Building a dict of messages:
        messages = {}
        ... multiple if/elif blocks ...
        return messages

        Each if/elif block adds ONE key to the dict.
        The caller accesses: component_messages['formatting'], etc.
        This is a "message map" — maps component names to status strings.

    📌 TEACHING NOTE — These messages appear in the PDF breakdown table:
        Each row in the score breakdown section shows:
        [Name] [████░░░ bar] [score/max]
        [message in small italic below]
        e.g., "Good formatting with minor improvements possible"

    Args:
        Each component score as a float

    Returns:
        Dict mapping component name to one-line status message
    """
    messages = {}

    # ── Formatting (max 20) ───────────────────────────────────────────────
    if formatting_score >= 18:
        messages['formatting'] = 'Excellent structure and organization'
    elif formatting_score >= 15:
        messages['formatting'] = 'Good formatting with minor improvements possible'
    elif formatting_score >= 12:
        messages['formatting'] = 'Adequate formatting, consider adding more structure'
    else:
        messages['formatting'] = 'Needs improvement: add sections and bullet points'

    # ── Keywords & Skills (max 25) ────────────────────────────────────────
    if keywords_score >= 22:
        messages['keywords'] = 'Excellent keyword optimization'
    elif keywords_score >= 18:
        messages['keywords'] = 'Good keyword presence'
    elif keywords_score >= 14:
        messages['keywords'] = 'Adequate keywords, could add more relevant terms'
    else:
        messages['keywords'] = 'Needs more keywords and skills'

    # ── Content Quality (max 25) ──────────────────────────────────────────
    if content_score >= 22:
        messages['content'] = 'Excellent content quality with strong action verbs'
    elif content_score >= 18:
        messages['content'] = 'Good content with measurable achievements'
    elif content_score >= 14:
        messages['content'] = 'Adequate content, add more quantifiable results'
    else:
        messages['content'] = 'Needs improvement: add action verbs and metrics'

    # ── Skill Validation (max 15) ─────────────────────────────────────────
    if skill_validation_score >= 13:
        messages['skill_validation'] = 'Excellent skill validation'
    elif skill_validation_score >= 10:
        messages['skill_validation'] = 'Good skill validation'
    elif skill_validation_score >= 7:
        messages['skill_validation'] = 'Some skills lack supporting evidence'
    else:
        messages['skill_validation'] = 'Many skills are not validated by projects'

    # ── ATS Compatibility (max 15) ────────────────────────────────────────
    if ats_compatibility_score >= 13:
        messages['ats_compatibility'] = 'Excellent ATS compatibility'
    elif ats_compatibility_score >= 11:
        messages['ats_compatibility'] = 'Good ATS compatibility'
    elif ats_compatibility_score >= 9:
        messages['ats_compatibility'] = 'Adequate ATS compatibility with minor issues'
    else:
        messages['ats_compatibility'] = 'ATS compatibility needs improvement'

    return messages


def generate_strengths(
    score_results: Dict,
    skill_validation_results: Dict,
    grammar_results: Dict
) -> List[str]:
    """
    Build a list of things the candidate did well.

    📌 TEACHING NOTE — Thresholds for "strength" vs "neutral":
        Only HIGH-performing criteria get listed as strengths.
        Each component uses a threshold that's ~75-80% of its maximum:

        formatting_score     ≥ 16 / 20  (80%)
        keywords_score       ≥ 20 / 25  (80%)
        content_score        ≥ 20 / 25  (80%)
        skill_validation     ≥ 12 / 15  (80%)
        ats_compatibility    ≥ 13 / 15  (87%)
        grammar errors       == 0       (100% — perfect)

        The 80% rule: only things the candidate did really well,
        not just "adequate." Listing mediocre performance as a strength
        would feel dishonest and unhelpful.

    📌 TEACHING NOTE — f-string with percentage calculation:
        validation_pct = skill_validation_results.get('validation_percentage', 0) * 100
        strengths.append(f'✅ {validation_pct:.0f}% of skills are validated by projects')

        validation_percentage is stored as 0.0-1.0.
        Multiply by 100 then :.0f formats as an integer percentage.
        Showing the actual number ("73% of skills validated") is more
        informative than just "Good skill validation."

    📌 TEACHING NOTE — Fallback message when no strengths found:
        if not strengths:
            strengths.append('Your resume has potential - focus on the recommendations below')

        Rather than returning an empty list (which would look like a bug),
        we always return at least one message.
        The fallback is encouraging ("has potential") while redirecting
        the user's attention to actionable recommendations.

    Args:
        score_results: Scores dict from _compute_overall_score()
        skill_validation_results: From skill validator
        grammar_results: From grammar checker

    Returns:
        Non-empty list of strength strings (at least the fallback message)
    """
    strengths = []

    if score_results['formatting_score'] >= 16:
        strengths.append('✅ Well-structured with clear sections and bullet points')

    if score_results['keywords_score'] >= 20:
        strengths.append('✅ Strong keyword optimization and skills presence')

    if score_results['content_score'] >= 20:
        strengths.append('✅ Excellent use of action verbs and quantifiable achievements')

    if score_results['skill_validation_score'] >= 12:
        validation_pct = skill_validation_results.get('validation_percentage', 0) * 100
        strengths.append(f'✅ {validation_pct:.0f}% of skills are validated by projects')

    if score_results['ats_compatibility_score'] >= 13:
        strengths.append('✅ Excellent ATS compatibility with clean formatting')

    if grammar_results.get('total_errors', 0) == 0:
        strengths.append('✅ Error-free grammar and spelling')

    # ── Fallback: always return at least one message ──────────────────────
    if not strengths:
        strengths.append('Your resume has potential - focus on the recommendations below')

    return strengths


def generate_critical_issues(
    score_results: Dict,
    grammar_results: Dict,
    location_results: Dict
) -> List[str]:
    """
    Build a list of critical problems that must be fixed.

    📌 TEACHING NOTE — What makes something "critical" vs "improvement"?
        Critical issues are things that will likely cause ATS rejection
        or make a recruiter immediately dismiss the resume:
        - Grammar errors → looks unprofessional
        - High privacy risk → sensitive personal info exposed
        - Very low formatting score → ATS can't parse it
        - Very low keyword score → ATS filters it out
        - Very low skill validation → claims without evidence

        "Improvements" (generate_improvements) are for scores that are
        mediocre — worth improving but not showstoppers.

    📌 TEACHING NOTE — Thresholds for critical (very low performance):
        formatting_score     < 10 / 20  (below 50%)
        keywords_score       < 12 / 25  (below 48%)
        skill_validation     <  7 / 15  (below 47%)
        grammar errors       > 0 critical errors
        privacy_risk         == 'high'

        These are "danger zone" thresholds — the candidate is well below
        acceptable performance and needs immediate attention.

    📌 TEACHING NOTE — issues list may be empty:
        Unlike generate_strengths() which always returns at least one item,
        generate_critical_issues() can return an empty list.
        That's the desired behavior — if there are no critical issues,
        the UI shows "No critical issues found!" (handled in the PDF sections).

    📌 TEACHING NOTE — conditional formatting in f-strings:
        f'🔴 {critical_errors} critical grammar/spelling error(s) detected'
        The variable is inserted directly. If critical_errors = 3:
        → "🔴 3 critical grammar/spelling error(s) detected"
        Using "error(s)" instead of "errors" handles the singular case
        (1 error vs 2 errors) without needing an if/else.

    Args:
        score_results: Scores dict
        grammar_results: From grammar checker
        location_results: From location detector

    Returns:
        List of critical issue strings (may be empty if no critical issues)
    """
    issues = []

    # Critical grammar errors → immediate red flag for recruiters
    critical_errors = len(grammar_results.get('critical_errors', []))
    if critical_errors > 0:
        issues.append(f'🔴 {critical_errors} critical grammar/spelling error(s) detected')

    # High privacy risk → personal safety concern
    if location_results.get('privacy_risk') == 'high':
        issues.append('🔴 High privacy risk: Remove detailed location information')

    # Below 50% on formatting → ATS can't parse the resume properly
    if score_results['formatting_score'] < 10:
        issues.append('🔴 Poor formatting: Add clear sections and bullet points')

    # Below 48% on keywords → ATS keyword matching will fail
    if score_results['keywords_score'] < 12:
        issues.append('🔴 Insufficient keywords and skills')

    # Below 47% on skill validation → claims without evidence
    if score_results['skill_validation_score'] < 7:
        issues.append('🔴 Most skills lack supporting evidence in projects')

    return issues  # May be empty — that's fine (means no critical issues)


def generate_improvements(
    score_results: Dict,
    skill_validation_results: Dict
) -> List[str]:
    """
    Build a list of medium-priority improvements (not critical, but worth doing).

    📌 TEACHING NOTE — Band-based improvement triggers:
        Each criterion uses a RANGE, not just a single threshold:
        12 ≤ formatting_score < 16  → add bullet points
        14 ≤ keywords_score  < 20   → add keywords
        14 ≤ content_score   < 20   → add achievements

        This means:
        - If score ≥ 16  → already good, no improvement suggestion (strength instead)
        - If 12 ≤ score < 16 → suggest improvement
        - If score < 12  → it's a CRITICAL issue (handle in generate_critical_issues)

        The three functions (strengths, critical, improvements) together cover
        the full score range with NO gaps and NO overlaps:
        Low   (<threshold1) → critical issue
        Mid   (threshold1-threshold2) → improvement suggestion
        High  (≥threshold2) → strength

    📌 TEACHING NOTE — Showing specific counts in improvement messages:
        unvalidated_count = len(skill_validation_results.get('unvalidated_skills', []))
        f'📝 Validate {unvalidated_count} skill(s) by adding relevant project details'

        Telling the user "validate 3 skills" is more actionable than
        "validate some skills." Specific numbers set clear expectations.

    📌 TEACHING NOTE — improvements may be empty:
        If all scores are either very high (strengths) or very low (critical issues),
        the improvements list will be empty. That's correct behavior —
        the candidate should focus on critical issues first anyway.

    Args:
        score_results: Scores dict
        skill_validation_results: From skill validator

    Returns:
        List of improvement strings (may be empty)
    """
    improvements = []

    # ── Formatting: medium band (12–16 out of 20) ─────────────────────────
    if 12 <= score_results['formatting_score'] < 16:
        improvements.append('📝 Add more bullet points and improve section organization')

    # ── Keywords: medium band (14–20 out of 25) ───────────────────────────
    if 14 <= score_results['keywords_score'] < 20:
        improvements.append('📝 Include more relevant keywords and technical skills')

    # ── Content: medium band (14–20 out of 25) ────────────────────────────
    if 14 <= score_results['content_score'] < 20:
        improvements.append('📝 Add more quantifiable achievements and action verbs')

    # ── Skill validation: medium band (7–12 out of 15) ───────────────────
    if 7 <= score_results['skill_validation_score'] < 12:
        unvalidated_count = len(skill_validation_results.get('unvalidated_skills', []))
        improvements.append(
            f'📝 Validate {unvalidated_count} skill(s) by adding relevant project details'
        )

    # ── ATS compatibility: medium band (9–13 out of 15) ──────────────────
    if 9 <= score_results['ats_compatibility_score'] < 13:
        improvements.append('📝 Simplify formatting for better ATS compatibility')

    return improvements  # May be empty — correct behavior