"""
PDF Sections 1 — Overall Score, Breakdown, Strengths, Issues, Improvements
First group of PDF section builder functions for the ATS report.

📌 TEACHING NOTE — Why split into sections1, sections2, sections3?
    The complete PDF report has ~10 sections.
    Putting all 10 functions in one file would create a 600+ line file —
    too long to read comfortably.

    The split is by THEME:
        sections1.py → Core scoring sections (score, breakdown, strengths, issues)
        sections2.py → Analysis detail sections (skills, grammar, location, JD)
        sections3.py → Action-oriented sections (recommendations, checklist)

    Each file is ~100-150 lines — a comfortable size for reading and maintenance.

📌 TEACHING NOTE — All functions here follow the same signature:
        def _add_*_section(pdf: ATSReportPDF, data: Dict) -> None

    They all:
    1. Take the PDF object and data as inputs
    2. MUTATE the PDF by calling pdf methods (add content to it)
    3. Return None (they modify the pdf object in place)

    This is consistent function design — predictable for anyone reading the code.
"""

from typing import Dict
from app.core.generator_utils import (
    ATSReportPDF,
    sanitize_text_for_pdf,
    draw_score_bar,
    get_component_score_color_rgb,
    get_score_color_rgb
)


def _add_overall_score_section(pdf: ATSReportPDF, scores: Dict):
    """
    Add the large overall score display at the top of the report.

    📌 TEACHING NOTE — Visual Hierarchy in PDF Design:
        The overall score is the MOST IMPORTANT number in the report.
        We make it visually dominant using:
        - Font size 48 (huge — 4× the body text size)
        - Color-coded (green/orange/red based on score)
        - Centered alignment

        This is a design principle called "Visual Hierarchy" — important
        information should look important. Users should understand the
        overall result in under 1 second of looking at the page.

    📌 TEACHING NOTE — f'{overall_score:.0f}/100':
        :.0f is a format specifier meaning "float with 0 decimal places"
        So 82.7 becomes "83" and 60.0 becomes "60".
        We show /100 to give context (out of 100 possible points).

    📌 TEACHING NOTE — Bonus/Penalty display:
        Some resumes get bonus points (e.g., certifications found)
        or penalty points (e.g., grammar errors, location issues).
        These adjust the final score beyond the base component scores.

        k.replace('_', ' ') converts 'grammar_penalty' → 'grammar penalty'
        for nicer display without underscores.

        We only show this section if bonuses or penalties exist:
        "if bonuses or penalties:" — Python evaluates empty dicts as False.

    Args:
        pdf: The ATSReportPDF object to add content to
        scores: The scores dict from analysis_results
    """
    pdf.add_section_header('Overall ATS Score')

    overall_score   = scores.get('overall_score', 0)
    interpretation  = scores.get('overall_interpretation', '')

    # Color the score based on performance tier (green/orange/red)
    color = get_score_color_rgb(overall_score)

    # Draw the large score number — font 48, bold, color-coded
    pdf.set_font('Helvetica', 'B', 48)
    pdf.set_text_color(*color)   # * unpacks (R, G, B) tuple as 3 args
    pdf.cell(0, 25, f'{overall_score:.0f}/100', align='C',
             new_x='LMARGIN', new_y='NEXT')

    # Draw interpretation text below (e.g., "Good Resume — Close to ATS Ready")
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(100, 100, 100)  # Grey (less prominent)

    # Remove emojis from interpretation for PDF safety
    clean_interpretation = (interpretation
        .replace('🌟', '').replace('✅', '').replace('👍', '')
        .replace('⚠️', '').replace('❌', '').replace('🔴', '')
        .strip()
    )
    pdf.cell(0, 10, clean_interpretation, align='C',
             new_x='LMARGIN', new_y='NEXT')

    # ── Show bonuses and penalties if any exist ───────────────────────────
    bonuses  = scores.get('bonuses', {})
    penalties = scores.get('penalties', {})

    if bonuses or penalties:   # Empty dicts evaluate as False in Python
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 9)   # Small italic for bonus/penalty line

        if bonuses:
            # Format: "+2 (certifications), +1 (linkedin)" in green
            bonus_text = ', '.join([
                f"+{v:.0f} ({k.replace('_', ' ')})" for k, v in bonuses.items()
            ])
            pdf.set_text_color(46, 125, 50)   # Green for bonuses
            pdf.cell(0, 6, f'Bonuses: {bonus_text}', align='C',
                     new_x='LMARGIN', new_y='NEXT')

        if penalties:
            # Format: "-3 (grammar penalty), -2 (location penalty)" in red
            penalty_text = ', '.join([
                f"-{v:.0f} ({k.replace('_', ' ')})" for k, v in penalties.items()
            ])
            pdf.set_text_color(198, 40, 40)   # Red for penalties
            pdf.cell(0, 6, f'Penalties: {penalty_text}', align='C',
                     new_x='LMARGIN', new_y='NEXT')

    pdf.ln(10)   # Space before next section


