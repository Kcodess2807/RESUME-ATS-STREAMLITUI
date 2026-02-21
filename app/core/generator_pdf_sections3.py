from typing import Dict
from app.core.generator_utils import ATSReportPDF, sanitize_text_for_pdf
from app.core.generator_actions import generate_action_items


def _add_recommendations_section(pdf: ATSReportPDF, analysis_results: Dict):
    try:
        from app.core.recommendation_generator import generate_all_recommendations, format_all_recommendations_for_display
        recommendations_result = generate_all_recommendations(
            skill_validation_results=analysis_results.get(
            'skill_validation', {}), grammar_results=analysis_results.get(
            'grammar_results', {}), location_results=analysis_results.get(
            'location_results', {}), score_results=analysis_results.get(
            'scores', {}), sections=analysis_results.get('processed_data',
            {}).get('sections', {}), keyword_analysis=analysis_results.get(
            'jd_comparison'), resume_keywords=analysis_results.get(
            'processed_data', {}).get('keywords', []))
        all_recommendations = recommendations_result.get('all_recommendations',
            [])
        if not all_recommendations:
            return
        pdf.add_page()
        pdf.add_section_header('Recommendations')
        estimated_improvement = recommendations_result.get(
            'estimated_improvement', 0)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.add_text(
            f'Following these recommendations could improve your score by up to {estimated_improvement:.0f} points.'
            )
        pdf.ln(5)
        priority_colors = {'critical': (198, 40, 40), 'high': (245, 124, 0),
            'medium': (255, 193, 7), 'low': (46, 125, 50)}
        priority_icons = {'critical': '[!!!]', 'high': '[!!]', 'medium':
            '[!]', 'low': '[i]'}
        for rec in all_recommendations[:10]:
            priority = rec.priority.value
            color = priority_colors.get(priority, (0, 0, 0))
            icon = priority_icons.get(priority, '')
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(*color)
            pdf.add_text(f'{icon} {rec.title}')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.add_text(rec.description)
            pdf.set_text_color(80, 80, 80)
            for action in rec.action_items[:3]:
                pdf.add_bullet_point(action, indent=15)
            pdf.ln(3)
    except ImportError:
        pass
    pdf.ln(5)


def _add_action_items_section(pdf: ATSReportPDF, analysis_results: Dict):
    pdf.add_page()
    pdf.add_section_header('Action Items Checklist')
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.add_text('Use this checklist to track your resume improvements:')
    pdf.ln(5)
    action_items = generate_action_items(analysis_results)
    if not action_items:
        pdf.set_text_color(46, 125, 50)
        pdf.add_text('No action items needed. Your resume is well-optimized!')
        return
    critical_items = [item for item in action_items if item['priority'] ==
        'critical']
    high_items = [item for item in action_items if item['priority'] == 'high']
    medium_items = [item for item in action_items if item['priority'] ==
        'medium']
    low_items = [item for item in action_items if item['priority'] == 'low']
    if critical_items:
        pdf.add_subsection_header('Critical Priority')
        pdf.set_text_color(198, 40, 40)
        for item in critical_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)
    if high_items:
        pdf.add_subsection_header('High Priority')
        pdf.set_text_color(245, 124, 0)
        for item in high_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)
    if medium_items:
        pdf.add_subsection_header('Medium Priority')
        pdf.set_text_color(255, 193, 7)
        for item in medium_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)
    if low_items:
        pdf.add_subsection_header('Low Priority')
        pdf.set_text_color(46, 125, 50)
        for item in low_items[:3]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
