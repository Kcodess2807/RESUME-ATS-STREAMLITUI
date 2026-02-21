import re
from typing import Dict, List, Tuple


def analyze_experience_section(experience_text: str, action_verbs: List[str
    ], full_text: str) ->Dict:
    results = {'score': 0.0, 'max_score': 20.0, 'job_entries': [],
        'metrics': {'total_jobs': 0, 'jobs_with_dates': 0,
        'jobs_with_bullets': 0, 'jobs_with_metrics': 0, 'action_verbs_used':
        0, 'quantified_achievements': 0}, 'feedback': [], 'strengths': [],
        'improvements': []}
    if not experience_text or len(experience_text.strip()) < 50:
        results['feedback'].append(
            '⚠️ Experience section is missing or too short')
        results['improvements'].append(
            'Add detailed work experience with job titles, companies, and dates'
            )
        return results
    job_entries = _parse_job_entries(experience_text)
    results['job_entries'] = job_entries
    results['metrics']['total_jobs'] = len(job_entries)
    for job in job_entries:
        if job.get('has_dates'):
            results['metrics']['jobs_with_dates'] += 1
        if job.get('bullet_count', 0) > 0:
            results['metrics']['jobs_with_bullets'] += 1
        if job.get('has_metrics'):
            results['metrics']['jobs_with_metrics'] += 1
    exp_lower = experience_text.lower()
    action_verb_count = sum(1 for verb in action_verbs if verb.lower() in
        exp_lower)
    results['metrics']['action_verbs_used'] = action_verb_count
    quantified = _count_quantified_achievements(experience_text)
    results['metrics']['quantified_achievements'] = quantified
    score = _calculate_experience_score(results['metrics'], len(job_entries))
    results['score'] = score
    _generate_experience_feedback(results)
    return results


def _parse_job_entries(experience_text: str) ->List[Dict]:
    jobs = []
    lines = experience_text.split('\n')
    current_job = None
    bullet_count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        date_pattern = (
            '(20\\d{2}|19\\d{2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)'
            )
        has_date = bool(re.search(date_pattern, line, re.IGNORECASE))
        title_patterns = [
            '(engineer|developer|manager|analyst|designer|consultant|intern|lead|director|specialist)'
            , '(senior|junior|associate|principal|staff|head)']
        has_title = any(re.search(p, line, re.IGNORECASE) for p in
            title_patterns)
        is_bullet = bool(re.match('^[\\•\\-\\*\\◦]|^\\d+\\.', line))
        if (has_date or has_title) and not is_bullet:
            if current_job:
                current_job['bullet_count'] = bullet_count
                jobs.append(current_job)
            current_job = {'text': line, 'has_dates': has_date, 'has_title':
                has_title, 'has_metrics': bool(re.search(
                '\\d+%|\\$\\d+|\\d+[kKmMbB]', line)), 'bullet_count': 0}
            bullet_count = 0
        elif is_bullet and current_job:
            bullet_count += 1
            if re.search(
                '\\d+%|\\$\\d+|\\d+[kKmMbB]|\\d+\\s*(users|customers|projects)'
                , line):
                current_job['has_metrics'] = True
    if current_job:
        current_job['bullet_count'] = bullet_count
        jobs.append(current_job)
    if not jobs and len(experience_text) > 100:
        jobs.append({'text': experience_text[:100], 'has_dates': bool(re.
            search('20\\d{2}|19\\d{2}', experience_text)), 'has_title': 
            True, 'has_metrics': bool(re.search('\\d+%|\\$\\d+',
            experience_text)), 'bullet_count': experience_text.count('•') +
            experience_text.count('-')})
    return jobs


