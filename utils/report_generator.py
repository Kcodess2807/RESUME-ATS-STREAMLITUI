"""
Report Generator Module for ATS Resume Scorer

This module generates PDF reports and action item checklists from analysis results.
Implements comprehensive PDF report generation with scores, breakdowns, recommendations,
and visualizations.

Requirements:
- 13.1: Generate PDF document containing all scores and analysis results
- 13.2: Include overall score, component breakdowns, and all recommendations
- 13.3: Include visualizations of score distributions and keyword analysis
- 13.4: Generate checklist document with prioritized recommendations
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import io
import base64

from fpdf import FPDF


def sanitize_text_for_pdf(text: str) -> str:
    """
    Sanitize text for PDF output by replacing Unicode characters with ASCII equivalents.
    
    Args:
        text: Input text that may contain Unicode characters
        
    Returns:
        Sanitized text safe for PDF rendering
    """
    replacements = {
        '→': '->',
        '←': '<-',
        '↔': '<->',
        '✅': '[+]',
        '❌': '[X]',
        '⚠️': '[!]',
        '🔴': '[!]',
        '🟡': '[*]',
        '🟢': '[o]',
        '🟠': '[*]',
        '🌟': '[*]',
        '👍': '[+]',
        '📝': '[>]',
        '📊': '[#]',
        '📋': '[#]',
        '📄': '[#]',
        '📍': '[#]',
        '📈': '[^]',
        '📥': '[v]',
        '🎯': '[*]',
        '💪': '[+]',
        '🚨': '[!]',
        '💡': '[i]',
        '💬': '[>]',
        '✨': '[*]',
        '🎁': '[+]',
        '🔍': '[?]',
        '•': '-',
        '◦': '-',
        '–': '-',
        '—': '-',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
    }
    
    result = text
    for unicode_char, ascii_replacement in replacements.items():
        result = result.replace(unicode_char, ascii_replacement)
    
    # Remove any remaining non-ASCII characters
    result = result.encode('ascii', 'ignore').decode('ascii')
    
    return result


class ATSReportPDF(FPDF):
    """Custom PDF class for ATS Resume Score reports."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Add header to each page."""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'ATS Resume Score Report', align='L')
        self.cell(0, 10, datetime.now().strftime('%Y-%m-%d'), align='R', new_x='LMARGIN', new_y='NEXT')
        self.line(10, 20, 200, 20)
        self.ln(5)
        
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
        
    def add_title(self, title: str):
        """Add a main title."""
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 0, 0)
        self.cell(0, 15, title, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)
        
    def add_section_header(self, title: str):
        """Add a section header."""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(59, 130, 246)  # Blue color
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)
        
    def add_subsection_header(self, title: str):
        """Add a subsection header."""
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        
    def add_text(self, text: str, bold: bool = False):
        """Add regular text."""
        self.set_font('Helvetica', 'B' if bold else '', 10)
        self.set_text_color(0, 0, 0)
        # Reset x position to left margin
        self.set_x(self.l_margin)
        # Calculate available width
        available_width = self.w - self.l_margin - self.r_margin
        # Sanitize text for PDF
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, safe_text)
        
    def add_bullet_point(self, text: str, indent: int = 10):
        """Add a bullet point."""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        # Save current x position and set indent
        current_x = self.l_margin + indent
        self.set_x(current_x)
        # Calculate available width
        available_width = self.w - current_x - self.r_margin
        # Sanitize text for PDF and use a simple dash as bullet
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, f"- {safe_text}")
        
    def add_colored_text(self, text: str, color: Tuple[int, int, int]):
        """Add colored text."""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*color)
        # Reset x position to left margin
        self.set_x(self.l_margin)
        # Calculate available width
        available_width = self.w - self.l_margin - self.r_margin
        # Sanitize text for PDF
        safe_text = sanitize_text_for_pdf(text)
        self.multi_cell(available_width, 6, safe_text)
        self.set_text_color(0, 0, 0)


