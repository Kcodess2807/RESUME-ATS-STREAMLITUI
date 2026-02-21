from typing import Dict, List
from datetime import datetime


def generate_action_items(analysis_results: Dict) ->List[Dict]:
    action_items = []
    grammar_results = analysis_results.get('grammar_results', {})
    for error in grammar_results.get('critical_errors', [])[:3]:
        message = error.get('message', 'Fix grammar error')
        suggestions = error.get('suggestions', [])
        suggestion = f' -> {suggestions[0]}' if suggestions else ''
        action_items.append({'priority': 'critical', 'item':
            f'Fix: {message}{suggestion}', 'category': 'grammar'})
    location_results = analysis_results.get('location_results', {})
    if location_results.get('privacy_risk') == 'high':
        action_items.append({'priority': 'critical', 'item':
            'Remove detailed location information (keep only City, State)',
            'category': 'privacy'})
    elif location_results.get('privacy_risk') == 'medium':
        action_items.append({'priority': 'high', 'item':
            'Simplify location information in resume', 'category': 'privacy'})
    skill_validation = analysis_results.get('skill_validation', {})
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    for skill in unvalidated_skills[:3]:
        action_items.append({'priority': 'high', 'item':
            f'Add project evidence for skill: {skill}', 'category': 'skills'})
    jd_comparison = analysis_results.get('jd_comparison', {})
    if jd_comparison:
        for kw in jd_comparison.get('missing_keywords', [])[:5]:
            action_items.append({'priority': 'medium', 'item':
                f'Add keyword to resume: {kw}', 'category': 'keywords'})
        for skill in jd_comparison.get('skills_gap', [])[:3]:
            action_items.append({'priority': 'medium', 'item':
                f'Consider adding skill: {skill}', 'category': 'skills'})
    for error in grammar_results.get('moderate_errors', [])[:2]:
        message = error.get('message', 'Fix punctuation/capitalization')
        action_items.append({'priority': 'medium', 'item':
            f'Fix: {message}', 'category': 'grammar'})
    scores = analysis_results.get('scores', {})
    if scores.get('formatting_score', 20) < 12:
        action_items.append({'priority': 'high', 'item':
            'Add clear section headers (Experience, Education, Skills)',
            'category': 'formatting'})
        action_items.append({'priority': 'high', 'item':
            'Use bullet points for achievements and responsibilities',
            'category': 'formatting'})
    elif scores.get('formatting_score', 20) < 16:
        action_items.append({'priority': 'medium', 'item':
            'Improve section organization and add more bullet points',
            'category': 'formatting'})
    if scores.get('content_score', 25) < 15:
        action_items.append({'priority': 'high', 'item':
            'Add quantifiable achievements (numbers, percentages, metrics)',
            'category': 'content'})
        action_items.append({'priority': 'high', 'item':
            'Start bullet points with strong action verbs', 'category':
            'content'})
    elif scores.get('content_score', 25) < 20:
        action_items.append({'priority': 'medium', 'item':
            'Add more quantifiable results to your experience', 'category':
            'content'})
    for error in grammar_results.get('minor_errors', [])[:2]:
        message = error.get('message', 'Style improvement')
        action_items.append({'priority': 'low', 'item':
            f'Consider: {message}', 'category': 'grammar'})
    return action_items


def generate_action_items_checklist(analysis_results: Dict) ->str:
    action_items = generate_action_items(analysis_results)
    if not action_items:
        return 'ATS Resume Action Items Checklist\n' + '=' * 35 + """

No action items needed. Your resume is well-optimized!"""
    lines = ['ATS Resume Action Items Checklist', '=' * 35, '',
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", '']
    priority_order = ['critical', 'high', 'medium', 'low']
    priority_labels = {'critical': 'CRITICAL PRIORITY', 'high':
        'HIGH PRIORITY', 'medium': 'MEDIUM PRIORITY', 'low': 'LOW PRIORITY'}
    for priority in priority_order:
        items = [item for item in action_items if item['priority'] == priority]
        if items:
            lines.append(f'\n{priority_labels[priority]}')
            lines.append('-' * len(priority_labels[priority]))
            for item in items:
                lines.append(f"[ ] {item['item']}")
    lines.append('\n' + '=' * 35)
    lines.append('Track your progress by checking off completed items.')
    return '\n'.join(lines)