def _count_quantified_achievements(text: str) ->int:
    patterns = ['\\d+%', '\\$[\\d,]+', '\\d+[kKmMbB]\\b',
        '\\d+\\s*(?:users|customers|clients|projects|teams|members)',
        '(?:increased|decreased|improved|reduced|grew|saved|generated|managed|led)\\s+(?:by\\s+)?\\d+'
        , '\\d+x\\s+(?:faster|better|improvement)']
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def _calculate_experience_score(metrics: Dict, job_count: int) ->float:
    score = 0.0
    if job_count >= 3:
        score += 5.0
    elif job_count >= 2:
        score += 4.0
    elif job_count >= 1:
        score += 3.0
    if job_count > 0:
        date_ratio = metrics['jobs_with_dates'] / job_count
        if date_ratio >= 0.9:
            score += 3.0
        elif date_ratio >= 0.7:
            score += 2.0
        elif date_ratio >= 0.5:
            score += 1.0
    if job_count > 0:
        bullet_ratio = metrics['jobs_with_bullets'] / job_count
        if bullet_ratio >= 0.9:
            score += 4.0
        elif bullet_ratio >= 0.7:
            score += 3.0
        elif bullet_ratio >= 0.5:
            score += 2.0
        elif bullet_ratio > 0:
            score += 1.0
    quant = metrics['quantified_achievements']
    if quant >= 8:
        score += 5.0
    elif quant >= 6:
        score += 4.0
    elif quant >= 4:
        score += 3.0
    elif quant >= 2:
        score += 2.0
    elif quant >= 1:
        score += 1.0
    verbs = metrics['action_verbs_used']
    if verbs >= 10:
        score += 3.0
    elif verbs >= 7:
        score += 2.0
    elif verbs >= 4:
        score += 1.0
    return min(20.0, max(0.0, score))


def _generate_experience_feedback(results: Dict) ->None:
    metrics = results['metrics']
    score = results['score']
    if metrics['total_jobs'] >= 2:
        results['strengths'].append(
            f"✅ {metrics['total_jobs']} job entries documented")
    if metrics['jobs_with_dates'] == metrics['total_jobs'] and metrics[
        'total_jobs'] > 0:
        results['strengths'].append('✅ All positions include dates')
    if metrics['quantified_achievements'] >= 5:
        results['strengths'].append(
            f"✅ {metrics['quantified_achievements']} quantified achievements")
    if metrics['action_verbs_used'] >= 8:
        results['strengths'].append(
            f"✅ Strong use of action verbs ({metrics['action_verbs_used']} found)"
            )
    if metrics['total_jobs'] < 2:
        results['improvements'].append(
            '📝 Add more work experience entries if available')
    if metrics['jobs_with_dates'] < metrics['total_jobs']:
        missing = metrics['total_jobs'] - metrics['jobs_with_dates']
        results['improvements'].append(
            f'📝 Add dates to {missing} job(s) missing date information')
    if metrics['quantified_achievements'] < 3:
        results['improvements'].append(
            '📝 Add more quantified achievements (numbers, percentages, metrics)'
            )
    if metrics['action_verbs_used'] < 5:
        results['improvements'].append(
            '📝 Use more action verbs to describe accomplishments')
    if metrics['jobs_with_bullets'] < metrics['total_jobs'] and metrics[
        'total_jobs'] > 0:
        results['improvements'].append(
            '📝 Use bullet points to list responsibilities and achievements')
    if score >= 16:
        results['feedback'].append(
            '🌟 Excellent experience section with strong details')
    elif score >= 12:
        results['feedback'].append(
            '✅ Good experience section with room for improvement')
    elif score >= 8:
        results['feedback'].append(
            '⚠️ Experience section needs more detail and quantification')
    else:
        results['feedback'].append(
            '❌ Experience section requires significant improvement')


def get_default_experience_results() ->Dict:
    return {'score': 10.0, 'max_score': 20.0, 'job_entries': [], 'metrics':
        {'total_jobs': 0, 'jobs_with_dates': 0, 'jobs_with_bullets': 0,
        'jobs_with_metrics': 0, 'action_verbs_used': 0,
        'quantified_achievements': 0}, 'feedback': [
        'Experience analysis not available'], 'strengths': [],
        'improvements': []}