def get_score_color_rgb(score: float) -> Tuple[int, int, int]:
    """
    Get RGB color based on score value.
    
    Args:
        score: Score value (0-100 for overall, varies for components)
        
    Returns:
        Tuple of (R, G, B) values
    """
    if score >= 80:
        return (46, 125, 50)  # Green
    elif score >= 60:
        return (245, 124, 0)  # Orange
    else:
        return (198, 40, 40)  # Red


def get_component_score_color_rgb(score: float, max_score: float) -> Tuple[int, int, int]:
    """
    Get RGB color based on component score percentage.
    
    Args:
        score: Component score value
        max_score: Maximum possible score for this component
        
    Returns:
        Tuple of (R, G, B) values
    """
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    return get_score_color_rgb(percentage)


def draw_score_bar(pdf: ATSReportPDF, score: float, max_score: float, 
                   x: float, y: float, width: float = 100, height: float = 8):
    """
    Draw a score progress bar.
    
    Args:
        pdf: PDF document
        score: Current score
        max_score: Maximum score
        x: X position
        y: Y position
        width: Bar width
        height: Bar height
    """
    percentage = score / max_score if max_score > 0 else 0
    fill_width = width * percentage
    
    # Background bar (gray)
    pdf.set_fill_color(224, 224, 224)
    pdf.rect(x, y, width, height, style='F')
    
    # Filled portion (colored based on score)
    color = get_component_score_color_rgb(score, max_score)
    pdf.set_fill_color(*color)
    pdf.rect(x, y, fill_width, height, style='F')
    
    # Border
    pdf.set_draw_color(180, 180, 180)
    pdf.rect(x, y, width, height, style='D')


def generate_pdf_report(analysis_results: Dict, user_info: Optional[Dict] = None) -> bytes:
    """
    Generate a comprehensive PDF report with all scores and recommendations.
    
    Args:
        analysis_results: Complete analysis results dictionary containing:
            - scores: Score results from scoring engine
            - skill_validation: Skill validation results
            - grammar_results: Grammar check results
            - location_results: Location detection results
            - jd_comparison: Optional JD comparison results
            - strengths: List of strength messages
            - critical_issues: List of critical issues
            - improvements: List of improvement suggestions
            - processed_data: Processed resume data
        user_info: Optional user information dictionary
        
    Returns:
        PDF file as bytes
        
    Validates:
        - Requirements 13.1: Generate PDF document containing all scores and analysis results
        - Requirements 13.2: Include overall score, component breakdowns, and all recommendations
        - Requirements 13.3: Include visualizations of score distributions and keyword analysis
    """
    pdf = ATSReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title
    pdf.add_title("ATS Resume Score Report")
    
    # Generation info
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
             align='C', new_x='LMARGIN', new_y='NEXT')
    if user_info and user_info.get('name'):
        pdf.cell(0, 6, f"User: {user_info['name']}", align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)
    
    scores = analysis_results.get('scores', {})
    
    # Overall Score Section
    _add_overall_score_section(pdf, scores)
    
    # Score Breakdown Section
    _add_score_breakdown_section(pdf, scores)
    
    # Strengths Section
    _add_strengths_section(pdf, analysis_results)
    
    # Critical Issues Section
    _add_critical_issues_section(pdf, analysis_results)
    
    # Areas for Improvement Section
    _add_improvements_section(pdf, analysis_results)
    
    # Skill Validation Section
    _add_skill_validation_section(pdf, analysis_results)
    
    # Grammar Analysis Section
    _add_grammar_section(pdf, analysis_results)
    
    # Location Privacy Section
    _add_location_section(pdf, analysis_results)
    
    # JD Comparison Section (if available)
    if analysis_results.get('jd_comparison'):
        _add_jd_comparison_section(pdf, analysis_results)
    
    # Recommendations Section
    _add_recommendations_section(pdf, analysis_results)
    
    # Action Items Checklist
    _add_action_items_section(pdf, analysis_results)
    
    # Return PDF as bytes
    return bytes(pdf.output())


