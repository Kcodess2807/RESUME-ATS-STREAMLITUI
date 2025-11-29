"""
Recommendation Generator Module for ATS Resume Scorer

This module generates actionable recommendations based on analysis results.
Implements recommendation generation for unvalidated skills, grammar errors,
location privacy issues, missing keywords, and formatting issues.
Recommendations are prioritized by their impact on the overall score.

Validates:
- Requirements 12.1: Generate recommendations for unvalidated skills
- Requirements 12.2: Generate recommendations for grammar errors
- Requirements 12.3: Generate recommendations for location privacy issues
- Requirements 12.4: Generate recommendations for missing keywords
- Requirements 12.5: Generate recommendations for formatting issues
- Requirements 12.6: Prioritize recommendations by impact
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    """Represents a single recommendation."""
    title: str
    description: str
    priority: Priority
    impact_score: float  # Estimated impact on overall score (0-10)
    category: str  # skill_validation, grammar, location, keywords, formatting
    action_items: List[str]  # Specific actions to take


def generate_skill_recommendations(
    skill_validation_results: Dict
) -> List[Recommendation]:
    """
    Generate recommendations for unvalidated skills.
    
    Args:
        skill_validation_results: Results from skill validation containing:
            - validated_skills: List of validated skill dicts
            - unvalidated_skills: List of unvalidated skill names
            - validation_percentage: Percentage of validated skills
            
    Returns:
        List of Recommendation objects for skill issues
        
    Validates:
        - Requirements 12.1: Generate recommendations to add projects or remove skills
    """
    recommendations = []
    
    unvalidated_skills = skill_validation_results.get('unvalidated_skills', [])
    validation_percentage = skill_validation_results.get('validation_percentage', 0.0)
    
    if not unvalidated_skills:
        return recommendations
    
    # Determine priority based on validation percentage
    if validation_percentage < 0.4:
        priority = Priority.CRITICAL
        impact = 8.0
    elif validation_percentage < 0.6:
        priority = Priority.HIGH
        impact = 6.0
    elif validation_percentage < 0.8:
        priority = Priority.MEDIUM
        impact = 4.0
    else:
        priority = Priority.LOW
        impact = 2.0
    
    # Generate main recommendation
    action_items = []
    for skill in unvalidated_skills[:5]:  # Top 5 unvalidated skills
        action_items.append(
            f"Add a project or experience demonstrating '{skill}', or remove it from skills"
        )
    
    if len(unvalidated_skills) > 5:
        action_items.append(
            f"... and {len(unvalidated_skills) - 5} more unvalidated skill(s)"
        )
    
    recommendations.append(Recommendation(
        title="Validate Your Listed Skills",
        description=(
            f"{len(unvalidated_skills)} skill(s) are not demonstrated in your projects or experience. "
            "ATS systems and recruiters look for evidence that you've actually used the skills you claim."
        ),
        priority=priority,
        impact_score=impact,
        category="skill_validation",
        action_items=action_items
    ))
    
    return recommendations



def generate_grammar_recommendations(
    grammar_results: Dict
) -> List[Recommendation]:
    """
    Generate recommendations for grammar and spelling errors.
    
    Args:
        grammar_results: Results from grammar checking containing:
            - critical_errors: List of critical error dicts
            - moderate_errors: List of moderate error dicts
            - minor_errors: List of minor error dicts
            - penalty_applied: Total penalty points
            
    Returns:
        List of Recommendation objects for grammar issues
        
    Validates:
        - Requirements 12.2: Generate recommendations with specific corrections
    """
    recommendations = []
    
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors = grammar_results.get('minor_errors', [])
    penalty = grammar_results.get('penalty_applied', 0.0)
    
    total_errors = len(critical_errors) + len(moderate_errors) + len(minor_errors)
    
    if total_errors == 0:
        return recommendations
    
    # Critical errors recommendation
    if critical_errors:
        action_items = []
        for error in critical_errors[:5]:
            error_text = error.get('error_text', 'unknown')
            suggestions = error.get('suggestions', [])
            suggestion_text = f" → '{suggestions[0]}'" if suggestions else ""
            action_items.append(
                f"Fix '{error_text}'{suggestion_text}: {error.get('message', '')}"
            )
        
        if len(critical_errors) > 5:
            action_items.append(f"... and {len(critical_errors) - 5} more critical error(s)")
        
        recommendations.append(Recommendation(
            title="Fix Critical Spelling/Grammar Errors",
            description=(
                f"{len(critical_errors)} critical error(s) found. These are spelling mistakes "
                "or major grammar issues that will make your resume look unprofessional."
            ),
            priority=Priority.CRITICAL,
            impact_score=min(10.0, len(critical_errors) * 2.0),
            category="grammar",
            action_items=action_items
        ))
    
    # Moderate errors recommendation
    if moderate_errors:
        action_items = []
        for error in moderate_errors[:3]:
            error_text = error.get('error_text', 'unknown')
            suggestions = error.get('suggestions', [])
            suggestion_text = f" → '{suggestions[0]}'" if suggestions else ""
            action_items.append(
                f"Fix '{error_text}'{suggestion_text}: {error.get('message', '')}"
            )
        
        if len(moderate_errors) > 3:
            action_items.append(f"... and {len(moderate_errors) - 3} more moderate error(s)")
        
        recommendations.append(Recommendation(
            title="Address Punctuation and Capitalization Issues",
            description=(
                f"{len(moderate_errors)} moderate error(s) found. These are punctuation "
                "or capitalization issues that should be corrected."
            ),
            priority=Priority.HIGH,
            impact_score=min(6.0, len(moderate_errors) * 1.0),
            category="grammar",
            action_items=action_items
        ))
    
    # Minor errors recommendation (only if significant)
    if minor_errors and len(minor_errors) >= 3:
        action_items = [
            f"Review {len(minor_errors)} style suggestion(s) for improved readability",
            "Consider using consistent formatting throughout"
        ]
        
        recommendations.append(Recommendation(
            title="Consider Style Improvements",
            description=(
                f"{len(minor_errors)} minor style suggestion(s) found. "
                "These are optional improvements for better readability."
            ),
            priority=Priority.LOW,
            impact_score=1.0,
            category="grammar",
            action_items=action_items
        ))
    
    return recommendations


def generate_location_recommendations(
    location_results: Dict
) -> List[Recommendation]:
    """
    Generate recommendations for location privacy issues.
    
    Args:
        location_results: Results from location detection containing:
            - detected_locations: List of detected location dicts
            - privacy_risk: Risk level (high, medium, low, none)
            - penalty_applied: Penalty points applied
            
    Returns:
        List of Recommendation objects for location privacy issues
        
    Validates:
        - Requirements 12.3: Generate recommendations to simplify or remove location info
    """
    recommendations = []
    
    detected_locations = location_results.get('detected_locations', [])
    privacy_risk = location_results.get('privacy_risk', 'none')
    penalty = location_results.get('penalty_applied', 0.0)
    
    if privacy_risk == 'none' or not detected_locations:
        return recommendations
    
    # Categorize locations by type
    addresses = [loc for loc in detected_locations if loc.get('type') == 'address']
    zip_codes = [loc for loc in detected_locations if loc.get('type') == 'zip']
    other_locations = [loc for loc in detected_locations 
                       if loc.get('type') not in ['address', 'zip']]
    
    action_items = []
    
    # Address removal
    if addresses:
        for addr in addresses[:2]:
            action_items.append(
                f"Remove full address: '{addr.get('text', '')}'"
            )
    
    # Zip code removal
    if zip_codes:
        for zip_code in zip_codes[:2]:
            action_items.append(
                f"Remove zip code: '{zip_code.get('text', '')}'"
            )
    
    # General recommendation
    action_items.append("Keep only 'City, State' in your contact header")
    
    # Determine priority based on risk level
    if privacy_risk == 'high':
        priority = Priority.CRITICAL
        impact = 5.0
        description = (
            "Your resume contains detailed location information that poses a privacy risk. "
            "Full addresses and zip codes are unnecessary and can be used to identify your location."
        )
    elif privacy_risk == 'medium':
        priority = Priority.HIGH
        impact = 3.0
        description = (
            "Your resume contains multiple location mentions. "
            "Consider simplifying to just 'City, State' in your contact header."
        )
    else:  # low
        priority = Priority.MEDIUM
        impact = 2.0
        description = (
            "Minor location information detected. "
            "Consider reviewing for unnecessary location details."
        )
    
    recommendations.append(Recommendation(
        title="Protect Your Location Privacy",
        description=description,
        priority=priority,
        impact_score=impact,
        category="location",
        action_items=action_items
    ))
    
    return recommendations



def generate_keyword_recommendations(
    keyword_analysis: Optional[Dict] = None,
    resume_keywords: Optional[List[str]] = None
) -> List[Recommendation]:
    """
    Generate recommendations for missing keywords.
    
    Args:
        keyword_analysis: Results from JD comparison containing:
            - missing_keywords: List of keywords in JD but not in resume
            - skills_gap: List of skills in JD but not in resume
            - match_percentage: Overall match percentage
        resume_keywords: List of keywords extracted from resume (for general analysis)
            
    Returns:
        List of Recommendation objects for keyword issues
        
    Validates:
        - Requirements 12.4: Generate recommendations to add missing keywords
    """
    recommendations = []
    
    # JD-specific recommendations
    if keyword_analysis:
        missing_keywords = keyword_analysis.get('missing_keywords', [])
        skills_gap = keyword_analysis.get('skills_gap', [])
        match_percentage = keyword_analysis.get('match_percentage', 0.0)
        
        # Missing keywords recommendation
        if missing_keywords:
            # Determine priority based on match percentage
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
                    f"Add '{keyword}' to your resume in a relevant section"
                )
            
            if len(missing_keywords) > 7:
                action_items.append(
                    f"... and {len(missing_keywords) - 7} more missing keyword(s)"
                )
            
            recommendations.append(Recommendation(
                title="Add Missing Job Description Keywords",
                description=(
                    f"{len(missing_keywords)} keyword(s) from the job description are missing "
                    f"from your resume. Your current match is {match_percentage:.0f}%."
                ),
                priority=priority,
                impact_score=impact,
                category="keywords",
                action_items=action_items
            ))
        
        # Skills gap recommendation
        if skills_gap:
            action_items = []
            for skill in skills_gap[:5]:
                action_items.append(
                    f"Consider adding '{skill}' if you have this skill"
                )
            
            if len(skills_gap) > 5:
                action_items.append(
                    f"... and {len(skills_gap) - 5} more skill(s) mentioned in the job"
                )
            
            recommendations.append(Recommendation(
                title="Address Skills Gap",
                description=(
                    f"The job description mentions {len(skills_gap)} skill(s) not found in your resume. "
                    "Add these skills if you have them, or consider gaining them."
                ),
                priority=Priority.HIGH,
                impact_score=5.0,
                category="keywords",
                action_items=action_items
            ))
    
    # General keyword recommendations (when no JD provided)
    elif resume_keywords is not None:
        if len(resume_keywords) < 10:
            recommendations.append(Recommendation(
                title="Increase Keyword Density",
                description=(
                    f"Your resume contains only {len(resume_keywords)} keywords. "
                    "Adding more relevant keywords will improve ATS matching."
                ),
                priority=Priority.MEDIUM,
                impact_score=4.0,
                category="keywords",
                action_items=[
                    "Add more technical skills and tools you've used",
                    "Include industry-specific terminology",
                    "Mention relevant certifications and methodologies"
                ]
            ))
    
    return recommendations


def generate_formatting_recommendations(
    score_results: Dict,
    sections: Dict[str, str]
) -> List[Recommendation]:
    """
    Generate recommendations for formatting issues.
    
    Args:
        score_results: Results from scoring containing:
            - formatting_score: Formatting component score (0-20)
        sections: Extracted resume sections
            
    Returns:
        List of Recommendation objects for formatting issues
        
    Validates:
        - Requirements 12.5: Generate recommendations to improve structure and organization
    """
    recommendations = []
    
    formatting_score = score_results.get('formatting_score', 0.0)
    
    # Check for missing sections
    missing_sections = []
    section_recommendations = {
        'experience': "Add a clear 'Experience' or 'Work History' section",
        'education': "Add an 'Education' section with your qualifications",
        'skills': "Add a 'Skills' section listing your technical and soft skills",
        'summary': "Consider adding a 'Summary' or 'Objective' section at the top",
        'projects': "Consider adding a 'Projects' section to showcase your work"
    }
    
    for section_name, recommendation in section_recommendations.items():
        if not sections.get(section_name) or len(sections.get(section_name, '')) < 20:
            missing_sections.append((section_name, recommendation))
    
    # Missing sections recommendation
    if missing_sections:
        # Core sections are critical
        core_missing = [s for s in missing_sections if s[0] in ['experience', 'education', 'skills']]
        optional_missing = [s for s in missing_sections if s[0] in ['summary', 'projects']]
        
        if core_missing:
            action_items = [rec for _, rec in core_missing]
            
            recommendations.append(Recommendation(
                title="Add Missing Core Sections",
                description=(
                    f"Your resume is missing {len(core_missing)} essential section(s). "
                    "ATS systems expect standard resume sections."
                ),
                priority=Priority.CRITICAL,
                impact_score=7.0,
                category="formatting",
                action_items=action_items
            ))
        
        if optional_missing and formatting_score < 15:
            action_items = [rec for _, rec in optional_missing]
            
            recommendations.append(Recommendation(
                title="Consider Adding Optional Sections",
                description=(
                    "Adding a summary and projects section can strengthen your resume."
                ),
                priority=Priority.LOW,
                impact_score=2.0,
                category="formatting",
                action_items=action_items
            ))
    
    # Low formatting score recommendations
    if formatting_score < 12:
        recommendations.append(Recommendation(
            title="Improve Resume Structure",
            description=(
                f"Your formatting score is {formatting_score:.1f}/20. "
                "Better structure will improve ATS parsing and readability."
            ),
            priority=Priority.HIGH,
            impact_score=5.0,
            category="formatting",
            action_items=[
                "Use bullet points to list achievements and responsibilities",
                "Add clear section headers (Experience, Education, Skills)",
                "Ensure consistent formatting throughout",
                "Use a clean, single-column layout"
            ]
        ))
    
    return recommendations



def prioritize_recommendations(
    recommendations: List[Recommendation]
) -> List[Recommendation]:
    """
    Sort recommendations by priority and impact score.
    
    Args:
        recommendations: List of Recommendation objects
        
    Returns:
        Sorted list with highest priority/impact first
        
    Validates:
        - Requirements 12.6: Prioritize recommendations by impact on overall score
    """
    # Priority order mapping
    priority_order = {
        Priority.CRITICAL: 0,
        Priority.HIGH: 1,
        Priority.MEDIUM: 2,
        Priority.LOW: 3
    }
    
    # Sort by priority first, then by impact score (descending)
    sorted_recommendations = sorted(
        recommendations,
        key=lambda r: (priority_order[r.priority], -r.impact_score)
    )
    
    return sorted_recommendations


def generate_all_recommendations(
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    score_results: Dict,
    sections: Dict[str, str],
    keyword_analysis: Optional[Dict] = None,
    resume_keywords: Optional[List[str]] = None
) -> Dict:
    """
    Generate all recommendations from analysis results and prioritize them.
    
    Args:
        skill_validation_results: Results from skill validation
        grammar_results: Results from grammar checking
        location_results: Results from location detection
        score_results: Results from scoring engine
        sections: Extracted resume sections
        keyword_analysis: Optional results from JD comparison
        resume_keywords: Optional list of resume keywords
        
    Returns:
        Dictionary containing:
        {
            'all_recommendations': List[Recommendation],
            'critical_recommendations': List[Recommendation],
            'high_recommendations': List[Recommendation],
            'medium_recommendations': List[Recommendation],
            'low_recommendations': List[Recommendation],
            'total_count': int,
            'estimated_improvement': float
        }
        
    Validates:
        - Requirements 12.1, 12.2, 12.3, 12.4, 12.5: Generate all recommendation types
        - Requirements 12.6: Prioritize by impact
    """
    all_recommendations = []
    
    # Generate recommendations from each category
    all_recommendations.extend(generate_skill_recommendations(skill_validation_results))
    all_recommendations.extend(generate_grammar_recommendations(grammar_results))
    all_recommendations.extend(generate_location_recommendations(location_results))
    all_recommendations.extend(generate_keyword_recommendations(keyword_analysis, resume_keywords))
    all_recommendations.extend(generate_formatting_recommendations(score_results, sections))
    
    # Prioritize all recommendations
    prioritized = prioritize_recommendations(all_recommendations)
    
    # Categorize by priority
    critical = [r for r in prioritized if r.priority == Priority.CRITICAL]
    high = [r for r in prioritized if r.priority == Priority.HIGH]
    medium = [r for r in prioritized if r.priority == Priority.MEDIUM]
    low = [r for r in prioritized if r.priority == Priority.LOW]
    
    # Calculate estimated improvement if all recommendations are followed
    estimated_improvement = sum(r.impact_score for r in prioritized)
    # Cap at reasonable maximum
    estimated_improvement = min(estimated_improvement, 30.0)
    
    return {
        'all_recommendations': prioritized,
        'critical_recommendations': critical,
        'high_recommendations': high,
        'medium_recommendations': medium,
        'low_recommendations': low,
        'total_count': len(prioritized),
        'estimated_improvement': estimated_improvement
    }


def format_recommendation_for_display(recommendation: Recommendation) -> Dict:
    """
    Format a recommendation for UI display.
    
    Args:
        recommendation: Recommendation object
        
    Returns:
        Dictionary with formatted display data
    """
    priority_colors = {
        Priority.CRITICAL: "🔴",
        Priority.HIGH: "🟠",
        Priority.MEDIUM: "🟡",
        Priority.LOW: "🟢"
    }
    
    priority_labels = {
        Priority.CRITICAL: "Critical",
        Priority.HIGH: "High Priority",
        Priority.MEDIUM: "Medium Priority",
        Priority.LOW: "Low Priority"
    }
    
    return {
        'title': recommendation.title,
        'description': recommendation.description,
        'priority_icon': priority_colors[recommendation.priority],
        'priority_label': priority_labels[recommendation.priority],
        'priority_value': recommendation.priority.value,
        'impact_score': recommendation.impact_score,
        'category': recommendation.category,
        'action_items': recommendation.action_items
    }


def format_all_recommendations_for_display(recommendations_result: Dict) -> List[Dict]:
    """
    Format all recommendations for UI display.
    
    Args:
        recommendations_result: Result from generate_all_recommendations
        
    Returns:
        List of formatted recommendation dictionaries
    """
    formatted = []
    for rec in recommendations_result.get('all_recommendations', []):
        formatted.append(format_recommendation_for_display(rec))
    return formatted


def generate_action_items_list(recommendations_result: Dict) -> List[Dict]:
    """
    Generate a flat list of action items from all recommendations.
    
    Args:
        recommendations_result: Result from generate_all_recommendations
        
    Returns:
        List of action item dictionaries with priority
        
    Validates:
        - Requirements 11.8: Generate prioritized action items
    """
    action_items = []
    
    for rec in recommendations_result.get('all_recommendations', []):
        for item in rec.action_items:
            action_items.append({
                'item': item,
                'priority': rec.priority.value,
                'category': rec.category,
                'parent_title': rec.title
            })
    
    return action_items


def get_recommendation_summary(recommendations_result: Dict) -> str:
    """
    Generate a summary message about recommendations.
    
    Args:
        recommendations_result: Result from generate_all_recommendations
        
    Returns:
        Summary message string
    """
    total = recommendations_result.get('total_count', 0)
    critical = len(recommendations_result.get('critical_recommendations', []))
    high = len(recommendations_result.get('high_recommendations', []))
    improvement = recommendations_result.get('estimated_improvement', 0.0)
    
    if total == 0:
        return "✅ Excellent! No major recommendations. Your resume is well-optimized."
    
    if critical > 0:
        return (
            f"🔴 Found {total} recommendation(s) including {critical} critical issue(s). "
            f"Addressing these could improve your score by up to {improvement:.0f} points."
        )
    elif high > 0:
        return (
            f"🟠 Found {total} recommendation(s) including {high} high-priority item(s). "
            f"Addressing these could improve your score by up to {improvement:.0f} points."
        )
    else:
        return (
            f"🟡 Found {total} recommendation(s) for improvement. "
            f"Addressing these could improve your score by up to {improvement:.0f} points."
        )
