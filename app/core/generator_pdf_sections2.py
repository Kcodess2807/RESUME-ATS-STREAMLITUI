"""
PDF Sections 2 — Skill Validation, Grammar, Location, JD Comparison
Second group of PDF section builders — the detailed analysis sections.

📌 TEACHING NOTE — What's in this file?
    This file covers the "detailed analysis" sections of the PDF:
    - Skill Validation  → which skills are proven, which aren't
    - Grammar           → error counts and specific corrections
    - Location          → privacy risk and detected sensitive locations
    - JD Comparison     → how well the resume matches a job description

    These sections are DATA-HEAVY — they display lots of structured
    information from the analysis pipeline in a readable PDF format.

📌 TEACHING NOTE — Consistent pattern across all 4 functions:
    1. Extract relevant data with .get() and defaults
    2. Guard clause: return early if no data
    3. Add section header
    4. Display summary statistics
    5. Display details (subsections with bullet points)
    6. Add spacing at the end

    Learning this pattern means you can understand ANY of these functions
    just by recognizing the structure.
"""

from typing import Dict
from app.core.generator_utils import ATSReportPDF, sanitize_text_for_pdf, get_score_color_rgb


def _add_skill_validation_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add the skill validation section showing validated vs unvalidated skills.

    📌 TEACHING NOTE — Data extraction at the top:
        We extract all the data we need FIRST, then display it.
        This makes the display logic clean — no .get() calls buried
        inside the rendering code.

        Pattern:
            skill_validation  = analysis_results.get('skill_validation', {})
            validated_skills  = skill_validation.get('validated_skills', [])
            unvalidated_skills = skill_validation.get('unvalidated_skills', [])
            validation_percentage = skill_validation.get('validation_percentage', 0)

        Each .get() has a safe default ([] or 0) to prevent crashes if
        the key is missing.

    📌 TEACHING NOTE — Summary line formatting:
        f'Total Skills: {total_skills} | Validated: {len(validated_skills)} ({validation_percentage * 100:.0f}%) | Unvalidated: {len(unvalidated_skills)}'

        The | pipe character is used as a visual separator — common in
        data dashboards and status lines. It's space-efficient and clear.

        validation_percentage is stored as 0.0-1.0 (decimal), so we
        multiply by 100 to show as a percentage: 0.73 → "73%"

    📌 TEACHING NOTE — [:10] slicing on validated/unvalidated lists:
        We show at most 10 skills per category.
        A resume might have 30+ skills — showing all of them would
        make this section 2 pages long and hard to scan.
        10 is enough to give a clear picture without overwhelming.

    📌 TEACHING NOTE — ', '.join(projects[:2]):
        Each validated skill has a list of projects that demonstrate it.
        We show at most 2 project names: "E-commerce App, Chatbot Project"
        join() converts the list to a comma-separated string.
        If projects is empty, we show 'N/A' as a safe fallback.

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict
    """
    skill_validation = analysis_results.get('skill_validation', {})

    # Guard: no skill validation data → skip this section entirely
    if not skill_validation:
        return

    pdf.add_section_header('Skill Validation Analysis')

    # Extract data
    validated_skills     = skill_validation.get('validated_skills', [])
    unvalidated_skills   = skill_validation.get('unvalidated_skills', [])
    validation_percentage = skill_validation.get('validation_percentage', 0)
    total_skills = len(validated_skills) + len(unvalidated_skills)

    # Summary statistics line
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.add_text(
        f'Total Skills: {total_skills} | '
        f'Validated: {len(validated_skills)} ({validation_percentage * 100:.0f}%) | '
        f'Unvalidated: {len(unvalidated_skills)}'
    )
    pdf.ln(3)

    # ── Validated skills (green — positive) ──────────────────────────────
    if validated_skills:
        pdf.add_subsection_header('Validated Skills')
        pdf.set_text_color(46, 125, 50)   # Green

        for skill_info in validated_skills[:10]:   # Show max 10
            skill_name   = skill_info.get('skill', 'Unknown')
            projects     = skill_info.get('projects', [])
            projects_text = ', '.join(projects[:2]) if projects else 'N/A'
            pdf.add_bullet_point(f'{skill_name} - demonstrated in: {projects_text}')

    # ── Unvalidated skills (red — needs attention) ────────────────────────
    if unvalidated_skills:
        pdf.ln(3)
        pdf.add_subsection_header('Unvalidated Skills (Need Evidence)')
        pdf.set_text_color(198, 40, 40)   # Red

        for skill in unvalidated_skills[:10]:   # Show max 10
            pdf.add_bullet_point(f'{skill} - not found in projects or experience')

    pdf.ln(5)


def _add_grammar_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add the grammar and spelling analysis section.

    📌 TEACHING NOTE — Showing a penalty in red:
        if penalty > 0:
            pdf.set_text_color(198, 40, 40)
            pdf.add_text(f'Score Penalty: -{penalty:.1f} points')

        We show the penalty prominently in red ONLY when it exists (> 0).
        The minus sign is added manually: f'-{penalty:.1f}'
        :.1f means 1 decimal place: 3.5 shows as "-3.5"

        This makes the cost of grammar errors clear and concrete.

    📌 TEACHING NOTE — Showing suggestions inline:
        f'{message}{suggestion_text}'
        suggestion_text = f' -> {suggestions[0]}' if suggestions else ''

        This produces: "Possible spelling mistake: 'experiance' -> 'experience'"
        or just: "Grammar issue: missing article" (if no suggestion)

        The conditional expression avoids adding " -> " when there's
        nothing to suggest — cleaner output.

    📌 TEACHING NOTE — "No errors" shown at the bottom:
        if total_errors == 0:
            pdf.set_text_color(46, 125, 50)
            pdf.add_text('Excellent! No grammar or spelling errors detected.')

        This check is at the END, after the detail sections.
        If there are no errors, the detail sections above produce nothing,
        and we just show the success message. Clean and simple.

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict
    """
    grammar_results = analysis_results.get('grammar_results', {})

    # Guard: no grammar data → skip section
    if not grammar_results:
        return

    pdf.add_section_header('Grammar & Spelling Analysis')

    # Extract error lists and penalty
    total_errors   = grammar_results.get('total_errors', 0)
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors   = grammar_results.get('minor_errors', [])
    penalty        = grammar_results.get('penalty_applied', 0)

    # Summary statistics line
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.add_text(
        f'Total Errors: {total_errors} | '
        f'Critical: {len(critical_errors)} | '
        f'Moderate: {len(moderate_errors)} | '
        f'Minor: {len(minor_errors)}'
    )

    # Show penalty if one was applied
    if penalty > 0:
        pdf.set_text_color(198, 40, 40)   # Red for penalty
        pdf.add_text(f'Score Penalty: -{penalty:.1f} points')

    pdf.ln(3)

    # ── Critical grammar errors (max 5 shown) ────────────────────────────
    if critical_errors:
        pdf.add_subsection_header('Critical Errors')
        pdf.set_text_color(198, 40, 40)   # Red

        for error in critical_errors[:5]:
            message     = error.get('message', 'Unknown error')
            suggestions = error.get('suggestions', [])
            # Build suggestion text only if suggestions exist
            suggestion_text = f' -> {suggestions[0]}' if suggestions else ''
            pdf.add_bullet_point(f'{message}{suggestion_text}')

    # ── Moderate grammar errors (max 3 shown) ────────────────────────────
    if moderate_errors:
        pdf.ln(2)
        pdf.add_subsection_header('Moderate Errors')
        pdf.set_text_color(245, 124, 0)   # Orange (less severe than red)

        for error in moderate_errors[:3]:
            message = error.get('message', 'Unknown error')
            pdf.add_bullet_point(message)

    # ── Success message when no errors ───────────────────────────────────
    if total_errors == 0:
        pdf.set_text_color(46, 125, 50)   # Green for success
        pdf.add_text('Excellent! No grammar or spelling errors detected.')

    pdf.ln(5)