def _add_overall_score_section(pdf: ATSReportPDF, scores: Dict):
    """Add overall score section to PDF."""
    pdf.add_section_header("Overall ATS Score")
    
    overall_score = scores.get('overall_score', 0)
    interpretation = scores.get('overall_interpretation', '')
    
    # Score display with color
    color = get_score_color_rgb(overall_score)
    pdf.set_font('Helvetica', 'B', 48)
    pdf.set_text_color(*color)
    pdf.cell(0, 25, f"{overall_score:.0f}/100", align='C', new_x='LMARGIN', new_y='NEXT')
    
    # Interpretation
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(100, 100, 100)
    # Remove emoji for PDF compatibility
    clean_interpretation = interpretation.replace('🌟', '').replace('✅', '').replace('👍', '')
    clean_interpretation = clean_interpretation.replace('⚠️', '').replace('❌', '').replace('🔴', '').strip()
    pdf.cell(0, 10, clean_interpretation, align='C', new_x='LMARGIN', new_y='NEXT')
    
    # Bonuses and penalties
    bonuses = scores.get('bonuses', {})
    penalties = scores.get('penalties', {})
    
    if bonuses or penalties:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 9)
        
        if bonuses:
            bonus_text = ", ".join([f"+{v:.0f} ({k.replace('_', ' ')})" for k, v in bonuses.items()])
            pdf.set_text_color(46, 125, 50)
            pdf.cell(0, 6, f"Bonuses: {bonus_text}", align='C', new_x='LMARGIN', new_y='NEXT')
        
        if penalties:
            penalty_text = ", ".join([f"-{v:.0f} ({k.replace('_', ' ')})" for k, v in penalties.items()])
            pdf.set_text_color(198, 40, 40)
            pdf.cell(0, 6, f"Penalties: {penalty_text}", align='C', new_x='LMARGIN', new_y='NEXT')
    
    pdf.ln(10)


def _add_score_breakdown_section(pdf: ATSReportPDF, scores: Dict):
    """Add score breakdown section with visual bars to PDF."""
    pdf.add_section_header("Score Breakdown")
    
    components = [
        ("Formatting", "formatting_score", 20),
        ("Keywords & Skills", "keywords_score", 25),
        ("Content Quality", "content_score", 25),
        ("Skill Validation", "skill_validation_score", 15),
        ("ATS Compatibility", "ats_compatibility_score", 15),
    ]
    
    component_messages = scores.get('component_messages', {})
    
    for name, key, max_score in components:
        score = scores.get(key, 0)
        message_key = key.replace('_score', '')
        message = component_messages.get(message_key, '')
        
        # Component name and score
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(60, 8, name)
        
        # Draw progress bar
        current_x = pdf.get_x()
        current_y = pdf.get_y()
        draw_score_bar(pdf, score, max_score, current_x, current_y + 1, width=80, height=6)
        
        # Score value
        pdf.set_x(current_x + 85)
        color = get_component_score_color_rgb(score, max_score)
        pdf.set_text_color(*color)
        pdf.cell(20, 8, f"{score:.0f}/{max_score}")
        
        pdf.ln(8)
        
        # Message
        if message:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(100, 100, 100)
            pdf.set_x(15)
            pdf.cell(0, 5, message, new_x='LMARGIN', new_y='NEXT')
        
        pdf.ln(3)
    
    pdf.ln(5)


def _add_strengths_section(pdf: ATSReportPDF, analysis_results: Dict):
    """Add strengths section to PDF."""
    strengths = analysis_results.get('strengths', [])
    
    if not strengths:
        return
    
    pdf.add_section_header("Strengths")
    
    pdf.set_text_color(46, 125, 50)  # Green
    for strength in strengths:
        # Clean emoji for PDF
        clean_strength = strength.replace('✅', '[+]').replace('🌟', '[*]')
        pdf.add_bullet_point(clean_strength)
    
    pdf.ln(5)


