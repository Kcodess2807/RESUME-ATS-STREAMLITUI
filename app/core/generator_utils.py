from typing import Dict, List, Optional, Tuple
from datetime import datetime
import io
import base64
from fpdf import FPDF


def sanitize_text_for_pdf(text: str) ->str:
    replacements = {'→': '->', '←': '<-', '↔': '<->', '✅': '[+]', '❌':
        '[X]', '⚠️': '[!]', '🔴': '[!]', '🟡': '[*]', '🟢': '[o]', '🟠': '[*]',
        '🌟': '[*]', '👍': '[+]', '📝': '[>]', '📊': '[#]', '📋': '[#]', '📄':
        '[#]', '📍': '[#]', '📈': '[^]', '📥': '[v]', '🎯': '[*]', '💪': '[+]',
        '🚨': '[!]', '💡': '[i]', '💬': '[>]', '✨': '[*]', '🎁': '[+]', '🔍':
        '[?]', '•': '-', '◦': '-', '–': '-', '—': '-', '"': '"', '"': '"',
        ': "\'",\n        ': "'", '…': '...'}
    result = text
    for unicode_char, ascii_replacement in replacements.items():
        result = result.replace(unicode_char, ascii_replacement)
    result = result.encode('ascii', 'ignore').decode('ascii')
    return result


class ATSReportPDF(FPDF):

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'ATS Resume Score Report', align='L')
        self.cell(0, 10, datetime.now().strftime('%Y-%m-%d'), align='R',
            new_x='LMARGIN', new_y='NEXT')
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def add_title(self, title: str):
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 0, 0)
        self.cell(0, 15, title, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

    def add_section_header(self, title: str):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(59, 130, 246)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def add_subsection_header(self, title: str):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')

    def add_text(self, text: str, bold: bool=False):
        self.set_font('Helvetica', 'B' if bold else '', 10)
        self.set_text_color(0, 0, 0)
        self.set_x(self.l_margin)
        available_width = self.w - self.l_margin - self.r_margin
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, safe_text)

    def add_bullet_point(self, text: str, indent: int=10):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        current_x = self.l_margin + indent
        self.set_x(current_x)
        available_width = self.w - current_x - self.r_margin
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, f'- {safe_text}')

    def add_colored_text(self, text: str, color: Tuple[int, int, int]):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*color)
        self.set_x(self.l_margin)
        available_width = self.w - self.l_margin - self.r_margin
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, safe_text)
        self.set_text_color(0, 0, 0)


def get_score_color_rgb(score: float) ->Tuple[int, int, int]:
    if score >= 80:
        return 46, 125, 50
    elif score >= 60:
        return 245, 124, 0
    else:
        return 198, 40, 40


def get_component_score_color_rgb(score: float, max_score: float) ->Tuple[
    int, int, int]:
    percentage = score / max_score * 100 if max_score > 0 else 0
    return get_score_color_rgb(percentage)


def draw_score_bar(pdf: ATSReportPDF, score: float, max_score: float, x:
    float, y: float, width: float=100, height: float=8):
    percentage = score / max_score if max_score > 0 else 0
    fill_width = width * percentage
    pdf.set_fill_color(224, 224, 224)
    pdf.rect(x, y, width, height, style='F')
    color = get_component_score_color_rgb(score, max_score)
    pdf.set_fill_color(*color)
    pdf.rect(x, y, fill_width, height, style='F')
    pdf.set_draw_color(180, 180, 180)
    pdf.rect(x, y, width, height, style='D')
