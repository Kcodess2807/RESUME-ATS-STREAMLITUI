"""
PDF Report Generator Module
Generates downloadable PDF reports and plain-text summaries of ATS analysis results.

📌 TEACHING NOTE — What does this file do?
    After the app analyzes a resume, the user wants to DOWNLOAD the results.
    This module creates two types of output:

    1. PDF Report  → Professional formatted report with colors, sections, charts
                     Uses the fpdf2 library (Python PDF generation)
                     Delivered as bytes → converted to base64 → download link

    2. Text Summary → Plain text version (no formatting)
                      Useful for copy-pasting or plain email
                      Emojis are replaced with text symbols ([+], [!], [>])

📌 TEACHING NOTE — How the PDF is assembled:
    The report is built section by section by calling helper functions
    imported from several companion files:

    generator_pdf_sections1.py → overall score, breakdown, strengths, issues
    generator_pdf_sections2.py → skill validation, grammar, location, JD comparison
    generator_pdf_sections3.py → recommendations, action items
    generator_actions.py       → action item generation logic

    This split keeps each file manageable. Without splitting, the generator
    would be 500+ lines in a single file — hard to read and maintain.
    This is called "modular design."

📌 TEACHING NOTE — File type produced: bytes
    pdf.output() returns a bytearray (raw binary data).
    bytes() converts it to an immutable bytes object.
    Binary data is what actually makes up a PDF file on disk.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import io
import base64
from fpdf import FPDF

# Import the PDF base class and color utility from helper file
from app.core.generator_utils import ATSReportPDF, get_score_color_rgb

# Import PDF section builders — each function adds one section to the PDF
from app.core.generator_pdf_sections1 import (
    _add_overall_score_section,    # Big score display at top
    _add_score_breakdown_section,  # Table of component scores
    _add_strengths_section,        # What the candidate did well
    _add_critical_issues_section,  # Must-fix problems
    _add_improvements_section      # Nice-to-fix suggestions
)
from app.core.generator_pdf_sections2 import (
    _add_skill_validation_section, # Validated vs unvalidated skills
    _add_grammar_section,          # Grammar errors found
    _add_location_section,         # Privacy/location issues
    _add_jd_comparison_section     # Job description match results
)
from app.core.generator_pdf_sections3 import (
    _add_recommendations_section,  # Prioritized recommendations
    _add_action_items_section      # Specific next steps for the candidate
)
from app.core.generator_actions import generate_action_items, generate_action_items_checklist


def generate_pdf_report(
    analysis_results: Dict,
    user_info: Optional[Dict] = None
) -> bytes:
    """
    Build a complete PDF report from analysis results and return it as bytes.

    📌 TEACHING NOTE — fpdf2 Library Basics:
        fpdf2 is a Python library for generating PDF files programmatically.
        You build the PDF by calling methods on a PDF object:

        pdf = FPDF()           → create PDF object
        pdf.add_page()         → add a new page
        pdf.set_font(...)      → choose font, style, size
        pdf.cell(...)          → add a text cell
        pdf.ln(10)             → add 10mm vertical space

        It's like painting on a canvas, line by line.
        ATSReportPDF (from generator_utils.py) is a SUBCLASS of FPDF that
        adds custom methods like add_title() and handles headers/footers.

    📌 TEACHING NOTE — pdf.alias_nb_pages():
        This tells fpdf2 to track total page count.
        It enables "Page 1 of 3" style footers — the total page count
        is only known AFTER all pages are added, so it's resolved at the end.

    📌 TEACHING NOTE — Conditional section:
        if analysis_results.get('jd_comparison'):
            _add_jd_comparison_section(pdf, analysis_results)

        The JD comparison section only appears if the user provided a
        job description. If not, jd_comparison is None/missing — we skip it.
        .get() returns None (not KeyError) if key doesn't exist.

    📌 TEACHING NOTE — bytes(pdf.output()):
        pdf.output() returns a bytearray.
        bytes() converts it to immutable bytes — the standard type for
        binary data in Python. Most file writing and HTTP response functions
        expect bytes, not bytearray.

    Args:
        analysis_results: Full results dict from the main analysis pipeline
        user_info: Optional dict with 'name' key for personalizing the report

    Returns:
        PDF file as a bytes object (ready to write to disk or send via HTTP)
    """
    # Create the PDF object (subclass of FPDF with custom styles)
    pdf = ATSReportPDF()

    # Enable "Page X of Y" functionality (resolves at render time)
    pdf.alias_nb_pages()
    pdf.add_page()

    # ── Report header ─────────────────────────────────────────────────────
    pdf.add_title('ATS Resume Score Report')

    # Metadata: generation timestamp and user name (if available)
    pdf.set_font('Helvetica', 'I', 10)   # Italic, size 10
    pdf.set_text_color(128, 128, 128)    # Grey color for metadata
    pdf.cell(
        0, 6,
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        align='C', new_x='LMARGIN', new_y='NEXT'  # Centered, move to next line
    )

    # Optionally add the user's name to personalize the report
    if user_info and user_info.get('name'):
        pdf.cell(
            0, 6,
            f"User: {user_info['name']}",
            align='C', new_x='LMARGIN', new_y='NEXT'
        )

    pdf.ln(10)  # 10mm vertical spacer

    # ── Extract scores dict (used by multiple section builders) ──────────
    scores = analysis_results.get('scores', {})

    # ── Add each section in order ────────────────────────────────────────
    # 📌 TEACHING NOTE — Order matters for PDF layout:
    #   fpdf2 draws top-to-bottom, so the call order = display order.
    #   Each _add_*_section() function moves the cursor to the next position.

    _add_overall_score_section(pdf, scores)       # Big score at top
    _add_score_breakdown_section(pdf, scores)     # Per-component score table
    _add_strengths_section(pdf, analysis_results) # Green checkmarks
    _add_critical_issues_section(pdf, analysis_results)  # Red alerts
    _add_improvements_section(pdf, analysis_results)     # Orange suggestions

    _add_skill_validation_section(pdf, analysis_results) # Validated skills
    _add_grammar_section(pdf, analysis_results)          # Grammar errors
    _add_location_section(pdf, analysis_results)         # Privacy issues

    # JD comparison section only appears if a JD was provided
    if analysis_results.get('jd_comparison'):
        _add_jd_comparison_section(pdf, analysis_results)

    _add_recommendations_section(pdf, analysis_results)  # Prioritized advice
    _add_action_items_section(pdf, analysis_results)     # Specific next steps

    # Convert PDF to bytes and return
    return bytes(pdf.output())


def get_pdf_download_link(pdf_bytes: bytes, filename: str = 'ats_report.pdf') -> str:
    """
    Convert PDF bytes into a base64-encoded data URL for browser download.

    📌 TEACHING NOTE — What is Base64?
        Browsers can't directly handle raw binary data in HTML links.
        Base64 encoding converts binary data to a safe ASCII string
        using only 64 characters (A-Z, a-z, 0-9, +, /).

        Example:
        bytes: b'\x25\x50\x44\x46'  (PDF magic bytes)
        base64: 'JVBER'             (ASCII representation)

        The resulting "data URL" looks like:
        "data:application/pdf;base64,JVBER..."

        Browsers understand this format and trigger a file download when
        the user clicks a link with this as the href.

    📌 TEACHING NOTE — .decode() after base64.b64encode():
        base64.b64encode() returns bytes (e.g., b'JVBER...')
        .decode() converts bytes to string (e.g., 'JVBER...')
        We need a string to put into the HTML href attribute.

    Args:
        pdf_bytes: PDF file as bytes (from generate_pdf_report())
        filename: Name the file should have when downloaded

    Returns:
        Data URL string for use as href in a download link
    """
    # Encode binary PDF data as base64 ASCII string
    b64 = base64.b64encode(pdf_bytes).decode()

    # Return a data URL — browsers recognize this as a downloadable file
    return f'data:application/pdf;base64,{b64}'


def generate_summary_text(analysis_results: Dict) -> str:
    """
    Generate a plain-text summary of the analysis results.

    📌 TEACHING NOTE — Why a plain text version?
        PDFs require a library and produce formatted binary output.
        Plain text is:
        - Easier to copy-paste into an email
        - Accessible without a PDF viewer
        - Simpler to generate (no library needed)
        - Searchable by screen readers (accessibility)

        The app likely offers both: "Download PDF" and "Copy Summary".

    📌 TEACHING NOTE — Emoji removal:
        The PDF renders emojis as visual symbols.
        Plain text terminals and emails might not display emojis correctly.
        We replace emojis with text equivalents:
            ✅ → [+]
            🔴/❌ → [!]
            📝 → [>]

        A more robust approach would use a library like 'emoji' to strip
        all emojis automatically, rather than hardcoding each one.

    📌 TEACHING NOTE — Building strings with a list and join:
        Instead of:
            text = ""
            text += "line 1\n"
            text += "line 2\n"
            ...
        We use:
            lines = ["line 1", "line 2", ...]
            return '\n'.join(lines)

        Why? String concatenation (+=) in a loop is O(n²) — each += creates
        a new string and copies everything. Building a list and joining once
        at the end is O(n) — much more efficient for large outputs.

    Args:
        analysis_results: Full analysis results dict

    Returns:
        Plain text summary string, suitable for copy-paste or file saving
    """
    scores = analysis_results.get('scores', {})
    overall_score = scores.get('overall_score', 0)
    interpretation = scores.get('overall_interpretation', '')

    # Remove emojis from the interpretation for plain text output
    clean_interpretation = interpretation
    for emoji in ['🌟', '✅', '👍', '⚠️', '❌', '🔴']:
        clean_interpretation = clean_interpretation.replace(emoji, '')
    clean_interpretation = clean_interpretation.strip()

    # Build the text line by line using a list (efficient string building)
    lines = [
        'ATS Resume Analysis Summary',
        '=' * 30,
        '',
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        '',
        f'Overall Score: {overall_score:.0f}/100',   # :.0f = 0 decimal places
        clean_interpretation,
        '',
        'Score Breakdown:',
        f"  - Formatting:       {scores.get('formatting_score', 0):.0f}/20",
        f"  - Keywords & Skills:{scores.get('keywords_score', 0):.0f}/25",
        f"  - Content Quality:  {scores.get('content_score', 0):.0f}/25",
        f"  - Skill Validation: {scores.get('skill_validation_score', 0):.0f}/15",
        f"  - ATS Compatibility:{scores.get('ats_compatibility_score', 0):.0f}/15",
        ''
    ]

    # ── Strengths section ─────────────────────────────────────────────────
    strengths = analysis_results.get('strengths', [])
    if strengths:
        lines.append('Strengths:')
        for strength in strengths:
            # Replace positive emojis with text symbol [+]
            clean_strength = strength
            for emoji in ['✅', '🌟']:
                clean_strength = clean_strength.replace(emoji, '[+]')
            lines.append(f'  {clean_strength}')
        lines.append('')

    # ── Critical issues section ───────────────────────────────────────────
    critical_issues = analysis_results.get('critical_issues', [])
    if critical_issues:
        lines.append('Critical Issues:')
        for issue in critical_issues:
            # Replace negative emojis with warning symbol [!]
            clean_issue = issue
            for emoji in ['🔴', '❌']:
                clean_issue = clean_issue.replace(emoji, '[!]')
            lines.append(f'  {clean_issue}')
        lines.append('')

    # ── Improvements section ──────────────────────────────────────────────
    improvements = analysis_results.get('improvements', [])
    if improvements:
        lines.append('Areas for Improvement:')
        for improvement in improvements:
            # Replace notepad emoji with action arrow [>]
            clean_improvement = improvement.replace('📝', '[>]')
            lines.append(f'  {clean_improvement}')
        lines.append('')

    # Footer
    lines.append('=' * 30)
    lines.append('Generated by ATS Resume Scorer')

    # Join all lines with newlines into a single string
    # This is the efficient way to build multi-line strings in Python
    return '\n'.join(lines)