def _add_critical_issues_section(pdf: ATSReportPDF, analysis_results: Dict):
    """Add critical issues section to PDF."""
    critical_issues = analysis_results.get('critical_issues', [])
    
    if not critical_issues:
        pdf.add_section_header("Critical Issues")
        pdf.set_text_color(46, 125, 50)
        pdf.add_text("No critical issues found! Your resume is in good shape.")
        pdf.ln(5)
        return
    
    pdf.add_section_header("Critical Issues")
    
    pdf.set_text_color(198, 40, 40)  # Red
    for issue in critical_issues:
        # Clean emoji for PDF
        clean_issue = issue.replace('🔴', '[!]').replace('❌', '[X]')
        pdf.add_bullet_point(clean_issue)
    
    pdf.ln(5)


def _add_improvements_section(pdf: ATSReportPDF, analysis_results: Dict):
    """Add areas for improvement section to PDF."""
    improvements = analysis_results.get('improvements', [])
    
    if not improvements:
        return
    
    pdf.add_section_header("Areas for Improvement")
    
    pdf.set_text_color(245, 124, 0)  # Orange
    for improvement in improvements:
        # Clean emoji for PDF
        clean_improvement = improvement.replace('📝', '[>]')
        pdf.add_bullet_point(clean_improvement)
    
    pdf.ln(5)


def _add_skill_validation_section(pdf: ATSReportPDF, analysis_results: Dict):
    """Add skill validation section to PDF."""
    skill_validation = analysis_results.get('skill_validation', {})
    
    if not skill_validation:
        return
    
    pdf.add_section_header("Skill Validation Analysis")
    
    validated_skills = skill_validation.get('validated_skills', [])
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    validation_percentage = skill_validation.get('validation_percentage', 0)
    
    total_skills = len(validated_skills) + len(unvalidated_skills)
    
    # Summary
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.add_text(f"Total Skills: {total_skills} | Validated: {len(validated_skills)} ({validation_percentage*100:.0f}%) | Unvalidated: {len(unvalidated_skills)}")
    pdf.ln(3)
    
    # Validated skills
    if validated_skills:
        pdf.add_subsection_header("Validated Skills")
        pdf.set_text_color(46, 125, 50)
        for skill_info in validated_skills[:10]:  # Limit to 10
            skill_name = skill_info.get('skill', 'Unknown')
            projects = skill_info.get('projects', [])
            projects_text = ", ".join(projects[:2]) if projects else "N/A"
            pdf.add_bullet_point(f"{skill_name} - demonstrated in: {projects_text}")
    
    # Unvalidated skills
    if unvalidated_skills:
        pdf.ln(3)
        pdf.add_subsection_header("Unvalidated Skills (Need Evidence)")
        pdf.set_text_color(198, 40, 40)
        for skill in unvalidated_skills[:10]:  # Limit to 10
            pdf.add_bullet_point(f"{skill} - not found in projects or experience")
    
    pdf.ln(5)


def _add_grammar_section(pdf: ATSReportPDF, analysis_results: Dict):
    """Add grammar analysis section to PDF."""
    grammar_results = analysis_results.get('grammar_results', {})
    
    if not grammar_results:
        return
    
    pdf.add_section_header("Grammar & Spelling Analysis")
    
    total_errors = grammar_results.get('total_errors', 0)
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors = grammar_results.get('minor_errors', [])
    penalty = grammar_results.get('penalty_applied', 0)
    
    # Summary
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.add_text(f"Total Errors: {total_errors} | Critical: {len(critical_errors)} | Moderate: {len(moderate_errors)} | Minor: {len(minor_errors)}")
    
    if penalty > 0:
        pdf.set_text_color(198, 40, 40)
        pdf.add_text(f"Score Penalty: -{penalty:.1f} points")
    
    pdf.ln(3)
    
    # Critical errors
    if critical_errors:
        pdf.add_subsection_header("Critical Errors")
        pdf.set_text_color(198, 40, 40)
        for error in critical_errors[:5]:
            message = error.get('message', 'Unknown error')
            suggestions = error.get('suggestions', [])
            suggestion_text = f" -> {suggestions[0]}" if suggestions else ""
            pdf.add_bullet_point(f"{message}{suggestion_text}")
    
    # Moderate errors
    if moderate_errors:
        pdf.ln(2)
        pdf.add_subsection_header("Moderate Errors")
        pdf.set_text_color(245, 124, 0)
        for error in moderate_errors[:3]:
            message = error.get('message', 'Unknown error')
            pdf.add_bullet_point(message)
    
    if total_errors == 0:
        pdf.set_text_color(46, 125, 50)
        pdf.add_text("Excellent! No grammar or spelling errors detected.")
    
    pdf.ln(5)


