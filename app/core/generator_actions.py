"""
Generator Actions Module
Generates a prioritized list of action items from resume analysis results.

📌 TEACHING NOTE — What does this file do?
    After all the analysis is done (grammar, skills, location, scoring),
    the candidate needs to know WHAT TO DO NEXT.

    This module converts raw analysis data into a prioritized to-do list:
        [ ] Fix: Spelling mistake in 'Experiance' -> 'Experience'  [CRITICAL]
        [ ] Remove detailed location information                    [CRITICAL]
        [ ] Add project evidence for skill: Machine Learning        [HIGH]
        [ ] Add keyword to resume: 'agile'                         [MEDIUM]
        [ ] Consider adding skill: 'data visualization'            [MEDIUM]

    Four priority levels:
        'critical' → fix immediately (grammar errors, privacy issues)
        'high'     → should fix (missing skill evidence, bad formatting)
        'medium'   → nice to fix (missing JD keywords, minor formatting)
        'low'      → optional polish (style suggestions)

📌 TEACHING NOTE — Data flow:
    analysis_results (big dict)
         ↓
    generate_action_items()      → List of action dicts
         ↓
    generate_action_items_checklist() → Formatted text string
         ↓
    generator_pdf_sections3.py   → Displayed in PDF

    Each layer transforms the data into a more "human-readable" form.
"""

from typing import Dict, List
from datetime import datetime


def generate_action_items(analysis_results: Dict) -> List[Dict]:
    """
    Extract and prioritize action items from all analysis components.

    📌 TEACHING NOTE — Aggregator Pattern:
        This function is an AGGREGATOR — it reads from many different
        parts of the analysis_results dict and combines everything
        into one unified list.

        It touches:
        - grammar_results    → critical and moderate grammar errors
        - location_results   → privacy risk level
        - skill_validation   → unvalidated skills
        - jd_comparison      → missing keywords and skill gaps
        - scores             → low formatting or content scores

        Each section contributes items with a priority level.
        The final list is returned in the order items were added
        (critical first, then high, medium, low — by construction).

    📌 TEACHING NOTE — Dict structure for each action item:
        {
            'priority': 'critical' | 'high' | 'medium' | 'low',
            'item':     'Human-readable instruction string',
            'category': 'grammar' | 'privacy' | 'skills' | 'keywords' |
                        'formatting' | 'content'
        }

        The 'category' field enables filtering by type in the UI
        (e.g., "show only formatting issues").

    📌 TEACHING NOTE — Slicing with [:3], [:5]:
        We limit how many items come from each source:
        grammar critical errors → max 3
        unvalidated skills      → max 3
        missing JD keywords     → max 5

        Why? Without limits, a resume with 20 grammar errors would generate
        20 action items from grammar alone — overwhelming the user.
        A curated short list is more actionable than an exhaustive one.

    📌 TEACHING NOTE — .get() with default values:
        analysis_results.get('grammar_results', {})
        If 'grammar_results' key doesn't exist, returns {} (empty dict).
        Then grammar_results.get('critical_errors', []) returns [] (empty list).
        This chain prevents KeyError crashes if any section is missing.

    Args:
        analysis_results: Full analysis results dict from the main pipeline

    Returns:
        List of action item dicts sorted by priority (critical first by construction)
    """
    action_items = []

    # ── CRITICAL: Grammar errors ─────────────────────────────────────────
    # Critical grammar errors (spelling, wrong words) hurt credibility most
    grammar_results = analysis_results.get('grammar_results', {})
    for error in grammar_results.get('critical_errors', [])[:3]:  # Max 3
        message     = error.get('message', 'Fix grammar error')
        suggestions = error.get('suggestions', [])
        # Show first suggestion if available: "Fix: ... -> correct_word"
        suggestion  = f' -> {suggestions[0]}' if suggestions else ''
        action_items.append({
            'priority': 'critical',
            'item':     f'Fix: {message}{suggestion}',
            'category': 'grammar'
        })

    # ── CRITICAL/HIGH: Location privacy risk ─────────────────────────────
    # High privacy risk = critical (full address/ZIP found)
    # Medium privacy risk = high (many location mentions)
    location_results = analysis_results.get('location_results', {})
    if location_results.get('privacy_risk') == 'high':
        action_items.append({
            'priority': 'critical',
            'item':     'Remove detailed location information (keep only City, State)',
            'category': 'privacy'
        })
    elif location_results.get('privacy_risk') == 'medium':
        action_items.append({
            'priority': 'high',
            'item':     'Simplify location information in resume',
            'category': 'privacy'
        })

    # ── HIGH: Unvalidated skills ──────────────────────────────────────────
    # Skills listed but not backed by any project or experience
    skill_validation  = analysis_results.get('skill_validation', {})
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    for skill in unvalidated_skills[:3]:   # Show worst 3
        action_items.append({
            'priority': 'high',
            'item':     f'Add project evidence for skill: {skill}',
            'category': 'skills'
        })

    # ── MEDIUM: Job Description gaps ─────────────────────────────────────
    # Only if a JD was provided (jd_comparison may be empty/None)
    jd_comparison = analysis_results.get('jd_comparison', {})
    if jd_comparison:
        # Keywords in JD but missing from resume
        for kw in jd_comparison.get('missing_keywords', [])[:5]:
            action_items.append({
                'priority': 'medium',
                'item':     f'Add keyword to resume: {kw}',
                'category': 'keywords'
            })
        # Skills mentioned in JD but absent from resume
        for skill in jd_comparison.get('skills_gap', [])[:3]:
            action_items.append({
                'priority': 'medium',
                'item':     f'Consider adding skill: {skill}',
                'category': 'skills'
            })

    # ── MEDIUM: Moderate grammar errors ──────────────────────────────────
    # Punctuation/capitalization — noticeable but not critical
    for error in grammar_results.get('moderate_errors', [])[:2]:
        message = error.get('message', 'Fix punctuation/capitalization')
        action_items.append({
            'priority': 'medium',
            'item':     f'Fix: {message}',
            'category': 'grammar'
        })

    # ── HIGH/MEDIUM: Formatting issues ───────────────────────────────────
    # 📌 TEACHING NOTE — Score thresholds as business rules:
    #   formatting_score < 12 (60% of 20) → HIGH priority formatting fixes
    #   formatting_score < 16 (80% of 20) → MEDIUM priority improvements
    #   The .get('formatting_score', 20) default of 20 means:
    #   if the score is missing, assume it's perfect — don't add false alerts.
    scores = analysis_results.get('scores', {})
    if scores.get('formatting_score', 20) < 12:
        action_items.append({
            'priority': 'high',
            'item':     'Add clear section headers (Experience, Education, Skills)',
            'category': 'formatting'
        })
        action_items.append({
            'priority': 'high',
            'item':     'Use bullet points for achievements and responsibilities',
            'category': 'formatting'
        })
    elif scores.get('formatting_score', 20) < 16:
        action_items.append({
            'priority': 'medium',
            'item':     'Improve section organization and add more bullet points',
            'category': 'formatting'
        })

    # ── HIGH/MEDIUM: Content quality ─────────────────────────────────────
    # content_score < 15 (60% of 25) → HIGH priority content fixes
    # content_score < 20 (80% of 25) → MEDIUM improvement
    if scores.get('content_score', 25) < 15:
        action_items.append({
            'priority': 'high',
            'item':     'Add quantifiable achievements (numbers, percentages, metrics)',
            'category': 'content'
        })
        action_items.append({
            'priority': 'high',
            'item':     'Start bullet points with strong action verbs',
            'category': 'content'
        })
    elif scores.get('content_score', 25) < 20:
        action_items.append({
            'priority': 'medium',
            'item':     'Add more quantifiable results to your experience',
            'category': 'content'
        })

    # ── LOW: Minor style suggestions ─────────────────────────────────────
    # Style issues — optional polish, not must-fix
    for error in grammar_results.get('minor_errors', [])[:2]:
        message = error.get('message', 'Style improvement')
        action_items.append({
            'priority': 'low',
            'item':     f'Consider: {message}',
            'category': 'grammar'
        })

    return action_items