def _add_score_breakdown_section(pdf: ATSReportPDF, scores: Dict):
    """
    Add a visual breakdown of all 5 component scores with progress bars.

    📌 TEACHING NOTE — The 5 Score Components:
        ('Formatting',         'formatting_score',        20)  → max 20 pts
        ('Keywords & Skills',  'keywords_score',          25)  → max 25 pts
        ('Content Quality',    'content_score',           25)  → max 25 pts
        ('Skill Validation',   'skill_validation_score',  15)  → max 15 pts
        ('ATS Compatibility',  'ats_compatibility_score', 15)  → max 15 pts
        Total maximum: 20+25+25+15+15 = 100 pts

        Each row in the breakdown shows:
        [Name] [███████░░░░░░ bar] [score/max]
        [Optional message about this component]

    📌 TEACHING NOTE — draw_score_bar() coordinate positioning:
        current_x = pdf.get_x()  → where the cursor is after printing the name
        current_y = pdf.get_y()  → current vertical position

        We draw the bar at (current_x, current_y + 1) — 1mm below the text
        baseline so the bar is vertically centered with the text.

        After drawing the bar, we set_x(current_x + 85) to jump past
        the bar (80mm wide + 5mm gap) to print the score number.

    📌 TEACHING NOTE — message_key = key.replace('_score', ''):
        'formatting_score' → 'formatting'
        This lets us look up component-specific messages in component_messages dict.
        String manipulation to derive related dictionary keys is common in Python.

    Args:
        pdf: ATSReportPDF object
        scores: Scores dict from analysis_results
    """
    pdf.add_section_header('Score Breakdown')

    # Define each component: (display name, score key, max points)
    components = [
        ('Formatting',        'formatting_score',        20),
        ('Keywords & Skills', 'keywords_score',          25),
        ('Content Quality',   'content_score',           25),
        ('Skill Validation',  'skill_validation_score',  15),
        ('ATS Compatibility', 'ats_compatibility_score', 15),
    ]

    # Optional per-component messages (e.g., "Good use of keywords")
    component_messages = scores.get('component_messages', {})

    for name, key, max_score in components:
        score = scores.get(key, 0)

        # Derive the message key: 'formatting_score' → 'formatting'
        message_key = key.replace('_score', '')
        message     = component_messages.get(message_key, '')

        # ── Row: Name + Bar + Score number ───────────────────────────────
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)

        # Print component name (60mm wide cell)
        pdf.cell(60, 8, name)

        # Capture cursor position AFTER the name cell, for bar placement
        current_x = pdf.get_x()
        current_y = pdf.get_y()

        # Draw progress bar at current position (80mm wide, 6mm tall)
        draw_score_bar(pdf, score, max_score,
                       current_x, current_y + 1,
                       width=80, height=6)

        # Jump cursor past the bar to print score number
        pdf.set_x(current_x + 85)   # 80mm bar + 5mm gap

        # Print "score/max" in appropriate color
        color = get_component_score_color_rgb(score, max_score)
        pdf.set_text_color(*color)
        pdf.cell(20, 8, f'{score:.0f}/{max_score}')

        pdf.ln(8)   # Move to next row

        # ── Optional message below the row ───────────────────────────────
        if message:
            pdf.set_font('Helvetica', 'I', 9)   # Small italic message
            pdf.set_text_color(100, 100, 100)    # Grey
            pdf.set_x(15)   # Slight indent
            pdf.cell(0, 5, message, new_x='LMARGIN', new_y='NEXT')

        pdf.ln(3)   # Small gap between rows

    pdf.ln(5)   # Larger gap after the whole breakdown table