def _add_location_section(pdf: ATSReportPDF, analysis_results: Dict):
    """Add location privacy section to PDF."""
    location_results = analysis_results.get('location_results', {})
    
    if not location_results:
        return
    
    pdf.add_section_header("Privacy & Location Analysis")
    
    privacy_risk = location_results.get('privacy_risk', 'none')
    detected_locations = location_results.get('detected_locations', [])
    penalty = location_results.get('penalty_applied', 0)
    
    # Risk level
    risk_colors = {
        'high': (198, 40, 40),
        'medium': (245, 124, 0),
        'low': (46, 125, 50),
        'none': (46, 125, 50)
    }
    
    color = risk_colors.get(privacy_risk, (0, 0, 0))
    pdf.set_text_color(*color)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.add_text(f"Privacy Risk Level: {privacy_risk.upper()}")
    
    if penalty > 0:
        pdf.set_text_color(198, 40, 40)
        pdf.add_text(f"Score Penalty: -{penalty:.1f} points")
    
    # Detected locations
    if detected_locations:
        pdf.ln(2)
        pdf.add_subsection_header("Detected Locations")
        pdf.set_text_color(0, 0, 0)
        for loc in detected_locations[:5]:
            loc_text = loc.get('text', 'Unknown')
            loc_type = loc.get('type', 'unknown')
            section = loc.get('section', 'unknown')
            pdf.add_bullet_point(f"{loc_text} ({loc_type}) in {section}")
        
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.add_text("Recommendation: Keep only 'City, State' in your contact header. Remove full addresses and zip codes.")
    else:
        pdf.set_text_color(46, 125, 50)
        pdf.add_text("No privacy concerns detected.")
    
    pdf.ln(5)


