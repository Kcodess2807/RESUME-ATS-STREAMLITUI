"""
Experience Section Analyzer Module
Analyzes the quality and completeness of the experience section in resumes.
"""

import re
from typing import Dict, List, Tuple


def analyze_experience_section(
    experience_text: str,
    action_verbs: List[str],
    full_text: str
) -> Dict:
    """
    Analyze the experience section for quality metrics.
    
    Args:
        experience_text: Text from the experience section
        action_verbs: List of action verbs found in resume
        full_text: Full resume text for context
        
    Returns:
        Dictionary containing experience analysis results
    """
    results = {
        'score': 0.0,
        'max_score': 20.0,
        'job_entries': [],
        'metrics': {
            'total_jobs': 0,
            'jobs_with_dates': 0,
            'jobs_with_bullets': 0,
            'jobs_with_metrics': 0,
            'action_verbs_used': 0,
            'quantified_achievements': 0,
        },
        'feedback': [],
        'strengths': [],
        'improvements': []
    }
    
    if not experience_text or len(experience_text.strip()) < 50:
        results['feedback'].append("⚠️ Experience section is missing or too short")
        results['improvements'].append("Add detailed work experience with job titles, companies, and dates")
        return results
    
    # Parse job entries
    job_entries = _parse_job_entries(experience_text)
    results['job_entries'] = job_entries
    results['metrics']['total_jobs'] = len(job_entries)
    
    # Analyze each job entry
    for job in job_entries:
        if job.get('has_dates'):
            results['metrics']['jobs_with_dates'] += 1
        if job.get('bullet_count', 0) > 0:
            results['metrics']['jobs_with_bullets'] += 1
        if job.get('has_metrics'):
            results['metrics']['jobs_with_metrics'] += 1
    
    # Count action verbs in experience section
    exp_lower = experience_text.lower()
    action_verb_count = sum(1 for verb in action_verbs if verb.lower() in exp_lower)
    results['metrics']['action_verbs_used'] = action_verb_count
    
    # Count quantified achievements
    quantified = _count_quantified_achievements(experience_text)
    results['metrics']['quantified_achievements'] = quantified
    
    # Calculate score
    score = _calculate_experience_score(results['metrics'], len(job_entries))
    results['score'] = score
    
    # Generate feedback
    _generate_experience_feedback(results)
    
    return results


def _parse_job_entries(experience_text: str) -> List[Dict]:
    """
    Parse individual job entries from experience section.
    
    Args:
        experience_text: Text from experience section
        
    Returns:
        List of job entry dictionaries
    """
    jobs = []
    
    # Split by common job entry patterns
    # Look for patterns like "Company Name" followed by dates or job titles
    lines = experience_text.split('\n')
    
    current_job = None
    bullet_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this looks like a new job entry (has date pattern or title-like structure)
        date_pattern = r'(20\d{2}|19\d{2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)'
        has_date = bool(re.search(date_pattern, line, re.IGNORECASE))
        
        # Check for job title patterns
        title_patterns = [
            r'(engineer|developer|manager|analyst|designer|consultant|intern|lead|director|specialist)',
            r'(senior|junior|associate|principal|staff|head)',
        ]
        has_title = any(re.search(p, line, re.IGNORECASE) for p in title_patterns)
        
        # Check if it's a bullet point
        is_bullet = bool(re.match(r'^[\•\-\*\◦]|^\d+\.', line))
        
        if (has_date or has_title) and not is_bullet:
            # Save previous job if exists
            if current_job:
                current_job['bullet_count'] = bullet_count
                jobs.append(current_job)
            
            # Start new job entry
            current_job = {
                'text': line,
                'has_dates': has_date,
                'has_title': has_title,
                'has_metrics': bool(re.search(r'\d+%|\$\d+|\d+[kKmMbB]', line)),
                'bullet_count': 0
            }
            bullet_count = 0
        elif is_bullet and current_job:
            bullet_count += 1
            # Check for metrics in bullet
            if re.search(r'\d+%|\$\d+|\d+[kKmMbB]|\d+\s*(users|customers|projects)', line):
                current_job['has_metrics'] = True
    
    # Don't forget the last job
    if current_job:
        current_job['bullet_count'] = bullet_count
        jobs.append(current_job)
    
    # If no jobs found through parsing, estimate based on content
    if not jobs and len(experience_text) > 100:
        # Assume at least one job entry exists
        jobs.append({
            'text': experience_text[:100],
            'has_dates': bool(re.search(r'20\d{2}|19\d{2}', experience_text)),
            'has_title': True,
            'has_metrics': bool(re.search(r'\d+%|\$\d+', experience_text)),
            'bullet_count': experience_text.count('•') + experience_text.count('-')
        })
    
    return jobs