def _add_strengths_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add the strengths section — what the candidate did well.

    📌 TEACHING NOTE — Early return for empty lists:
        if not strengths: return
        
        An empty list evaluates to False in Python ("falsy").
        If there are no strengths, we return immediately and add nothing.
        This prevents empty section headers from appearing in the PDF —
        much cleaner than a section with "No strengths found."

    📌 TEACHING NOTE — Text color set ONCE before loop:
        pdf.set_text_color(46, 125, 50)  ← green, set once
        for strength in strengths:
            pdf.add_bullet_point(...)    ← all items will be green

        In fpdf2, color state persists until changed.
        Setting it once before the loop is more efficient than setting
        it inside the loop on every iteration.

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict (we extract 'strengths' from it)
    """
    strengths = analysis_results.get('strengths', [])

    # Guard: don't add an empty section
    if not strengths:
        return

    pdf.add_section_header('Strengths')
    pdf.set_text_color(46, 125, 50)  # Green for positive items

    for strength in strengths:
        # Replace emojis with ASCII equivalents for PDF safety
        clean_strength = strength.replace('✅', '[+]').replace('🌟', '[*]')
        pdf.add_bullet_point(clean_strength)

    pdf.ln(5)


def _add_critical_issues_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add critical issues section — problems that must be fixed.

    📌 TEACHING NOTE — Showing "No issues" is good UX:
        Unlike strengths (where we silently skip if empty), critical issues
        ALWAYS shows — even if there are none.

        Why? If the user doesn't see a "Critical Issues" section at all,
        they might think the analysis missed it. Showing "No critical issues
        found! Your resume is in good shape." is reassuring and complete.

        Two different empty-state strategies:
        - Strengths: silent skip (missing strengths = neutral, not noteworthy)
        - Critical Issues: explicit "all clear" (absence of issues IS noteworthy)

    📌 TEACHING NOTE — Color coding for issues:
        (198, 40, 40) is a dark red — Material Design Red 800.
        Red signals danger/error, which is appropriate for critical issues.
        This is consistent with the traffic light system from generator_utils.py.

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict
    """
    critical_issues = analysis_results.get('critical_issues', [])

    pdf.add_section_header('Critical Issues')

    if not critical_issues:
        # Show positive "all clear" message when no critical issues
        pdf.set_text_color(46, 125, 50)   # Green for "all clear"
        pdf.add_text('No critical issues found! Your resume is in good shape.')
        pdf.ln(5)
        return

    # Show each critical issue in red
    pdf.set_text_color(198, 40, 40)   # Red for critical issues
    for issue in critical_issues:
        clean_issue = issue.replace('🔴', '[!]').replace('❌', '[X]')
        pdf.add_bullet_point(clean_issue)

    pdf.ln(5)


def _add_improvements_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add areas for improvement — things that could be better but aren't critical.

    📌 TEACHING NOTE — Orange for "improvements":
        Color hierarchy in this report:
        🟢 Green  (46, 125, 50)  → Strengths, "all clear" messages
        🔴 Red    (198, 40, 40)  → Critical issues, errors
        🟠 Orange (245, 124, 0)  → Improvements (between good and bad)

        Orange is a deliberate middle ground — more urgent than green
        (these need attention) but less alarming than red (not showstoppers).
        This three-color system gives users immediate visual priority cues.

    📌 TEACHING NOTE — 📝 → [>] replacement:
        The 📝 emoji (notepad) is used in feedback strings throughout the app
        to indicate "action required." In PDF it becomes [>] — an arrow-like
        ASCII symbol suggesting "do this."

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict
    """
    improvements = analysis_results.get('improvements', [])

    # Guard: don't add empty section (unlike critical_issues, silence is fine here)
    if not improvements:
        return

    pdf.add_section_header('Areas for Improvement')
    pdf.set_text_color(245, 124, 0)   # Orange — warning/suggestion color

    for improvement in improvements:
        clean_improvement = improvement.replace('📝', '[>]')
        pdf.add_bullet_point(clean_improvement)

    pdf.ln(5)