def _add_jd_comparison_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add job description comparison section to PDF.
    
    Requirements: 13.3 - Include visualizations of keyword analysis
    """
    jd_comparison = analysis_results.get('jd_comparison', {})
    
    if not jd_comparison:
        return
    
    pdf.add_page()
    pdf.add_section_header("Job Description Match Analysis")
    
    match_percentage = jd_comparison.get('match_percentage', 0)
    semantic_similarity = jd_comparison.get('semantic_similarity', 0)
    matched_keywords = jd_comparison.get('matched_keywords', [])
    missing_keywords = jd_comparison.get('missing_keywords', [])
    skills_gap = jd_comparison.get('skills_gap', [])
    
    # Match metrics
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, "Keyword Match:")
    
    color = get_score_color_rgb(match_percentage)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f"{match_percentage:.0f}%", new_x='LMARGIN', new_y='NEXT')
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 10, "Semantic Similarity:")
    
    sim_percentage = semantic_similarity * 100
    color = get_score_color_rgb(sim_percentage)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f"{sim_percentage:.0f}%", new_x='LMARGIN', new_y='NEXT')
    
    pdf.ln(5)
    
    # Matched keywords
    if matched_keywords:
        pdf.add_subsection_header(f"Matched Keywords ({len(matched_keywords)})")
        pdf.set_text_color(46, 125, 50)
        keywords_text = ", ".join(matched_keywords[:20])
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 6, keywords_text)
        pdf.ln(3)
    
    # Missing keywords
    if missing_keywords:
        pdf.add_subsection_header(f"Missing Keywords ({len(missing_keywords)})")
        pdf.set_text_color(198, 40, 40)
        for kw in missing_keywords[:15]:
            pdf.add_bullet_point(f"Add '{kw}' to your resume")
        pdf.ln(3)
    
    # Skills gap
    if skills_gap:
        pdf.add_subsection_header(f"Skills Gap ({len(skills_gap)})")
        pdf.set_text_color(245, 124, 0)
        for skill in skills_gap[:10]:
            pdf.add_bullet_point(f"Consider adding: {skill}")
    
    pdf.ln(5)


def _add_recommendations_section(pdf: ATSReportPDF, analysis_results: Dict):
    """Add recommendations section to PDF."""
    # Try to get recommendations from the recommendation generator
    try:
        from utils.recommendation_generator import (
            generate_all_recommendations,
            format_all_recommendations_for_display
        )
        
        recommendations_result = generate_all_recommendations(
            skill_validation_results=analysis_results.get('skill_validation', {}),
            grammar_results=analysis_results.get('grammar_results', {}),
            location_results=analysis_results.get('location_results', {}),
            score_results=analysis_results.get('scores', {}),
            sections=analysis_results.get('processed_data', {}).get('sections', {}),
            keyword_analysis=analysis_results.get('jd_comparison'),
            resume_keywords=analysis_results.get('processed_data', {}).get('keywords', [])
        )
        
        all_recommendations = recommendations_result.get('all_recommendations', [])
        
        if not all_recommendations:
            return
        
        pdf.add_page()
        pdf.add_section_header("Recommendations")
        
        estimated_improvement = recommendations_result.get('estimated_improvement', 0)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.add_text(f"Following these recommendations could improve your score by up to {estimated_improvement:.0f} points.")
        pdf.ln(5)
        
        priority_colors = {
            'critical': (198, 40, 40),
            'high': (245, 124, 0),
            'medium': (255, 193, 7),
            'low': (46, 125, 50)
        }
        
        priority_icons = {
            'critical': '[!!!]',
            'high': '[!!]',
            'medium': '[!]',
            'low': '[i]'
        }
        
        for rec in all_recommendations[:10]:  # Limit to 10 recommendations
            priority = rec.priority.value
            color = priority_colors.get(priority, (0, 0, 0))
            icon = priority_icons.get(priority, '')
            
            # Title with priority
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(*color)
            pdf.add_text(f"{icon} {rec.title}")
            
            # Description
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.add_text(rec.description)
            
            # Action items
            pdf.set_text_color(80, 80, 80)
            for action in rec.action_items[:3]:
                pdf.add_bullet_point(action, indent=15)
            
            pdf.ln(3)
        
    except ImportError:
        # Fallback if recommendation generator not available
        pass
    
    pdf.ln(5)


def _add_action_items_section(pdf: ATSReportPDF, analysis_results: Dict):
    """
    Add action items checklist section to PDF.
    
    Requirements: 13.4 - Generate checklist document with prioritized recommendations
    """
    pdf.add_page()
    pdf.add_section_header("Action Items Checklist")
    
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.add_text("Use this checklist to track your resume improvements:")
    pdf.ln(5)
    
    action_items = generate_action_items(analysis_results)
    
    if not action_items:
        pdf.set_text_color(46, 125, 50)
        pdf.add_text("No action items needed. Your resume is well-optimized!")
        return
    
    # Group by priority
    critical_items = [item for item in action_items if item['priority'] == 'critical']
    high_items = [item for item in action_items if item['priority'] == 'high']
    medium_items = [item for item in action_items if item['priority'] == 'medium']
    low_items = [item for item in action_items if item['priority'] == 'low']
    
    # Critical items
    if critical_items:
        pdf.add_subsection_header("Critical Priority")
        pdf.set_text_color(198, 40, 40)
        for item in critical_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)
    
    # High priority items
    if high_items:
        pdf.add_subsection_header("High Priority")
        pdf.set_text_color(245, 124, 0)
        for item in high_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)
    
    # Medium priority items
    if medium_items:
        pdf.add_subsection_header("Medium Priority")
        pdf.set_text_color(255, 193, 7)
        for item in medium_items[:5]:
            pdf.add_bullet_point(f"[ ] {item['item']}")
        pdf.ln(3)
    
    # Low priority items
    if low_items:
        pdf.add_subsection_header("Low Priority")
        pdf.set_text_color(46, 125, 50)
        for item in low_items[:3]:
            pdf.add_bullet_point(f"[ ] {item['item']}")


def generate_action_items(analysis_results: Dict) -> List[Dict]:
    """
    Generate prioritized action items list from analysis results.
    
    Args:
        analysis_results: Complete analysis results dictionary
        
    Returns:
        List of action item dictionaries with priority, item text, and category
        
    Validates:
        - Requirements 13.4: Generate checklist document with prioritized recommendations
    """
    action_items = []
    
    # Grammar critical errors
    grammar_results = analysis_results.get('grammar_results', {})
    for error in grammar_results.get('critical_errors', [])[:3]:
        message = error.get('message', 'Fix grammar error')
        suggestions = error.get('suggestions', [])
        suggestion = f" -> {suggestions[0]}" if suggestions else ""
        action_items.append({
            'priority': 'critical',
            'item': f"Fix: {message}{suggestion}",
            'category': 'grammar'
        })
    
    # Location privacy issues
    location_results = analysis_results.get('location_results', {})
    if location_results.get('privacy_risk') == 'high':
        action_items.append({
            'priority': 'critical',
            'item': 'Remove detailed location information (keep only City, State)',
            'category': 'privacy'
        })
    elif location_results.get('privacy_risk') == 'medium':
        action_items.append({
            'priority': 'high',
            'item': 'Simplify location information in resume',
            'category': 'privacy'
        })
    
    # Unvalidated skills
    skill_validation = analysis_results.get('skill_validation', {})
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    for skill in unvalidated_skills[:3]:
        action_items.append({
            'priority': 'high',
            'item': f"Add project evidence for skill: {skill}",
            'category': 'skills'
        })
    
    # Missing keywords from JD
    jd_comparison = analysis_results.get('jd_comparison', {})
    if jd_comparison:
        for kw in jd_comparison.get('missing_keywords', [])[:5]:
            action_items.append({
                'priority': 'medium',
                'item': f"Add keyword to resume: {kw}",
                'category': 'keywords'
            })
        
        for skill in jd_comparison.get('skills_gap', [])[:3]:
            action_items.append({
                'priority': 'medium',
                'item': f"Consider adding skill: {skill}",
                'category': 'skills'
            })
    
    # Moderate grammar errors
    for error in grammar_results.get('moderate_errors', [])[:2]:
        message = error.get('message', 'Fix punctuation/capitalization')
        action_items.append({
            'priority': 'medium',
            'item': f"Fix: {message}",
            'category': 'grammar'
        })
    
    # Formatting improvements based on score
    scores = analysis_results.get('scores', {})
    if scores.get('formatting_score', 20) < 12:
        action_items.append({
            'priority': 'high',
            'item': 'Add clear section headers (Experience, Education, Skills)',
            'category': 'formatting'
        })
        action_items.append({
            'priority': 'high',
            'item': 'Use bullet points for achievements and responsibilities',
            'category': 'formatting'
        })
    elif scores.get('formatting_score', 20) < 16:
        action_items.append({
            'priority': 'medium',
            'item': 'Improve section organization and add more bullet points',
            'category': 'formatting'
        })
    
    # Content improvements
    if scores.get('content_score', 25) < 15:
        action_items.append({
            'priority': 'high',
            'item': 'Add quantifiable achievements (numbers, percentages, metrics)',
            'category': 'content'
        })
        action_items.append({
            'priority': 'high',
            'item': 'Start bullet points with strong action verbs',
            'category': 'content'
        })
    elif scores.get('content_score', 25) < 20:
        action_items.append({
            'priority': 'medium',
            'item': 'Add more quantifiable results to your experience',
            'category': 'content'
        })
    
    # Minor grammar errors
    for error in grammar_results.get('minor_errors', [])[:2]:
        message = error.get('message', 'Style improvement')
        action_items.append({
            'priority': 'low',
            'item': f"Consider: {message}",
            'category': 'grammar'
        })
    
    return action_items


def generate_action_items_checklist(analysis_results: Dict) -> str:
    """
    Generate a plain text action items checklist.
    
    Args:
        analysis_results: Complete analysis results dictionary
        
    Returns:
        Plain text checklist string
        
    Validates:
        - Requirements 13.4: Generate checklist document with prioritized recommendations
    """
    action_items = generate_action_items(analysis_results)
    
    if not action_items:
        return "ATS Resume Action Items Checklist\n" + "=" * 35 + "\n\nNo action items needed. Your resume is well-optimized!"
    
    lines = [
        "ATS Resume Action Items Checklist",
        "=" * 35,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ""
    ]
    
    # Group by priority
    priority_order = ['critical', 'high', 'medium', 'low']
    priority_labels = {
        'critical': 'CRITICAL PRIORITY',
        'high': 'HIGH PRIORITY',
        'medium': 'MEDIUM PRIORITY',
        'low': 'LOW PRIORITY'
    }
    
    for priority in priority_order:
        items = [item for item in action_items if item['priority'] == priority]
        if items:
            lines.append(f"\n{priority_labels[priority]}")
            lines.append("-" * len(priority_labels[priority]))
            for item in items:
                lines.append(f"[ ] {item['item']}")
    
    lines.append("\n" + "=" * 35)
    lines.append("Track your progress by checking off completed items.")
    
    return "\n".join(lines)


def get_pdf_download_link(pdf_bytes: bytes, filename: str = "ats_report.pdf") -> str:
    """
    Generate a base64 download link for the PDF.
    
    Args:
        pdf_bytes: PDF file as bytes
        filename: Download filename
        
    Returns:
        Base64 encoded data URI string
    """
    b64 = base64.b64encode(pdf_bytes).decode()
    return f"data:application/pdf;base64,{b64}"


def generate_summary_text(analysis_results: Dict) -> str:
    """
    Generate a plain text summary of the analysis.
    
    Args:
        analysis_results: Complete analysis results dictionary
        
    Returns:
        Plain text summary string
    """
    scores = analysis_results.get('scores', {})
    overall_score = scores.get('overall_score', 0)
    interpretation = scores.get('overall_interpretation', '')
    
    # Clean emoji from interpretation
    clean_interpretation = interpretation
    for emoji in ['🌟', '✅', '👍', '⚠️', '❌', '🔴']:
        clean_interpretation = clean_interpretation.replace(emoji, '')
    clean_interpretation = clean_interpretation.strip()
    
    lines = [
        "ATS Resume Analysis Summary",
        "=" * 30,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Overall Score: {overall_score:.0f}/100",
        clean_interpretation,
        "",
        "Score Breakdown:",
        f"  - Formatting: {scores.get('formatting_score', 0):.0f}/20",
        f"  - Keywords & Skills: {scores.get('keywords_score', 0):.0f}/25",
        f"  - Content Quality: {scores.get('content_score', 0):.0f}/25",
        f"  - Skill Validation: {scores.get('skill_validation_score', 0):.0f}/15",
        f"  - ATS Compatibility: {scores.get('ats_compatibility_score', 0):.0f}/15",
        ""
    ]
    
    # Strengths
    strengths = analysis_results.get('strengths', [])
    if strengths:
        lines.append("Strengths:")
        for strength in strengths:
            clean_strength = strength
            for emoji in ['✅', '🌟']:
                clean_strength = clean_strength.replace(emoji, '[+]')
            lines.append(f"  {clean_strength}")
        lines.append("")
    
    # Critical issues
    critical_issues = analysis_results.get('critical_issues', [])
    if critical_issues:
        lines.append("Critical Issues:")
        for issue in critical_issues:
            clean_issue = issue
            for emoji in ['🔴', '❌']:
                clean_issue = clean_issue.replace(emoji, '[!]')
            lines.append(f"  {clean_issue}")
        lines.append("")
    
    # Improvements
    improvements = analysis_results.get('improvements', [])
    if improvements:
        lines.append("Areas for Improvement:")
        for improvement in improvements:
            clean_improvement = improvement.replace('📝', '[>]')
            lines.append(f"  {clean_improvement}")
        lines.append("")
    
    lines.append("=" * 30)
    lines.append("Generated by ATS Resume Scorer")
    
    return "\n".join(lines)
