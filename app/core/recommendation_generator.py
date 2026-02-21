from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from app.core.recommendation_generators1 import (generate_skill_recommendations,
    generate_grammar_recommendations, Priority, Recommendation)
from app.core.recommendation_generators2 import generate_location_recommendations, generate_keyword_recommendations, generate_formatting_recommendations


def prioritize_recommendations(recommendations: List[Recommendation]) ->List[
    Recommendation]:
    priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.
        MEDIUM: 2, Priority.LOW: 3}
    sorted_recommendations = sorted(recommendations, key=lambda r: (
        priority_order[r.priority], -r.impact_score))
    return sorted_recommendations


def generate_all_recommendations(skill_validation_results: Dict,
    grammar_results: Dict, location_results: Dict, score_results: Dict,
    sections: Dict[str, str], keyword_analysis: Optional[Dict]=None,
    resume_keywords: Optional[List[str]]=None) ->Dict:
    all_recommendations = []
    all_recommendations.extend(generate_skill_recommendations(
        skill_validation_results))
    all_recommendations.extend(generate_grammar_recommendations(
        grammar_results))
    all_recommendations.extend(generate_location_recommendations(
        location_results))
    all_recommendations.extend(generate_keyword_recommendations(
        keyword_analysis, resume_keywords))
    all_recommendations.extend(generate_formatting_recommendations(
        score_results, sections))
    prioritized = prioritize_recommendations(all_recommendations)
    critical = [r for r in prioritized if r.priority == Priority.CRITICAL]
    high = [r for r in prioritized if r.priority == Priority.HIGH]
    medium = [r for r in prioritized if r.priority == Priority.MEDIUM]
    low = [r for r in prioritized if r.priority == Priority.LOW]
    estimated_improvement = sum(r.impact_score for r in prioritized)
    estimated_improvement = min(estimated_improvement, 30.0)
    return {'all_recommendations': prioritized, 'critical_recommendations':
        critical, 'high_recommendations': high, 'medium_recommendations':
        medium, 'low_recommendations': low, 'total_count': len(prioritized),
        'estimated_improvement': estimated_improvement}


def format_recommendation_for_display(recommendation: Recommendation) ->Dict:
    priority_colors = {Priority.CRITICAL: '🔴', Priority.HIGH: '🟠', Priority
        .MEDIUM: '🟡', Priority.LOW: '🟢'}
    priority_labels = {Priority.CRITICAL: 'Critical', Priority.HIGH:
        'High Priority', Priority.MEDIUM: 'Medium Priority', Priority.LOW:
        'Low Priority'}
    return {'title': recommendation.title, 'description': recommendation.
        description, 'priority_icon': priority_colors[recommendation.
        priority], 'priority_label': priority_labels[recommendation.
        priority], 'priority_value': recommendation.priority.value,
        'impact_score': recommendation.impact_score, 'category':
        recommendation.category, 'action_items': recommendation.action_items}


def format_all_recommendations_for_display(recommendations_result: Dict
    ) ->List[Dict]:
    formatted = []
    for rec in recommendations_result.get('all_recommendations', []):
        formatted.append(format_recommendation_for_display(rec))
    return formatted


def generate_action_items_list(recommendations_result: Dict) ->List[Dict]:
    action_items = []
    for rec in recommendations_result.get('all_recommendations', []):
        for item in rec.action_items:
            action_items.append({'item': item, 'priority': rec.priority.
                value, 'category': rec.category, 'parent_title': rec.title})
    return action_items


def get_recommendation_summary(recommendations_result: Dict) ->str:
    total = recommendations_result.get('total_count', 0)
    critical = len(recommendations_result.get('critical_recommendations', []))
    high = len(recommendations_result.get('high_recommendations', []))
    improvement = recommendations_result.get('estimated_improvement', 0.0)
    if total == 0:
        return (
            '✅ Excellent! No major recommendations. Your resume is well-optimized.'
            )
    if critical > 0:
        return (
            f'🔴 Found {total} recommendation(s) including {critical} critical issue(s). Addressing these could improve your score by up to {improvement:.0f} points.'
            )
    elif high > 0:
        return (
            f'🟠 Found {total} recommendation(s) including {high} high-priority item(s). Addressing these could improve your score by up to {improvement:.0f} points.'
            )
    else:
        return (
            f'🟡 Found {total} recommendation(s) for improvement. Addressing these could improve your score by up to {improvement:.0f} points.'
            )