def _add_location_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add the privacy and location analysis section.

    📌 TEACHING NOTE — Dictionary as a color lookup table:
        risk_colors = {
            'high':   (198, 40, 40),   # Red
            'medium': (245, 124, 0),   # Orange
            'low':    (46, 125, 50),   # Green
            'none':   (46, 125, 50),   # Green
        }
        color = risk_colors.get(privacy_risk, (0, 0, 0))

        Instead of:
            if privacy_risk == 'high': color = (198, 40, 40)
            elif privacy_risk == 'medium': color = (245, 124, 0)
            ...

        Using a dict is more Pythonic (clean, readable) and easier to extend
        (just add a new key-value pair for a new risk level).
        .get(key, default) returns (0, 0, 0) (black) if the risk level
        is something unexpected — a safe fallback.

    📌 TEACHING NOTE — Two-branch display (locations found vs not found):
        if detected_locations:
            → show each location with type and section
            → show recommendation
        else:
            → show "No privacy concerns" message

        This two-branch structure ensures the section always has content —
        users see either what was found OR that nothing problematic was found.

    📌 TEACHING NOTE — loc.get('section', 'unknown'):
        The section field tells WHERE in the resume the location was found:
        'contact_header', 'experience', 'education', 'other'.
        Using .get() with 'unknown' prevents crashes if section is missing.

        Display format: "Bengaluru (gpe) in experience"
        → "{text} ({type}) in {section}"

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict
    """
    location_results = analysis_results.get('location_results', {})

    # Guard: no location data → skip section
    if not location_results:
        return

    pdf.add_section_header('Privacy & Location Analysis')

    # Extract data
    privacy_risk       = location_results.get('privacy_risk', 'none')
    detected_locations = location_results.get('detected_locations', [])
    penalty            = location_results.get('penalty_applied', 0)

    # ── Color lookup by risk level ────────────────────────────────────────
    risk_colors = {
        'high':   (198, 40, 40),   # Red
        'medium': (245, 124, 0),   # Orange
        'low':    (46, 125, 50),   # Green
        'none':   (46, 125, 50),   # Green (same as low — no issues)
    }
    color = risk_colors.get(privacy_risk, (0, 0, 0))   # Black as fallback

    # Show risk level in appropriate color
    pdf.set_text_color(*color)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.add_text(f'Privacy Risk Level: {privacy_risk.upper()}')

    # Show penalty if one was applied
    if penalty > 0:
        pdf.set_text_color(198, 40, 40)   # Red for penalty
        pdf.add_text(f'Score Penalty: -{penalty:.1f} points')

    # ── Branch: locations found ───────────────────────────────────────────
    if detected_locations:
        pdf.ln(2)
        pdf.add_subsection_header('Detected Locations')
        pdf.set_text_color(0, 0, 0)

        # Show up to 5 detected locations
        for loc in detected_locations[:5]:
            loc_text = loc.get('text', 'Unknown')
            loc_type = loc.get('type', 'unknown')   # 'address', 'zip', 'gpe'
            section  = loc.get('section', 'unknown') # 'contact_header', 'experience'
            pdf.add_bullet_point(f'{loc_text} ({loc_type}) in {section}')

        pdf.ln(2)
        # Hardcoded best practice recommendation
        pdf.set_font('Helvetica', 'I', 9)   # Small italic
        pdf.set_text_color(100, 100, 100)   # Grey
        pdf.add_text(
            "Recommendation: Keep only 'City, State' in your contact header. "
            "Remove full addresses and zip codes."
        )

    # ── Branch: no problematic locations found ───────────────────────────
    else:
        pdf.set_text_color(46, 125, 50)   # Green for success
        pdf.add_text('No privacy concerns detected.')

    pdf.ln(5)


def _add_jd_comparison_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add the Job Description match analysis section.

    📌 TEACHING NOTE — pdf.add_page():
        This section calls pdf.add_page() at the start!
        This means it ALWAYS starts on a new page, regardless of where
        the previous section ended.

        Why? JD comparison is a major section with lots of data.
        Starting fresh on a new page gives it room to breathe and
        makes the report feel more organized/professional.

        Other sections don't call add_page() — they flow naturally
        after the previous section. This one is special.

    📌 TEACHING NOTE — Displaying percentages:
        match_percentage is already 0-100 (e.g., 73.5)
        semantic_similarity is 0.0-1.0 (e.g., 0.68)

        For display:
        match_percentage → f'{match_percentage:.0f}%'  → "74%"
        semantic_similarity × 100 → f'{sim_percentage:.0f}%' → "68%"

        Both converted to the same format for consistency in the UI.

    📌 TEACHING NOTE — multi_cell for keyword lists:
        Matched keywords might be: "python, django, aws, docker, kubernetes..."
        This can easily exceed one line width.

        multi_cell() wraps text automatically to the next line.
        cell() would truncate it at the line boundary.
        For lists of keywords, multi_cell is essential.

    📌 TEACHING NOTE — Bullet points for actionable items:
        Missing keywords → "Add 'agile' to your resume"
        Skills gap       → "Consider adding: data visualization"

        The framing matters:
        - "Add keyword" → specific, actionable
        - "Consider adding skill" → softer, because skills take time to learn

        Word choice in feedback UI is a UX decision, not just a code decision.

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict (must contain 'jd_comparison')
    """
    jd_comparison = analysis_results.get('jd_comparison', {})

    # Guard: no JD comparison data (user didn't provide a JD)
    if not jd_comparison:
        return

    # Start on a new page — JD section gets its own page
    pdf.add_page()
    pdf.add_section_header('Job Description Match Analysis')

    # Extract all comparison metrics
    match_percentage     = jd_comparison.get('match_percentage', 0)
    semantic_similarity  = jd_comparison.get('semantic_similarity', 0)
    matched_keywords     = jd_comparison.get('matched_keywords', [])
    missing_keywords     = jd_comparison.get('missing_keywords', [])
    skills_gap           = jd_comparison.get('skills_gap', [])

    # ── Display match percentage ──────────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, 'Keyword Match:')

    color = get_score_color_rgb(match_percentage)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f'{match_percentage:.0f}%', new_x='LMARGIN', new_y='NEXT')

    # ── Display semantic similarity ───────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, 'Semantic Similarity:')

    sim_percentage = semantic_similarity * 100   # Convert 0.0-1.0 → 0-100
    color = get_score_color_rgb(sim_percentage)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f'{sim_percentage:.0f}%', new_x='LMARGIN', new_y='NEXT')

    pdf.ln(5)

    # ── Matched keywords (green — already in resume) ──────────────────────
    if matched_keywords:
        pdf.add_subsection_header(f'Matched Keywords ({len(matched_keywords)})')
        pdf.set_text_color(46, 125, 50)   # Green

        # Join all keywords into one comma-separated string (max 20)
        keywords_text = ', '.join(matched_keywords[:20])
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 6, keywords_text)   # multi_cell for auto line wrap
        pdf.ln(3)

    # ── Missing keywords (red — to add to resume) ─────────────────────────
    if missing_keywords:
        pdf.add_subsection_header(f'Missing Keywords ({len(missing_keywords)})')
        pdf.set_text_color(198, 40, 40)   # Red

        for kw in missing_keywords[:15]:
            pdf.add_bullet_point(f"Add '{kw}' to your resume")
        pdf.ln(3)

    # ── Skills gap (orange — skills to consider learning) ─────────────────
    if skills_gap:
        pdf.add_subsection_header(f'Skills Gap ({len(skills_gap)})')
        pdf.set_text_color(245, 124, 0)   # Orange (softer framing)

        for skill in skills_gap[:10]:
            pdf.add_bullet_point(f'Consider adding: {skill}')

    pdf.ln(5)