from typing import Dict
from app.core.generator_utils import ATSReportPDF, sanitize_text_for_pdf, draw_score_bar, get_component_score_color_rgb, get_score_color_rgb


def _add_overall_score_section(pdf: ATSReportPDF, scores: Dict):
    pdf.add_section_header('Overall ATS Score')
    overall_score = scores.get('overall_score', 0)
    interpretation = scores.get('overall_interpretation', '')
    color = get_score_color_rgb(overall_score)
    pdf.set_font('Helvetica', 'B', 48)
    pdf.set_text_color(*color)
    pdf.cell(0, 25, f'{overall_score:.0f}/100', align='C', new_x='LMARGIN',
        new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(100, 100, 100)
    clean_interpretation = interpretation.replace('🌟', '').replace('✅', ''
        ).replace('👍', '')
    clean_interpretation = clean_interpretation.replace('⚠️', '').replace('❌',
        '').replace('🔴', '').strip()
    pdf.cell(0, 10, clean_interpretation, align='C', new_x='LMARGIN', new_y
        ='NEXT')
    bonuses = scores.get('bonuses', {})
    penalties = scores.get('penalties', {})
    if bonuses or penalties:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 9)
        if bonuses:
            bonus_text = ', '.join([f"+{v:.0f} ({k.replace('_', ' ')})" for
                k, v in bonuses.items()])
            pdf.set_text_color(46, 125, 50)
            pdf.cell(0, 6, f'Bonuses: {bonus_text}', align='C', new_x=
                'LMARGIN', new_y='NEXT')
        if penalties:
            penalty_text = ', '.join([f"-{v:.0f} ({k.replace('_', ' ')})" for
                k, v in penalties.items()])
            pdf.set_text_color(198, 40, 40)
            pdf.cell(0, 6, f'Penalties: {penalty_text}', align='C', new_x=
                'LMARGIN', new_y='NEXT')
    pdf.ln(10)


def _add_score_breakdown_section(pdf: ATSReportPDF, scores: Dict):
    pdf.add_section_header('Score Breakdown')
    components = [('Formatting', 'formatting_score', 20), (
        'Keywords & Skills', 'keywords_score', 25), ('Content Quality',
        'content_score', 25), ('Skill Validation', 'skill_validation_score',
        15), ('ATS Compatibility', 'ats_compatibility_score', 15)]
    component_messages = scores.get('component_messages', {})
    for name, key, max_score in components:
        score = scores.get(key, 0)
        message_key = key.replace('_score', '')
        message = component_messages.get(message_key, '')
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(60, 8, name)
        current_x = pdf.get_x()
        current_y = pdf.get_y()
        draw_score_bar(pdf, score, max_score, current_x, current_y + 1,
            width=80, height=6)
        pdf.set_x(current_x + 85)
        color = get_component_score_color_rgb(score, max_score)
        pdf.set_text_color(*color)
        pdf.cell(20, 8, f'{score:.0f}/{max_score}')
        pdf.ln(8)
        if message:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(100, 100, 100)
            pdf.set_x(15)
            pdf.cell(0, 5, message, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(3)
    pdf.ln(5)


def _add_strengths_section(pdf: ATSReportPDF, analysis_results: Dict):
    strengths = analysis_results.get('strengths', [])
    if not strengths:
        return
    pdf.add_section_header('Strengths')
    pdf.set_text_color(46, 125, 50)
    for strength in strengths:
        clean_strength = strength.replace('✅', '[+]').replace('🌟', '[*]')
        pdf.add_bullet_point(clean_strength)
    pdf.ln(5)


def _add_critical_issues_section(pdf: ATSReportPDF, analysis_results: Dict):
    critical_issues = analysis_results.get('critical_issues', [])
    if not critical_issues:
        pdf.add_section_header('Critical Issues')
        pdf.set_text_color(46, 125, 50)
        pdf.add_text('No critical issues found! Your resume is in good shape.')
        pdf.ln(5)
        return
    pdf.add_section_header('Critical Issues')
    pdf.set_text_color(198, 40, 40)
    for issue in critical_issues:
        clean_issue = issue.replace('🔴', '[!]').replace('❌', '[X]')
        pdf.add_bullet_point(clean_issue)
    pdf.ln(5)


def _add_improvements_section(pdf: ATSReportPDF, analysis_results: Dict):
    improvements = analysis_results.get('improvements', [])
    if not improvements:
        return
    pdf.add_section_header('Areas for Improvement')
    pdf.set_text_color(245, 124, 0)
    for improvement in improvements:
        clean_improvement = improvement.replace('📝', '[>]')
        pdf.add_bullet_point(clean_improvement)
    pdf.ln(5)
