"""
Generator Utilities Module
Core PDF building blocks: the ATSReportPDF class, color functions, and text sanitizer.

📌 TEACHING NOTE — Why a separate utils file for the generator?
    The generator system is split across 6 files:
        generator.py              → orchestrator (calls everything)
        generator_actions.py      → action item logic
        generator_pdf_sections1-3 → content for each PDF section
        generator_utils.py        ← YOU ARE HERE (shared tools)

    This file is the FOUNDATION — everything the other generator files need:
    - sanitize_text_for_pdf()  → make any text PDF-safe
    - ATSReportPDF class       → the custom PDF object with helper methods
    - get_score_color_rgb()    → convert a score to a color
    - draw_score_bar()         → draw a visual progress bar in the PDF

    By centralizing these here, ALL section files share the same tools
    without duplicating code. This is the DRY principle in action.

📌 TEACHING NOTE — Inheritance (OOP):
    The most important concept in this file is ATSReportPDF,
    which INHERITS from FPDF (the third-party PDF library class).
    This is a classic example of Object-Oriented Programming inheritance.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import io
import base64
from fpdf import FPDF  # Third-party library for generating PDF files


def sanitize_text_for_pdf(text: str) -> str:
    """
    Convert any Unicode text (emojis, special chars) to PDF-safe ASCII.

    📌 TEACHING NOTE — Why do PDFs struggle with Unicode?
        Standard PDF fonts (Helvetica, Times, Courier) only support ASCII
        characters (the basic 128 characters in English).
        Emojis, curly quotes, em-dashes, and arrows are UNICODE characters
        that go beyond ASCII. If we try to put them in a PDF with a
        standard font, they either show as blank boxes or crash the library.

        Solution: replace each problematic character with a safe ASCII substitute
        before writing to PDF.

    📌 TEACHING NOTE — The replacements dictionary:
        This is a lookup table: {bad_char: safe_replacement}
        Categories of replacements:
        - Arrows:       → becomes ->  (ASCII arrow)
        - Emojis:       ✅ becomes [+]  ❌ becomes [X]  etc.
        - Bullet chars: • becomes -   ◦ becomes -
        - Punctuation:  " " become "  – — become -  … becomes ...

        The symbols chosen ([+], [X], [!], [>]) are meaningful:
        [+] = positive/good    [X] = wrong/bad
        [!] = warning          [>] = action/suggestion

    📌 TEACHING NOTE — .encode('ascii', 'ignore').decode('ascii'):
        This is a catch-all safety net AFTER the dictionary replacements.
        - .encode('ascii', 'ignore') → converts to ASCII bytes, silently
          DROPPING any characters that can't be represented in ASCII
        - .decode('ascii') → converts bytes back to a string

        Together: "if any non-ASCII character slipped through the dict,
        just remove it rather than crashing."

        This two-step approach (explicit replacements + fallback strip)
        is more robust than either alone.

    Args:
        text: Any string, possibly containing emojis or special characters

    Returns:
        ASCII-safe string ready for PDF rendering
    """
    # Lookup table: Unicode character → ASCII substitute
    replacements = {
        # Arrows
        '→': '->',  '←': '<-',  '↔': '<->',
        # Status emojis
        '✅': '[+]', '❌': '[X]', '⚠️': '[!]',
        '🔴': '[!]', '🟡': '[*]', '🟢': '[o]', '🟠': '[*]',
        # Misc emojis
        '🌟': '[*]', '👍': '[+]', '📝': '[>]', '📊': '[#]',
        '📋': '[#]', '📄': '[#]', '📍': '[#]', '📈': '[^]',
        '📥': '[v]', '🎯': '[*]', '💪': '[+]', '🚨': '[!]',
        '💡': '[i]', '💬': '[>]', '✨': '[*]', '🎁': '[+]', '🔍': '[?]',
        # Bullet variants
        '•': '-',   '◦': '-',
        # Dashes and quotes
        '–': '-',   '—': '-',
        '"': '"',   '"': '"',   "'": "'",
        '…': '...'
    }

    result = text
    # Step 1: Replace known problematic characters with ASCII equivalents
    for unicode_char, ascii_replacement in replacements.items():
        result = result.replace(unicode_char, ascii_replacement)

    # Step 2: Strip any remaining non-ASCII characters (catch-all safety net)
    # encode('ascii', 'ignore') silently drops non-ASCII bytes
    result = result.encode('ascii', 'ignore').decode('ascii')

    return result


# ============================================================
# 📌 TEACHING NOTE — Inheritance in Python (OOP)
#
#   class ATSReportPDF(FPDF):
#       This means ATSReportPDF INHERITS from FPDF.
#
#   FPDF is the base class (from the fpdf2 library).
#   ATSReportPDF is our custom subclass.
#
#   Inheritance gives ATSReportPDF ALL of FPDF's methods automatically:
#   .add_page(), .cell(), .set_font(), .ln() etc.
#
#   We then ADD our own methods:
#   .add_title(), .add_section_header(), .add_bullet_point() etc.
#
#   And we OVERRIDE two special methods:
#   .header() → called automatically at the top of every new page
#   .footer() → called automatically at the bottom of every page
#
#   This is the "Template Method Pattern" — the base class calls
#   header() and footer() for us; we just define what they do.
#
#   Analogy: FPDF is a blank printed form. ATSReportPDF is our
#   customized version with our own header, footer, and helper stamps.
# ============================================================

class ATSReportPDF(FPDF):
    """
    Custom PDF class for ATS resume reports, extending fpdf2's FPDF.

    📌 TEACHING NOTE — Why extend FPDF instead of using it directly?
        Without subclassing:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(59, 130, 246)
            pdf.cell(0, 10, 'Section Header', ...)
            # repeated 30 times across 3 files = messy!

        With our subclass:
            pdf = ATSReportPDF()
            pdf.add_page()
            pdf.add_section_header('Section Header')
            # clean one-liner that encapsulates all the font/color setup

        Subclassing creates a "domain-specific language" for our PDF:
        instead of low-level fpdf2 calls, we have meaningful method names
        like add_section_header() and add_bullet_point().
    """

    def __init__(self):
        """
        Initialize the PDF with auto page breaks enabled.

        📌 TEACHING NOTE — super().__init__():
            super() refers to the PARENT class (FPDF).
            super().__init__() calls FPDF's constructor to set up the
            base PDF object before we add our customizations.

            ALWAYS call super().__init__() in a subclass constructor,
            or the parent class won't be properly initialized.

        📌 TEACHING NOTE — set_auto_page_break(auto=True, margin=15):
            When text reaches 15mm from the bottom of the page,
            fpdf2 automatically starts a new page.
            Without this, text would overflow off the bottom and be cut off.
        """
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """
        Automatically called by fpdf2 at the top of every new page.

        📌 TEACHING NOTE — Method Overriding:
            FPDF has a default header() method that does nothing.
            By defining header() in our subclass, we OVERRIDE it —
            our version runs instead of the empty default.

            fpdf2 calls this automatically — we never call it ourselves.
            This is the "Hollywood Principle": "Don't call us, we'll call you."

        📌 TEACHING NOTE — self.line(10, 20, 200, 20):
            Draws a horizontal line across the page.
            Parameters: (x1, y1, x2, y2) in millimeters.
            The standard A4 page is 210mm wide, so x2=200 goes near the edge.
        """
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)  # Grey color for header

        # Left-aligned report title
        self.cell(0, 10, 'ATS Resume Score Report', align='L')
        # Right-aligned date (new_x='LMARGIN' resets cursor to left margin)
        self.cell(0, 10, datetime.now().strftime('%Y-%m-%d'), align='R',
                  new_x='LMARGIN', new_y='NEXT')

        # Horizontal separator line under the header
        self.line(10, 20, 200, 20)
        self.ln(5)  # 5mm of space after the line

    def footer(self):
        """
        Automatically called by fpdf2 at the bottom of every page.

        📌 TEACHING NOTE — Page numbering with {nb}:
            f'Page {self.page_no()}/{{nb}}'

            self.page_no()  → current page number (known at time of rendering)
            {nb}            → total pages (only known AFTER all pages are added!)

            The double braces {{nb}} create a LITERAL {nb} in the string
            (not an f-string substitution). fpdf2 replaces {nb} with the
            final page count at the very end of PDF generation.
            This is why generator.py calls pdf.alias_nb_pages() first.

        📌 TEACHING NOTE — self.set_y(-15):
            Negative y values count from the BOTTOM of the page.
            set_y(-15) positions the cursor 15mm from the bottom.
            This is how we place the footer at the bottom regardless of page height.
        """
        self.set_y(-15)   # Position 15mm from bottom
        self.set_font('Helvetica', 'I', 8)   # Italic, size 8 (small)
        self.set_text_color(128, 128, 128)   # Grey
        # {nb} is replaced by fpdf2 with total page count at render time
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def add_title(self, title: str):
        """
        Add a large centered title (used once at the top of the report).

        📌 TEACHING NOTE — Font size 24 for titles:
            fpdf2 uses points (pt) for font sizes, same as word processors.
            24pt is approximately equivalent to a Word document H1 heading.
            Hierarchy used in this PDF:
                24pt → main report title (add_title)
                14pt → section headers (add_section_header)
                11pt → subsection headers (add_subsection_header)
                10pt → body text (add_text, add_bullet_point)
        """
        self.set_font('Helvetica', 'B', 24)  # Bold, large
        self.set_text_color(0, 0, 0)         # Black
        self.cell(0, 15, title, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

    def add_section_header(self, title: str):
        """
        Add a blue bold section header (e.g., "Skill Validation Analysis").

        📌 TEACHING NOTE — Color (59, 130, 246):
            fpdf2 colors use RGB format: (Red, Green, Blue), each 0-255.
            (59, 130, 246) is a medium blue — commonly used for headings
            in modern UI design (similar to Tailwind's blue-500).

            Color psychology: blue conveys professionalism and trust,
            which suits a professional resume report.
        """
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(59, 130, 246)  # Blue heading color
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def add_subsection_header(self, title: str):
        """Add a smaller black bold subsection header."""
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 0, 0)  # Black
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')

    def add_text(self, text: str, bold: bool = False):
        """
        Add a paragraph of body text with automatic line wrapping.

        📌 TEACHING NOTE — multi_cell() vs cell():
            cell(width, height, text)       → single line, truncates if too long
            multi_cell(width, height, text) → wraps automatically to next line

            For body text that might be long, multi_cell is essential.
            We calculate available_width to respect left and right margins:
                available_width = page_width - left_margin - right_margin

        📌 TEACHING NOTE — Conditional formatting ('B' if bold else ''):
            Python ternary expression used for font style:
            'B' if bold else '' → 'B' (Bold) or '' (Regular)
            This lets the caller choose bold with: add_text("text", bold=True)

        📌 TEACHING NOTE — sanitize_text_for_pdf() called here:
            Every method that writes text to PDF goes through sanitize first.
            This is a "defense in depth" approach — even if a caller forgets
            to sanitize, our methods handle it automatically.

        Args:
            text: Text to display (may contain emojis — will be sanitized)
            bold: Whether to render in bold (default False)
        """
        self.set_font('Helvetica', 'B' if bold else '', 10)
        self.set_text_color(0, 0, 0)
        self.set_x(self.l_margin)   # Always start from left margin

        # Calculate available width (page width minus both margins)
        available_width = self.w - self.l_margin - self.r_margin

        # Sanitize before writing (replaces emojis with ASCII equivalents)
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, safe_text)  # 6mm line height

    def add_bullet_point(self, text: str, indent: int = 10):
        """
        Add an indented bullet point line.

        📌 TEACHING NOTE — Manual indentation in PDF:
            Unlike HTML/CSS, PDFs have no automatic indentation.
            We create indentation manually:
            1. Calculate current_x = left_margin + indent (e.g., 10+10 = 20mm)
            2. set_x(current_x) moves the cursor to that position
            3. Reduce available_width by the indent so text wraps correctly

            Without adjusting available_width, wrapped lines would extend
            past the right margin.

        📌 TEACHING NOTE — f'- {safe_text}':
            We prepend "- " (hyphen + space) as the bullet character.
            We can't use "•" (Unicode bullet) because it's not ASCII-safe.
            The hyphen is the safe ASCII substitute.

        Args:
            text: Bullet point text (will be sanitized)
            indent: Indentation in mm from left margin (default 10mm)
        """
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)

        # Position cursor at indented position
        current_x = self.l_margin + indent
        self.set_x(current_x)

        # Reduce available width to account for indentation
        available_width = self.w - current_x - self.r_margin

        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, f'- {safe_text}')  # "- " prefix as bullet

    def add_colored_text(self, text: str, color: Tuple[int, int, int]):
        """
        Add bold text in a custom color, then reset color to black.

        📌 TEACHING NOTE — State management in fpdf2:
            fpdf2 uses a "global state" model — set_text_color() affects
            ALL subsequent text until changed again.

            This is a common pattern in graphics/PDF libraries:
            "you set the pen color, then draw, then change color again."

            Notice we reset to black (0,0,0) at the end of this method.
            This is defensive programming — we don't want our color choice
            to accidentally affect text drawn by the NEXT method call.

            This "set → use → reset" pattern is called "bracketing" or
            "save/restore state."

        Args:
            text: Text to display
            color: RGB tuple e.g. (198, 40, 40) for red
        """
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*color)   # *color unpacks (R, G, B) as 3 args
        self.set_x(self.l_margin)
        available_width = self.w - self.l_margin - self.r_margin
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, safe_text)
        self.set_text_color(0, 0, 0)  # Reset to black after colored text


def get_score_color_rgb(score: float) -> Tuple[int, int, int]:
    """
    Convert a 0-100 score into a green/orange/red RGB color.

    📌 TEACHING NOTE — Traffic Light Color System:
        This implements a classic "traffic light" UX pattern:
        🟢 Green  (≥80) → Good/Pass
        🟠 Orange (≥60) → Warning/Average
        🔴 Red    (<60) → Bad/Fail

        The exact RGB values chosen:
        (46, 125, 50)   → Material Design Green 800 (dark enough to read on white)
        (245, 124, 0)   → Material Design Orange 700
        (198, 40, 40)   → Material Design Red 800

        Using a consistent color library (Material Design) ensures the
        colors look professional and have good contrast ratios.

    📌 TEACHING NOTE — Returning a Tuple:
        The function returns THREE values packed as a Tuple[int, int, int].
        Callers unpack it with *color: pdf.set_text_color(*color)
        The * operator unpacks a tuple into positional arguments.

    Args:
        score: Float 0.0 to 100.0

    Returns:
        RGB tuple as (R, G, B) each 0-255
    """
    if score >= 80:
        return 46, 125, 50    # Green — good score
    elif score >= 60:
        return 245, 124, 0    # Orange — average score
    else:
        return 198, 40, 40    # Red — poor score


def get_component_score_color_rgb(score: float, max_score: float) -> Tuple[int, int, int]:
    """
    Get color for a component score that has a custom maximum (not 100).

    📌 TEACHING NOTE — Why this wrapper function?
        Component scores have different maximums:
            Formatting: 20 pts max
            Keywords:   25 pts max
            Content:    25 pts max

        get_score_color_rgb() expects a 0-100 scale.
        This function converts "15 out of 20" → 75% → passes 75.0 to get_score_color_rgb().

        This is a "normalization" step — converting different scales
        to a common 0-100 scale before applying the same color logic.

        Formula: percentage = (score / max_score) × 100
        Guard:   if max_score > 0 (prevent division by zero)

    Args:
        score: Raw component score (e.g., 15.0)
        max_score: Maximum possible for this component (e.g., 20.0)

    Returns:
        RGB color tuple from get_score_color_rgb()
    """
    # Normalize to 0-100 percentage, guard against division by zero
    percentage = (score / max_score * 100) if max_score > 0 else 0
    return get_score_color_rgb(percentage)


def draw_score_bar(
    pdf: ATSReportPDF,
    score: float,
    max_score: float,
    x: float,
    y: float,
    width: float = 100,
    height: float = 8
):
    """
    Draw a colored progress bar showing a score visually.

    📌 TEACHING NOTE — How the progress bar is drawn (3 rectangles):

        Step 1: Draw the BACKGROUND (grey, full width)
            ████████████████████  (grey background, 100mm wide)

        Step 2: Draw the FILLED portion (colored, proportional width)
            ████████░░░░░░░░░░░░  (green fill at 40%, grey shows through)

        Step 3: Draw the BORDER (outline, full width)
            ┌────────────────────┐  (grey border box drawn on top)

        All three are drawn at the exact same (x, y) position.
        Later draws appear ON TOP of earlier ones (painter's algorithm).

    📌 TEACHING NOTE — pdf.rect(x, y, width, height, style='F'):
        style='F' → Fill only (no border)
        style='D' → Draw border only (no fill)
        style='FD' → Fill AND draw border

        We use 'F' for background and fill (no border needed yet),
        then 'D' for the border at the end (draws clean border on top).

    📌 TEACHING NOTE — fill_width calculation:
        fill_width = total_width × (score / max_score)
        e.g., score=15, max=20, width=100mm → fill_width = 75mm
        Guard: if max_score > 0 prevents division by zero.

    📌 TEACHING NOTE — Coordinate system in fpdf2:
        Origin (0,0) is at the TOP-LEFT corner of the page.
        x increases to the right, y increases DOWNWARD.
        All measurements are in millimeters.

    Args:
        pdf: The ATSReportPDF instance to draw on
        score: Current score value
        max_score: Maximum possible score
        x: Left edge of the bar in mm
        y: Top edge of the bar in mm
        width: Total bar width in mm (default 100mm)
        height: Bar height in mm (default 8mm)
    """
    # Calculate what fraction of the bar to fill
    percentage = score / max_score if max_score > 0 else 0
    fill_width = width * percentage   # e.g., 0.75 × 100 = 75mm

    # Step 1: Draw grey background (full width)
    pdf.set_fill_color(224, 224, 224)  # Light grey (RGB)
    pdf.rect(x, y, width, height, style='F')  # style='F' = fill only

    # Step 2: Draw colored fill (proportional to score)
    color = get_component_score_color_rgb(score, max_score)
    pdf.set_fill_color(*color)  # Green, orange, or red based on score
    pdf.rect(x, y, fill_width, height, style='F')

    # Step 3: Draw border outline (on top, full width)
    pdf.set_draw_color(180, 180, 180)  # Medium grey border
    pdf.rect(x, y, width, height, style='D')  # style='D' = draw border only