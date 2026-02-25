"""
PDF Sections 3 — Recommendations and Action Items Checklist
Final group of PDF section builders — the action-oriented closing sections.

📌 TEACHING NOTE — Why are these the LAST sections?
    The report follows a deliberate narrative flow:

    Page 1:  Overall score + breakdown         (What's your score?)
    Page 1:  Strengths + Issues + Improvements (What did you do?)
    Page 2:  Skills + Grammar + Location + JD  (Detailed analysis)
    Page 3+: Recommendations + Action items    (What to do next?)

    This flow mirrors how people naturally think:
    1. What happened? (score)
    2. How did I do in each area? (breakdown)
    3. What specifically needs work? (details)
    4. What should I do about it? (THIS FILE)

    The "action" sections are most valuable — they convert data into
    decisions the candidate can act on immediately.

📌 TEACHING NOTE — Optional dependency pattern in _add_recommendations_section:
    This section uses a try/except ImportError to optionally use an
    advanced recommendation engine (recommendation_generator.py).
    If that module doesn't exist, the section silently skips.
    This is a feature flag via import — a real-world pattern.
"""

from typing import Dict
from app.core.generator_utils import ATSReportPDF, sanitize_text_for_pdf
from app.core.generator_actions import generate_action_items


def _add_recommendations_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add a prioritized recommendations section from the recommendation engine.

    📌 TEACHING NOTE — try/except ImportError (Optional Feature Pattern):
        This entire section is wrapped in:
            try:
                from app.core.recommendation_generator import ...
                ...actual work...
            except ImportError:
                pass

        This means: "Try to use the advanced recommendation engine.
        If it's not installed/available, silently skip this section."

        This is called "graceful degradation for optional features."
        The PDF is still complete and useful without this section —
        it just won't have the advanced recommendations.

        Use cases for this pattern:
        - Features that depend on optional/premium libraries
        - Modules that are still in development
        - Platform-specific code that may not be available everywhere

    📌 TEACHING NOTE — Accessing attributes with dot notation (rec.priority.value):
        rec is a recommendation OBJECT (not a dict).
        It has attributes:  rec.priority, rec.title, rec.description, rec.action_items
        rec.priority is likely an ENUM, so .value gets the string ('critical', 'high', etc.)

        This is different from dicts (rec['priority']).
        Objects use dot notation (rec.priority).
        Python developers must know both — dicts and objects behave differently.

    📌 TEACHING NOTE — priority_icons dict:
        priority_icons = {
            'critical': '[!!!]',
            'high':     '[!!]',
            'medium':   '[!]',
            'low':      '[i]'
        }

        The number of ! marks visually signals severity:
        [!!!] → very urgent    [!] → moderate    [i] → informational

        This is a visual encoding trick — more characters = more urgent.
        Users understand this intuitively without needing to read a legend.

    📌 TEACHING NOTE — all_recommendations[:10]:
        Even if the engine generates 20+ recommendations, we show max 10.
        Too many recommendations = paralysis. The most important 10 are enough.

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict
    """
    try:
        # Attempt to import the advanced recommendation engine
        from app.core.recommendation_generator import (
            generate_all_recommendations,
            format_all_recommendations_for_display
        )

        # Generate recommendations by passing results from each analysis module
        recommendations_result = generate_all_recommendations(
            skill_validation_results = analysis_results.get('skill_validation', {}),
            grammar_results          = analysis_results.get('grammar_results', {}),
            location_results         = analysis_results.get('location_results', {}),
            score_results            = analysis_results.get('scores', {}),
            sections                 = analysis_results.get('processed_data', {}).get('sections', {}),
            keyword_analysis         = analysis_results.get('jd_comparison'),
            resume_keywords          = analysis_results.get('processed_data', {}).get('keywords', [])
        )

        all_recommendations = recommendations_result.get('all_recommendations', [])

        # Guard: skip section if no recommendations generated
        if not all_recommendations:
            return

        # Start on a new page for the recommendations section
        pdf.add_page()
        pdf.add_section_header('Recommendations')

        # Show estimated improvement potential
        estimated_improvement = recommendations_result.get('estimated_improvement', 0)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.add_text(
            f'Following these recommendations could improve your score by '
            f'up to {estimated_improvement:.0f} points.'
        )
        pdf.ln(5)

        # Color and icon per priority level
        priority_colors = {
            'critical': (198, 40, 40),   # Red
            'high':     (245, 124, 0),   # Orange
            'medium':   (255, 193, 7),   # Yellow
            'low':      (46, 125, 50)    # Green
        }
        priority_icons = {
            'critical': '[!!!]',
            'high':     '[!!]',
            'medium':   '[!]',
            'low':      '[i]'
        }

        # ── Display each recommendation ───────────────────────────────────
        for rec in all_recommendations[:10]:   # Cap at 10
            priority = rec.priority.value      # Enum → string (e.g., 'critical')
            color    = priority_colors.get(priority, (0, 0, 0))
            icon     = priority_icons.get(priority, '')

            # Title line with priority icon and color
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(*color)
            pdf.add_text(f'{icon} {rec.title}')

            # Description in black (neutral)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.add_text(rec.description)

            # Action steps in dark grey (slightly de-emphasized)
            pdf.set_text_color(80, 80, 80)
            for action in rec.action_items[:3]:   # Max 3 action steps per rec
                pdf.add_bullet_point(action, indent=15)   # Extra indent (15mm)

            pdf.ln(3)   # Space between recommendations

    except ImportError:
        # recommendation_generator.py not available — silently skip this section
        # 📌 TEACHING NOTE: 'pass' in an except block = intentional silent ignore
        # This is appropriate ONLY when the missing feature is truly optional.
        pass

    pdf.ln(5)


def _add_action_items_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add a priority-grouped action items checklist as the final page.

    📌 TEACHING NOTE — Why this is the LAST section in the PDF:
        The action items checklist is designed to be PRINTED AND USED.
        Placing it last makes it easy to tear out or reference separately.
        It's the candidate's "take-away" — the one page that gives them
        their to-do list in a format they can actually act on.

    📌 TEACHING NOTE — List comprehension filtering:
        critical_items = [item for item in action_items if item['priority'] == 'critical']
        high_items     = [item for item in action_items if item['priority'] == 'high']
        medium_items   = [item for item in action_items if item['priority'] == 'medium']
        low_items      = [item for item in action_items if item['priority'] == 'low']

        This creates four FILTERED lists from one source list.
        List comprehension: [expression for item in iterable if condition]
        is cleaner and more Pythonic than:
            critical_items = []
            for item in action_items:
                if item['priority'] == 'critical':
                    critical_items.append(item)

        All four are computed upfront, then each is displayed in its own block.

    📌 TEACHING NOTE — [ ] checkbox format:
        pdf.add_bullet_point(f"[ ] {item['item']}")

        Each action item is prefixed with [ ] — a visual checkbox.
        The candidate can print this page and literally check off items
        as they improve their resume. This adds real physical usability
        to what could otherwise be just a digital report.

    📌 TEACHING NOTE — Priority color consistency:
        'critical' → Red    (198, 40, 40)
        'high'     → Orange (245, 124, 0)
        'medium'   → Yellow (255, 193, 7)
        'low'      → Green  (46, 125, 50)

        These colors are CONSISTENT throughout the entire PDF.
        The same red that marks critical errors in grammar also marks
        critical action items here. Consistency reduces cognitive load —
        users don't need to learn a new color system for each section.

    📌 TEACHING NOTE — Early return on empty list:
        if not action_items:
            pdf.set_text_color(46, 125, 50)
            pdf.add_text('No action items needed. Your resume is well-optimized!')
            return

        Showing a "congratulations" message is better UX than an empty checklist.
        The green color reinforces the positive message.

    Args:
        pdf: ATSReportPDF object
        analysis_results: Full analysis dict
    """
    # Always start the action items on a new page (it's the closing section)
    pdf.add_page()
    pdf.add_section_header('Action Items Checklist')

    # Subtitle explaining how to use the checklist
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.add_text('Use this checklist to track your resume improvements:')
    pdf.ln(5)

    # Generate action items from the analysis results
    action_items = generate_action_items(analysis_results)

    # ── Edge case: no action items needed ────────────────────────────────
    if not action_items:
        pdf.set_text_color(46, 125, 50)
        pdf.add_text('No action items needed. Your resume is well-optimized!')
        return

    # ── Filter into priority groups ───────────────────────────────────────
    # 📌 List comprehension filtering — see teaching note above
    critical_items = [item for item in action_items if item['priority'] == 'critical']
    high_items     = [item for item in action_items if item['priority'] == 'high']
    medium_items   = [item for item in action_items if item['priority'] == 'medium']
    low_items      = [item for item in action_items if item['priority'] == 'low']

    # ── Critical items (max 5) ────────────────────────────────────────────
    if critical_items:
        pdf.add_subsection_header('Critical Priority')
        pdf.set_text_color(198, 40, 40)   # Red
        for item in critical_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)

    # ── High items (max 5) ────────────────────────────────────────────────
    if high_items:
        pdf.add_subsection_header('High Priority')
        pdf.set_text_color(245, 124, 0)   # Orange
        for item in high_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)

    # ── Medium items (max 5) ──────────────────────────────────────────────
    if medium_items:
        pdf.add_subsection_header('Medium Priority')
        pdf.set_text_color(255, 193, 7)   # Yellow
        for item in medium_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)

    # ── Low items (max 3 — lower cap, these are optional) ────────────────
    if low_items:
        pdf.add_subsection_header('Low Priority')
        pdf.set_text_color(46, 125, 50)   # Green (least urgent)
        for item in low_items[:3]:   # Only 3 — low priority = less important
            pdf.add_bullet_point(f"[ ] {item['item']}")