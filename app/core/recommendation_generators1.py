from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    title: str
    description: str
    priority: Priority
    impact_score: float
    category: str
    action_items: List[str]


from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


def generate_skill_recommendations(skill_validation_results: Dict) ->List[
    Recommendation]:
    recommendations = []
    unvalidated_skills = skill_validation_results.get('unvalidated_skills', [])
    validation_percentage = skill_validation_results.get(
        'validation_percentage', 0.0)
    if not unvalidated_skills:
        return recommendations
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
    action_items = []
    for skill in unvalidated_skills[:5]:
        action_items.append(
            f"Add a project or experience demonstrating '{skill}', or remove it from skills"
            )
    if len(unvalidated_skills) > 5:
        action_items.append(
            f'... and {len(unvalidated_skills) - 5} more unvalidated skill(s)')
    recommendations.append(Recommendation(title=
        'Validate Your Listed Skills', description=
        f"{len(unvalidated_skills)} skill(s) are not demonstrated in your projects or experience. ATS systems and recruiters look for evidence that you've actually used the skills you claim."
        , priority=priority, impact_score=impact, category=
        'skill_validation', action_items=action_items))
    return recommendations


def generate_grammar_recommendations(grammar_results: Dict) ->List[
    Recommendation]:
    recommendations = []
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors = grammar_results.get('minor_errors', [])
    penalty = grammar_results.get('penalty_applied', 0.0)
    total_errors = len(critical_errors) + len(moderate_errors) + len(
        minor_errors)
    if total_errors == 0:
        return recommendations
    if critical_errors:
        action_items = []
        for error in critical_errors[:5]:
            error_text = error.get('error_text', 'unknown')
            suggestions = error.get('suggestions', [])
            suggestion_text = f" → '{suggestions[0]}'" if suggestions else ''
            action_items.append(
                f"Fix '{error_text}'{suggestion_text}: {error.get('message', '')}"
                )
        if len(critical_errors) > 5:
            action_items.append(
                f'... and {len(critical_errors) - 5} more critical error(s)')
        recommendations.append(Recommendation(title=
            'Fix Critical Spelling/Grammar Errors', description=
            f'{len(critical_errors)} critical error(s) found. These are spelling mistakes or major grammar issues that will make your resume look unprofessional.'
            , priority=Priority.CRITICAL, impact_score=min(10.0, len(
            critical_errors) * 2.0), category='grammar', action_items=
            action_items))
    if moderate_errors:
        action_items = []
        for error in moderate_errors[:3]:
            error_text = error.get('error_text', 'unknown')
            suggestions = error.get('suggestions', [])
            suggestion_text = f" → '{suggestions[0]}'" if suggestions else ''
            action_items.append(
                f"Fix '{error_text}'{suggestion_text}: {error.get('message', '')}"
                )
        if len(moderate_errors) > 3:
            action_items.append(
                f'... and {len(moderate_errors) - 3} more moderate error(s)')
        recommendations.append(Recommendation(title=
            'Address Punctuation and Capitalization Issues', description=
            f'{len(moderate_errors)} moderate error(s) found. These are punctuation or capitalization issues that should be corrected.'
            , priority=Priority.HIGH, impact_score=min(6.0, len(
            moderate_errors) * 1.0), category='grammar', action_items=
            action_items))
    if minor_errors and len(minor_errors) >= 3:
        action_items = [
            f'Review {len(minor_errors)} style suggestion(s) for improved readability'
            , 'Consider using consistent formatting throughout']
        recommendations.append(Recommendation(title=
            'Consider Style Improvements', description=
            f'{len(minor_errors)} minor style suggestion(s) found. These are optional improvements for better readability.'
            , priority=Priority.LOW, impact_score=1.0, category='grammar',
            action_items=action_items))
    return recommendations
