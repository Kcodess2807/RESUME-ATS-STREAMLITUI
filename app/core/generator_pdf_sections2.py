from typing import Dict
from app.core.generator_utils import ATSReportPDF, sanitize_text_for_pdf, get_score_color_rgb


def _add_skill_validation_section(pdf: ATSReportPDF, analysis_results: Dict):
    skill_validation = analysis_results.get('skill_validation', {})
    if not skill_validation:
        return
    pdf.add_section_header('Skill Validation Analysis')
    validated_skills = skill_validation.get('validated_skills', [])
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    validation_percentage = skill_validation.get('validation_percentage', 0)
    total_skills = len(validated_skills) + len(unvalidated_skills)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.add_text(
        f'Total Skills: {total_skills} | Validated: {len(validated_skills)} ({validation_percentage * 100:.0f}%) | Unvalidated: {len(unvalidated_skills)}'
        )
    pdf.ln(3)
    if validated_skills:
        pdf.add_subsection_header('Validated Skills')
        pdf.set_text_color(46, 125, 50)
        for skill_info in validated_skills[:10]:
            skill_name = skill_info.get('skill', 'Unknown')
            projects = skill_info.get('projects', [])
            projects_text = ', '.join(projects[:2]) if projects else 'N/A'
            pdf.add_bullet_point(
                f'{skill_name} - demonstrated in: {projects_text}')
    if unvalidated_skills:
        pdf.ln(3)
        pdf.add_subsection_header('Unvalidated Skills (Need Evidence)')
        pdf.set_text_color(198, 40, 40)
        for skill in unvalidated_skills[:10]:
            pdf.add_bullet_point(
                f'{skill} - not found in projects or experience')
    pdf.ln(5)


def _add_grammar_section(pdf: ATSReportPDF, analysis_results: Dict):
    grammar_results = analysis_results.get('grammar_results', {})
    if not grammar_results:
        return
    pdf.add_section_header('Grammar & Spelling Analysis')
    total_errors = grammar_results.get('total_errors', 0)
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors = grammar_results.get('minor_errors', [])
    penalty = grammar_results.get('penalty_applied', 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.add_text(
        f'Total Errors: {total_errors} | Critical: {len(critical_errors)} | Moderate: {len(moderate_errors)} | Minor: {len(minor_errors)}'
        )
    if penalty > 0:
        pdf.set_text_color(198, 40, 40)
        pdf.add_text(f'Score Penalty: -{penalty:.1f} points')
    pdf.ln(3)
    if critical_errors:
        pdf.add_subsection_header('Critical Errors')
        pdf.set_text_color(198, 40, 40)
        for error in critical_errors[:5]:
            message = error.get('message', 'Unknown error')
            suggestions = error.get('suggestions', [])
            suggestion_text = f' -> {suggestions[0]}' if suggestions else ''
            pdf.add_bullet_point(f'{message}{suggestion_text}')
    if moderate_errors:
        pdf.ln(2)
        pdf.add_subsection_header('Moderate Errors')
        pdf.set_text_color(245, 124, 0)
        for error in moderate_errors[:3]:
            message = error.get('message', 'Unknown error')
            pdf.add_bullet_point(message)
    if total_errors == 0:
        pdf.set_text_color(46, 125, 50)
        pdf.add_text('Excellent! No grammar or spelling errors detected.')
    pdf.ln(5)


def _add_location_section(pdf: ATSReportPDF, analysis_results: Dict):
    location_results = analysis_results.get('location_results', {})
    if not location_results:
        return
    pdf.add_section_header('Privacy & Location Analysis')
    privacy_risk = location_results.get('privacy_risk', 'none')
    detected_locations = location_results.get('detected_locations', [])
    penalty = location_results.get('penalty_applied', 0)
    risk_colors = {'high': (198, 40, 40), 'medium': (245, 124, 0), 'low': (
        46, 125, 50), 'none': (46, 125, 50)}
    color = risk_colors.get(privacy_risk, (0, 0, 0))
    pdf.set_text_color(*color)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.add_text(f'Privacy Risk Level: {privacy_risk.upper()}')
    if penalty > 0:
        pdf.set_text_color(198, 40, 40)
        pdf.add_text(f'Score Penalty: -{penalty:.1f} points')
    if detected_locations:
        pdf.ln(2)
        pdf.add_subsection_header('Detected Locations')
        pdf.set_text_color(0, 0, 0)
        for loc in detected_locations[:5]:
            loc_text = loc.get('text', 'Unknown')
            loc_type = loc.get('type', 'unknown')
            section = loc.get('section', 'unknown')
            pdf.add_bullet_point(f'{loc_text} ({loc_type}) in {section}')
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.add_text(
            "Recommendation: Keep only 'City, State' in your contact header. Remove full addresses and zip codes."
            )
    else:
        pdf.set_text_color(46, 125, 50)
        pdf.add_text('No privacy concerns detected.')
    pdf.ln(5)


def _add_jd_comparison_section(pdf: ATSReportPDF, analysis_results: Dict):
    jd_comparison = analysis_results.get('jd_comparison', {})
    if not jd_comparison:
        return
    pdf.add_page()
    pdf.add_section_header('Job Description Match Analysis')
    match_percentage = jd_comparison.get('match_percentage', 0)
    semantic_similarity = jd_comparison.get('semantic_similarity', 0)
    matched_keywords = jd_comparison.get('matched_keywords', [])
    missing_keywords = jd_comparison.get('missing_keywords', [])
    skills_gap = jd_comparison.get('skills_gap', [])
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, 'Keyword Match:')
    color = get_score_color_rgb(match_percentage)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f'{match_percentage:.0f}%', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, 'Semantic Similarity:')
    sim_percentage = semantic_similarity * 100
    color = get_score_color_rgb(sim_percentage)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f'{sim_percentage:.0f}%', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    if matched_keywords:
        pdf.add_subsection_header(f'Matched Keywords ({len(matched_keywords)})'
            )
        pdf.set_text_color(46, 125, 50)
        keywords_text = ', '.join(matched_keywords[:20])
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 6, keywords_text)
        pdf.ln(3)
    if missing_keywords:
        pdf.add_subsection_header(f'Missing Keywords ({len(missing_keywords)})'
            )
        pdf.set_text_color(198, 40, 40)
        for kw in missing_keywords[:15]:
            pdf.add_bullet_point(f"Add '{kw}' to your resume")
        pdf.ln(3)
    if skills_gap:
        pdf.add_subsection_header(f'Skills Gap ({len(skills_gap)})')
        pdf.set_text_color(245, 124, 0)
        for skill in skills_gap[:10]:
            pdf.add_bullet_point(f'Consider adding: {skill}')
    pdf.ln(5)