def _count_quantified_achievements(text: str) -> int:
    """
    Count quantified achievements in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Count of quantified achievements
    """
    patterns = [
        r'\d+%',  # Percentages
        r'\$[\d,]+',  # Dollar amounts
        r'\d+[kKmMbB]\b',  # Abbreviated numbers
        r'\d+\s*(?:users|customers|clients|projects|teams|members)',  # User/team metrics
        r'(?:increased|decreased|improved|reduced|grew|saved|generated|managed|led)\s+(?:by\s+)?\d+',
        r'\d+x\s+(?:faster|better|improvement)',  # Multiplier improvements
    ]
    
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    
    return count


def _calculate_experience_score(metrics: Dict, job_count: int) -> float:
    """
    Calculate experience section score based on metrics.
    
    Scoring breakdown (0-20 points):
    - Job entries present: 0-5 points
    - Dates included: 0-3 points
    - Bullet points used: 0-4 points
    - Quantified achievements: 0-5 points
    - Action verbs: 0-3 points
    
    Args:
        metrics: Dictionary of experience metrics
        job_count: Number of job entries
        
    Returns:
        Experience score (0-20)
    """
    score = 0.0
    
    # Job entries (0-5 points)
    if job_count >= 3:
        score += 5.0
    elif job_count >= 2:
        score += 4.0
    elif job_count >= 1:
        score += 3.0
    
    # Dates included (0-3 points)
    if job_count > 0:
        date_ratio = metrics['jobs_with_dates'] / job_count
        if date_ratio >= 0.9:
            score += 3.0
        elif date_ratio >= 0.7:
            score += 2.0
        elif date_ratio >= 0.5:
            score += 1.0
    
    # Bullet points (0-4 points)
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
    
    # Quantified achievements (0-5 points)
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
    
    # Action verbs (0-3 points)
    verbs = metrics['action_verbs_used']
    if verbs >= 10:
        score += 3.0
    elif verbs >= 7:
        score += 2.0
    elif verbs >= 4:
        score += 1.0
    
    return min(20.0, max(0.0, score))


def _generate_experience_feedback(results: Dict) -> None:
    """
    Generate feedback messages based on experience analysis.
    
    Args:
        results: Results dictionary to update with feedback
    """
    metrics = results['metrics']
    score = results['score']
    
    # Strengths
    if metrics['total_jobs'] >= 2:
        results['strengths'].append(f"✅ {metrics['total_jobs']} job entries documented")
    
    if metrics['jobs_with_dates'] == metrics['total_jobs'] and metrics['total_jobs'] > 0:
        results['strengths'].append("✅ All positions include dates")
    
    if metrics['quantified_achievements'] >= 5:
        results['strengths'].append(f"✅ {metrics['quantified_achievements']} quantified achievements")
    
    if metrics['action_verbs_used'] >= 8:
        results['strengths'].append(f"✅ Strong use of action verbs ({metrics['action_verbs_used']} found)")
    
    # Improvements
    if metrics['total_jobs'] < 2:
        results['improvements'].append("📝 Add more work experience entries if available")
    
    if metrics['jobs_with_dates'] < metrics['total_jobs']:
        missing = metrics['total_jobs'] - metrics['jobs_with_dates']
        results['improvements'].append(f"📝 Add dates to {missing} job(s) missing date information")
    
    if metrics['quantified_achievements'] < 3:
        results['improvements'].append("📝 Add more quantified achievements (numbers, percentages, metrics)")
    
    if metrics['action_verbs_used'] < 5:
        results['improvements'].append("📝 Use more action verbs to describe accomplishments")
    
    if metrics['jobs_with_bullets'] < metrics['total_jobs'] and metrics['total_jobs'] > 0:
        results['improvements'].append("📝 Use bullet points to list responsibilities and achievements")
    
    # Overall feedback
    if score >= 16:
        results['feedback'].append("🌟 Excellent experience section with strong details")
    elif score >= 12:
        results['feedback'].append("✅ Good experience section with room for improvement")
    elif score >= 8:
        results['feedback'].append("⚠️ Experience section needs more detail and quantification")
    else:
        results['feedback'].append("❌ Experience section requires significant improvement")


def get_default_experience_results() -> Dict:
    """
    Return default experience results when analysis cannot be performed.
    
    Returns:
        Default experience analysis dictionary
    """
    return {
        'score': 10.0,
        'max_score': 20.0,
        'job_entries': [],
        'metrics': {
            'total_jobs': 0,
            'jobs_with_dates': 0,
            'jobs_with_bullets': 0,
            'jobs_with_metrics': 0,
            'action_verbs_used': 0,
            'quantified_achievements': 0,
        },
        'feedback': ["Experience analysis not available"],
        'strengths': [],
        'improvements': []
    }
