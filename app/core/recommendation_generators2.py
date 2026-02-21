from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from app.core.recommendation_generators1 import Priority, Recommendation


def generate_location_recommendations(location_results: Dict) ->List[
    Recommendation]:
    recommendations = []
    detected_locations = location_results.get('detected_locations', [])
    privacy_risk = location_results.get('privacy_risk', 'none')
    penalty = location_results.get('penalty_applied', 0.0)
    if privacy_risk == 'none' or not detected_locations:
        return recommendations
    addresses = [loc for loc in detected_locations if loc.get('type') ==
        'address']
    zip_codes = [loc for loc in detected_locations if loc.get('type') == 'zip']
    other_locations = [loc for loc in detected_locations if loc.get('type')
         not in ['address', 'zip']]
    action_items = []
    if addresses:
        for addr in addresses[:2]:
            action_items.append(
                f"Remove full address: '{addr.get('text', '')}'")
    if zip_codes:
        for zip_code in zip_codes[:2]:
            action_items.append(
                f"Remove zip code: '{zip_code.get('text', '')}'")
    action_items.append("Keep only 'City, State' in your contact header")
    if privacy_risk == 'high':
        priority = Priority.CRITICAL
        impact = 5.0
        description = (
            'Your resume contains detailed location information that poses a privacy risk. Full addresses and zip codes are unnecessary and can be used to identify your location.'
            )
    elif privacy_risk == 'medium':
        priority = Priority.HIGH
        impact = 3.0
        description = (
            "Your resume contains multiple location mentions. Consider simplifying to just 'City, State' in your contact header."
            )
    else:
        priority = Priority.MEDIUM
        impact = 2.0
        description = (
            'Minor location information detected. Consider reviewing for unnecessary location details.'
            )
    recommendations.append(Recommendation(title=
        'Protect Your Location Privacy', description=description, priority=
        priority, impact_score=impact, category='location', action_items=
        action_items))
    return recommendations


def generate_keyword_recommendations(keyword_analysis: Optional[Dict]=None,
    resume_keywords: Optional[List[str]]=None) ->List[Recommendation]:
    recommendations = []
    if keyword_analysis:
        missing_keywords = keyword_analysis.get('missing_keywords', [])
        skills_gap = keyword_analysis.get('skills_gap', [])
        match_percentage = keyword_analysis.get('match_percentage', 0.0)
        if missing_keywords:
            if match_percentage < 40:
                priority = Priority.CRITICAL
                impact = 8.0
            elif match_percentage < 60:
                priority = Priority.HIGH
                impact = 6.0
            else:
                priority = Priority.MEDIUM
                impact = 4.0
            action_items = []
            for keyword in missing_keywords[:7]:
                action_items.append(
                    f"Add '{keyword}' to your resume in a relevant section")
            if len(missing_keywords) > 7:
                action_items.append(
                    f'... and {len(missing_keywords) - 7} more missing keyword(s)'
                    )
            recommendations.append(Recommendation(title=
                'Add Missing Job Description Keywords', description=
                f'{len(missing_keywords)} keyword(s) from the job description are missing from your resume. Your current match is {match_percentage:.0f}%.'
                , priority=priority, impact_score=impact, category=
                'keywords', action_items=action_items))
        if skills_gap:
            action_items = []
            for skill in skills_gap[:5]:
                action_items.append(
                    f"Consider adding '{skill}' if you have this skill")
            if len(skills_gap) > 5:
                action_items.append(
                    f'... and {len(skills_gap) - 5} more skill(s) mentioned in the job'
                    )
            recommendations.append(Recommendation(title=
                'Address Skills Gap', description=
                f'The job description mentions {len(skills_gap)} skill(s) not found in your resume. Add these skills if you have them, or consider gaining them.'
                , priority=Priority.HIGH, impact_score=5.0, category=
                'keywords', action_items=action_items))
    elif resume_keywords is not None:
        if len(resume_keywords) < 10:
            recommendations.append(Recommendation(title=
                'Increase Keyword Density', description=
                f'Your resume contains only {len(resume_keywords)} keywords. Adding more relevant keywords will improve ATS matching.'
                , priority=Priority.MEDIUM, impact_score=4.0, category=
                'keywords', action_items=[
                "Add more technical skills and tools you've used",
                'Include industry-specific terminology',
                'Mention relevant certifications and methodologies']))
    return recommendations


def generate_formatting_recommendations(score_results: Dict, sections: Dict
    [str, str]) ->List[Recommendation]:
    recommendations = []
    formatting_score = score_results.get('formatting_score', 0.0)
    missing_sections = []
    section_recommendations = {'experience':
        "Add a clear 'Experience' or 'Work History' section", 'education':
        "Add an 'Education' section with your qualifications", 'skills':
        "Add a 'Skills' section listing your technical and soft skills",
        'summary':
        "Consider adding a 'Summary' or 'Objective' section at the top",
        'projects':
        "Consider adding a 'Projects' section to showcase your work"}
    for section_name, recommendation in section_recommendations.items():
        if not sections.get(section_name) or len(sections.get(section_name, '')
            ) < 20:
            missing_sections.append((section_name, recommendation))
    if missing_sections:
        core_missing = [s for s in missing_sections if s[0] in [
            'experience', 'education', 'skills']]
        optional_missing = [s for s in missing_sections if s[0] in [
            'summary', 'projects']]
        if core_missing:
            action_items = [rec for _, rec in core_missing]
            recommendations.append(Recommendation(title=
                'Add Missing Core Sections', description=
                f'Your resume is missing {len(core_missing)} essential section(s). ATS systems expect standard resume sections.'
                , priority=Priority.CRITICAL, impact_score=7.0, category=
                'formatting', action_items=action_items))
        if optional_missing and formatting_score < 15:
            action_items = [rec for _, rec in optional_missing]
            recommendations.append(Recommendation(title=
                'Consider Adding Optional Sections', description=
                'Adding a summary and projects section can strengthen your resume.'
                , priority=Priority.LOW, impact_score=2.0, category=
                'formatting', action_items=action_items))
    if formatting_score < 12:
        recommendations.append(Recommendation(title=
            'Improve Resume Structure', description=
            f'Your formatting score is {formatting_score:.1f}/20. Better structure will improve ATS parsing and readability.'
            , priority=Priority.HIGH, impact_score=5.0, category=
            'formatting', action_items=[
            'Use bullet points to list achievements and responsibilities',
            'Add clear section headers (Experience, Education, Skills)',
            'Ensure consistent formatting throughout',
            'Use a clean, single-column layout']))
    return recommendations