def generate_action_items_checklist(analysis_results: Dict) -> str:
    """
    Format action items as a plain-text checklist (for copy-paste or text download).

    📌 TEACHING NOTE — [ ] Checkbox Syntax:
        [ ] is a text-based checkbox — common in Markdown and plain text.
        In a real task manager (Notion, GitHub Issues), these render as
        interactive checkboxes. In plain text, they're visual reminders
        the user can check off manually.

        This format is deliberately simple — no library needed, works
        in any text editor, email, or note-taking app.

    📌 TEACHING NOTE — Grouping by priority:
        Instead of showing items in the order they were added, we
        GROUP them by priority level using a fixed order list:
            priority_order = ['critical', 'high', 'medium', 'low']

        For each priority level:
        1. Filter items of that priority
        2. If any exist, add a section header
        3. List items under it

        This ensures critical items are ALWAYS shown first, regardless
        of the order they were added by generate_action_items().

    📌 TEACHING NOTE — Early return for empty list:
        If no action items, we return a "congratulations" message immediately.
        This avoids printing empty section headers and looks much better.

    📌 TEACHING NOTE — String building with list + join:
        lines = ['line1', 'line2', ...]
        return '\n'.join(lines)
        More efficient than string concatenation in a loop (same reason as generator.py).

    Args:
        analysis_results: Full analysis results dict

    Returns:
        Formatted plain-text checklist string
    """
    action_items = generate_action_items(analysis_results)

    # Edge case: no issues found → congratulatory message
    if not action_items:
        return (
            'ATS Resume Action Items Checklist\n' +
            '=' * 35 +
            '\n\nNo action items needed. Your resume is well-optimized!'
        )

    # Build header
    lines = [
        'ATS Resume Action Items Checklist',
        '=' * 35,
        '',
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ''
    ]

    # Priority labels for section headers
    priority_order  = ['critical', 'high', 'medium', 'low']
    priority_labels = {
        'critical': 'CRITICAL PRIORITY',
        'high':     'HIGH PRIORITY',
        'medium':   'MEDIUM PRIORITY',
        'low':      'LOW PRIORITY'
    }

    # ── Group and display by priority level ──────────────────────────────
    for priority in priority_order:
        # Filter to items of this priority level only
        items = [item for item in action_items if item['priority'] == priority]

        if items:  # Only show section if there are items of this priority
            lines.append(f'\n{priority_labels[priority]}')
            # Separator line matches header length for visual alignment
            lines.append('-' * len(priority_labels[priority]))

            for item in items:
                # [ ] prefix creates visual checkboxes the user can fill in
                lines.append(f"[ ] {item['item']}")

    # Footer
    lines.append('\n' + '=' * 35)
    lines.append('Track your progress by checking off completed items.')

    return '\n'.join(lines)