from typing import Dict, List


def generate_score_interpretation(overall_score: float) ->str:
    if overall_score >= 90:
        return '🌟 Excellent! Your resume is highly optimized for ATS systems.'
    elif overall_score >= 80:
        return (
            '✅ Great! Your resume should perform well with most ATS systems.')
    elif overall_score >= 70:
        return (
            '👍 Good! Your resume is ATS-friendly with room for minor improvements.'
            )
    elif overall_score >= 60:
        return (
            '⚠️ Fair. Your resume needs some improvements to be fully ATS-compatible.'
            )
    elif overall_score >= 50:
        return (
            '❌ Below Average. Significant improvements needed for ATS compatibility.'
            )
    else:
        return (
            '🔴 Poor. Your resume requires major revisions to pass ATS screening.'
            )


def generate_score_breakdown_messages(formatting_score: float,
    keywords_score: float, content_score: float, skill_validation_score:
    float, ats_compatibility_score: float) ->Dict[str, str]:
    messages = {}
    if formatting_score >= 18:
        messages['formatting'] = 'Excellent structure and organization'
    elif formatting_score >= 15:
        messages['formatting'
            ] = 'Good formatting with minor improvements possible'
    elif formatting_score >= 12:
        messages['formatting'
            ] = 'Adequate formatting, consider adding more structure'
    else:
        messages['formatting'
            ] = 'Needs improvement: add sections and bullet points'
    if keywords_score >= 22:
        messages['keywords'] = 'Excellent keyword optimization'
    elif keywords_score >= 18:
        messages['keywords'] = 'Good keyword presence'
    elif keywords_score >= 14:
        messages['keywords'
            ] = 'Adequate keywords, could add more relevant terms'
    else:
        messages['keywords'] = 'Needs more keywords and skills'
    if content_score >= 22:
        messages['content'
            ] = 'Excellent content quality with strong action verbs'
    elif content_score >= 18:
        messages['content'] = 'Good content with measurable achievements'
    elif content_score >= 14:
        messages['content'] = 'Adequate content, add more quantifiable results'
    else:
        messages['content'] = 'Needs improvement: add action verbs and metrics'
    if skill_validation_score >= 13:
        messages['skill_validation'] = 'Excellent skill validation'
    elif skill_validation_score >= 10:
        messages['skill_validation'] = 'Good skill validation'
    elif skill_validation_score >= 7:
        messages['skill_validation'] = 'Some skills lack supporting evidence'
    else:
        messages['skill_validation'
            ] = 'Many skills are not validated by projects'
    if ats_compatibility_score >= 13:
        messages['ats_compatibility'] = 'Excellent ATS compatibility'
    elif ats_compatibility_score >= 11:
        messages['ats_compatibility'] = 'Good ATS compatibility'
    elif ats_compatibility_score >= 9:
        messages['ats_compatibility'
            ] = 'Adequate ATS compatibility with minor issues'
    else:
        messages['ats_compatibility'] = 'ATS compatibility needs improvement'
    return messages


def generate_strengths(score_results: Dict, skill_validation_results: Dict,
    grammar_results: Dict) ->List[str]:
    strengths = []
    if score_results['formatting_score'] >= 16:
        strengths.append(
            '✅ Well-structured with clear sections and bullet points')
    if score_results['keywords_score'] >= 20:
        strengths.append('✅ Strong keyword optimization and skills presence')
    if score_results['content_score'] >= 20:
        strengths.append(
            '✅ Excellent use of action verbs and quantifiable achievements')
    if score_results['skill_validation_score'] >= 12:
        validation_pct = skill_validation_results.get('validation_percentage',
            0) * 100
        strengths.append(
            f'✅ {validation_pct:.0f}% of skills are validated by projects')
    if score_results['ats_compatibility_score'] >= 13:
        strengths.append('✅ Excellent ATS compatibility with clean formatting')
    if grammar_results.get('total_errors', 0) == 0:
        strengths.append('✅ Error-free grammar and spelling')
    if not strengths:
        strengths.append(
            'Your resume has potential - focus on the recommendations below')
    return strengths


def generate_critical_issues(score_results: Dict, grammar_results: Dict,
    location_results: Dict) ->List[str]:
    issues = []
    critical_errors = len(grammar_results.get('critical_errors', []))
    if critical_errors > 0:
        issues.append(
            f'🔴 {critical_errors} critical grammar/spelling error(s) detected')
    if location_results.get('privacy_risk') == 'high':
        issues.append(
            '🔴 High privacy risk: Remove detailed location information')
    if score_results['formatting_score'] < 10:
        issues.append('🔴 Poor formatting: Add clear sections and bullet points'
            )
    if score_results['keywords_score'] < 12:
        issues.append('🔴 Insufficient keywords and skills')
    if score_results['skill_validation_score'] < 7:
        issues.append('🔴 Most skills lack supporting evidence in projects')
    return issues


def generate_improvements(score_results: Dict, skill_validation_results: Dict
    ) ->List[str]:
    improvements = []
    if 12 <= score_results['formatting_score'] < 16:
        improvements.append(
            '📝 Add more bullet points and improve section organization')
    if 14 <= score_results['keywords_score'] < 20:
        improvements.append(
            '📝 Include more relevant keywords and technical skills')
    if 14 <= score_results['content_score'] < 20:
        improvements.append(
            '📝 Add more quantifiable achievements and action verbs')
    if 7 <= score_results['skill_validation_score'] < 12:
        unvalidated_count = len(skill_validation_results.get(
            'unvalidated_skills', []))
        improvements.append(
            f'📝 Validate {unvalidated_count} skill(s) by adding relevant project details'
            )
    if 9 <= score_results['ats_compatibility_score'] < 13:
        improvements.append(
            '📝 Simplify formatting for better ATS compatibility')
    return improvements
