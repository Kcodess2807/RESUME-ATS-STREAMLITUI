"""
Experience Analyzer Module
Analyzes the work experience section of a resume and scores it out of 20 points.

📌 TEACHING NOTE — What does this file do?
    This is one of the SCORING engines of the ATS system.
    It focuses entirely on one resume section: Work Experience.

    The experience section is worth 20 out of 100 total ATS points.
    This file answers questions like:
    - How many jobs has the candidate listed?
    - Do all jobs have dates?
    - Are bullet points used?
    - Are achievements quantified? ("increased sales by 30%" vs "improved sales")
    - Are strong action verbs used? ("led", "built", "reduced" vs "was responsible for")

    📌 Scoring Breakdown (max 20 points):
        Job count          → up to 5 pts
        Dates present      → up to 3 pts
        Bullet points used → up to 4 pts
        Quantified results → up to 5 pts
        Action verbs       → up to 3 pts

    Key concept demonstrated: RULE-BASED ANALYSIS using Regex
    (No AI/ML here — just pattern matching on text)
"""

import re
from typing import Dict, List, Tuple


def analyze_experience_section(
    experience_text: str,
    action_verbs: List[str],
    full_text: str
) -> Dict:
    """
    Main entry point — analyze the experience section and return a full scored report.

    📌 TEACHING NOTE — Early Return / Guard Clause:
        The first thing this function does is check if there's enough text to analyze.
        If the experience section is missing or too short (< 50 chars), it returns
        immediately with an empty result and a warning message.

        This is called a "Guard Clause" — check the bad/edge case first and exit early.
        It avoids deeply nested if/else blocks and keeps the main logic clean.

        Without guard clause (messy):
            if experience_text and len(experience_text) > 50:
                ... 50 lines of code ...
        
        With guard clause (clean):
            if not experience_text or len < 50: return early
            ... 50 lines of main logic, unindented ...

    📌 TEACHING NOTE — Results dict as a "report object":
        We initialize a results dict at the top with ALL keys pre-set to defaults.
        This guarantees the caller always gets a complete structure back,
        even if some parts couldn't be computed. No missing key errors downstream.

    Args:
        experience_text: Text of just the experience section
        action_verbs: List of strong action verbs (loaded from data/action_verbs.json)
        full_text: Full resume text (available but not used here — kept for API consistency)

    Returns:
        Dict with score, metrics, feedback, strengths, improvements
    """
    # Initialize results with all keys and default values
    # This is our "report template" — filled in as we analyze
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
            'quantified_achievements': 0
        },
        'feedback': [],
        'strengths': [],
        'improvements': []
    }

    # ── Guard Clause: not enough text to analyze ─────────────────────────
    if not experience_text or len(experience_text.strip()) < 50:
        results['feedback'].append('⚠️ Experience section is missing or too short')
        results['improvements'].append(
            'Add detailed work experience with job titles, companies, and dates'
        )
        return results  # Exit early — nothing more to do

    # ── Step 1: Parse the text into individual job entries ───────────────
    job_entries = _parse_job_entries(experience_text)
    results['job_entries'] = job_entries
    results['metrics']['total_jobs'] = len(job_entries)

    # ── Step 2: Count which jobs have dates, bullets, and metrics ────────
    for job in job_entries:
        if job.get('has_dates'):
            results['metrics']['jobs_with_dates'] += 1
        if job.get('bullet_count', 0) > 0:
            results['metrics']['jobs_with_bullets'] += 1
        if job.get('has_metrics'):
            results['metrics']['jobs_with_metrics'] += 1

    # ── Step 3: Count action verbs used in the experience section ────────
    # We lowercase both sides for case-insensitive matching
    exp_lower = experience_text.lower()
    action_verb_count = sum(1 for verb in action_verbs if verb.lower() in exp_lower)
    results['metrics']['action_verbs_used'] = action_verb_count

    # ── Step 4: Count quantified achievements ("increased by 30%", "$50K") ──
    quantified = _count_quantified_achievements(experience_text)
    results['metrics']['quantified_achievements'] = quantified

    # ── Step 5: Calculate numeric score ──────────────────────────────────
    score = _calculate_experience_score(results['metrics'], len(job_entries))
    results['score'] = score

    # ── Step 6: Generate human-readable feedback ─────────────────────────
    _generate_experience_feedback(results)

    return results


def _parse_job_entries(experience_text: str) -> List[Dict]:
    """
    Parse the experience section text into a list of individual job entries.

    📌 TEACHING NOTE — State Machine Parsing:
        This function uses a technique called a "state machine" (simplified).
        We iterate through lines and track "what job are we currently in?"
        using the `current_job` variable.

        States:
        - current_job = None  → haven't seen a job header yet
        - current_job = {...} → inside a job, collecting bullet points

        Transitions:
        - See a line with date/title → start a new job (save old one first)
        - See a bullet point → add to current job's bullet count
        - See blank line → skip it

        This is a very common parsing pattern for structured but informal text.

    📌 TEACHING NOTE — Regex Patterns Used:
        date_pattern  → matches years (2019, 1998) or month names or "Present"
        title_patterns → matches common job title words
        is_bullet     → matches lines starting with •, -, *, ◦ or "1."

        re.IGNORECASE makes matching case-insensitive (Jan = jan = JAN)
        re.search() looks anywhere in the string (vs re.match() which only checks start)

    📌 TEACHING NOTE — Fallback at the end:
        If no job entries were parsed (e.g., experience is written as a paragraph),
        we create ONE synthetic entry from the full text. This prevents a score of 0
        for candidates who just wrote their experience differently.

    Returns:
        List of job dicts, each with: text, has_dates, has_title, has_metrics, bullet_count
    """
    jobs = []
    lines = experience_text.split('\n')
    current_job = None   # Tracks the job we're currently parsing
    bullet_count = 0     # Running count of bullets for current_job

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip blank lines

        # ── Detect what kind of line this is ─────────────────────────────

        # Does this line mention a year or month? (indicates a job header)
        date_pattern = r'(20\d{2}|19\d{2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)'
        has_date = bool(re.search(date_pattern, line, re.IGNORECASE))

        # Does this line contain job title keywords?
        title_patterns = [
            r'(engineer|developer|manager|analyst|designer|consultant|intern|lead|director|specialist)',
            r'(senior|junior|associate|principal|staff|head)'
        ]
        has_title = any(re.search(p, line, re.IGNORECASE) for p in title_patterns)

        # Does this line start with a bullet character or number?
        is_bullet = bool(re.match(r'^[\•\-\*\◦]|^\d+\.', line))

        # ── State transition: new job detected ───────────────────────────
        if (has_date or has_title) and not is_bullet:
            # Save the previous job before starting a new one
            if current_job:
                current_job['bullet_count'] = bullet_count
                jobs.append(current_job)

            # Start tracking the new job
            current_job = {
                'text': line,
                'has_dates': has_date,
                'has_title': has_title,
                # Check if the job HEADER LINE itself has metrics
                'has_metrics': bool(re.search(r'\d+%|\$\d+|\d+[kKmMbB]', line)),
                'bullet_count': 0
            }
            bullet_count = 0  # Reset bullet counter for new job

        # ── Collect bullet points for current job ────────────────────────
        elif is_bullet and current_job:
            bullet_count += 1
            # If this bullet has a number/metric, mark the job as having metrics
            if re.search(r'\d+%|\$\d+|\d+[kKmMbB]|\d+\s*(users|customers|projects)', line):
                current_job['has_metrics'] = True

    # Don't forget to save the last job after the loop ends
    if current_job:
        current_job['bullet_count'] = bullet_count
        jobs.append(current_job)

    # ── Fallback: no structured jobs found but text exists ───────────────
    # 📌 TEACHING NOTE: Some resumes don't follow the standard format.
    # Rather than giving a zero score for format issues, we create a
    # synthetic entry so the candidate still gets partial credit.
    if not jobs and len(experience_text) > 100:
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
    Count how many quantified achievements appear in the experience text.

    📌 TEACHING NOTE — Why quantified achievements matter for ATS:
        ATS systems and recruiters both prefer specific, measurable results.
        "Increased revenue by 40%" is much stronger than "improved revenue."
        Numbers prove impact and make the resume stand out.

    📌 TEACHING NOTE — Regex Pattern Categories:
        Each pattern targets a different way candidates write numbers:

        \\d+%                    → "increased by 30%", "reduced costs by 15%"
        \\$[\\d,]+               → "$50,000 budget", "$2M in sales"
        \\d+[kKmMbB]\\b         → "10K users", "2M downloads", "500B data points"
        \\d+\\s*(?:users|...)   → "500 users", "20 customers"
        (increased|...)by \\d+  → "grew by 3", "saved 40 hours"
        \\d+x faster/better     → "3x faster", "2x improvement"

        re.findall() returns ALL matches (not just first one).
        We sum the counts across all patterns.

    📌 TEACHING NOTE — Potential Issue (good discussion point):
        The same achievement might match multiple patterns and get counted twice.
        e.g., "increased revenue by 40%" matches both the % pattern AND the
        "increased...by...number" pattern.
        A more precise implementation would deduplicate by match position.

    Returns:
        Integer count of quantified achievement patterns found
    """
    patterns = [
        r'\d+%',                          # Percentages: 30%, 15%
        r'\$[\d,]+',                      # Dollar amounts: $50,000
        r'\d+[kKmMbB]\b',                # Abbreviated numbers: 10K, 2M
        r'\d+\s*(?:users|customers|clients|projects|teams|members)',  # Counts
        r'(?:increased|decreased|improved|reduced|grew|saved|generated|managed|led)\s+(?:by\s+)?\d+',  # Action + number
        r'\d+x\s+(?:faster|better|improvement)'  # Multipliers: 3x faster
    ]

    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def _calculate_experience_score(metrics: Dict, job_count: int) -> float:
    """
    Convert metrics into a numeric score out of 20 points.

    📌 TEACHING NOTE — Tiered Scoring (Rubric-Based):
        This function implements a RUBRIC — a structured scoring guide.
        Each criterion has tiers with different point values.
        This is exactly how teachers grade essays using rubrics!

        The tiers use ratios (jobs_with_dates / total_jobs) instead of
        raw counts so the score scales fairly regardless of how many jobs
        a candidate has listed.

    📌 TEACHING NOTE — Score Composition (total = 20 points):
        Job count          → max 5 pts  (3+ jobs = full marks)
        Dates present      → max 3 pts  (90%+ jobs have dates = full marks)
        Bullet points      → max 4 pts  (90%+ jobs have bullets = full marks)
        Quantified results → max 5 pts  (8+ achievements = full marks)
        Action verbs       → max 3 pts  (10+ verbs = full marks)

    📌 TEACHING NOTE — min(20.0, max(0.0, score)):
        This clamps the result to [0, 20].
        max(0.0, score)  → score can't be negative
        min(20.0, ...)   → score can't exceed maximum
        Both combined → safe range guarantee regardless of rounding errors.

    Args:
        metrics: Dict of computed metrics from analyze_experience_section()
        job_count: Total number of job entries found

    Returns:
        Float score between 0.0 and 20.0
    """
    score = 0.0

    # ── Criterion 1: Number of jobs (max 5 pts) ──────────────────────────
    if job_count >= 3:
        score += 5.0   # 3+ jobs → full marks
    elif job_count >= 2:
        score += 4.0
    elif job_count >= 1:
        score += 3.0   # At least has something

    # ── Criterion 2: Jobs with dates (max 3 pts) ─────────────────────────
    if job_count > 0:
        date_ratio = metrics['jobs_with_dates'] / job_count
        if date_ratio >= 0.9:    # 90%+ jobs have dates
            score += 3.0
        elif date_ratio >= 0.7:  # 70%+
            score += 2.0
        elif date_ratio >= 0.5:  # At least half
            score += 1.0

    # ── Criterion 3: Jobs with bullet points (max 4 pts) ─────────────────
    if job_count > 0:
        bullet_ratio = metrics['jobs_with_bullets'] / job_count
        if bullet_ratio >= 0.9:
            score += 4.0
        elif bullet_ratio >= 0.7:
            score += 3.0
        elif bullet_ratio >= 0.5:
            score += 2.0
        elif bullet_ratio > 0:   # At least one job has bullets
            score += 1.0

    # ── Criterion 4: Quantified achievements (max 5 pts) ─────────────────
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

    # ── Criterion 5: Action verbs (max 3 pts) ────────────────────────────
    verbs = metrics['action_verbs_used']
    if verbs >= 10:
        score += 3.0
    elif verbs >= 7:
        score += 2.0
    elif verbs >= 4:
        score += 1.0

    # Clamp to valid range: score can never be negative or exceed 20
    return min(20.0, max(0.0, score))


def _generate_experience_feedback(results: Dict) -> None:
    """
    Populate the results dict with human-readable strengths, improvements, and feedback.

    📌 TEACHING NOTE — Mutating a dict passed as argument:
        This function takes `results` and MODIFIES it in-place.
        It doesn't return anything (return type is None).

        In Python, dicts are passed by reference — when you modify a dict
        inside a function, the changes are visible to the caller.
        This is different from integers/strings which are passed by value.

        Alternative design: return new lists from this function.
        Current design: mutate the existing dict (simpler, less memory).

    📌 TEACHING NOTE — Strengths vs Improvements vs Feedback:
        Three separate lists in the results dict, each with a different purpose:
        - strengths:    things the candidate did WELL (positive reinforcement)
        - improvements: specific things to FIX (actionable advice)
        - feedback:     overall summary statement based on the score tier

        Separating these lets the UI display them in different places/styles.

    📌 TEACHING NOTE — Score Tier Thresholds:
        ≥ 16 → Excellent   (80%+ of max)
        ≥ 12 → Good        (60%+ of max)
        ≥  8 → Needs work  (40%+ of max)
        <  8 → Poor        (below 40%)

    Args:
        results: The results dict — modified in-place (no return value)
    """
    metrics = results['metrics']
    score = results['score']

    # ── Strengths (things done well) ─────────────────────────────────────
    if metrics['total_jobs'] >= 2:
        results['strengths'].append(f"✅ {metrics['total_jobs']} job entries documented")

    # Only praise dates if ALL jobs have them (100% compliance)
    if metrics['jobs_with_dates'] == metrics['total_jobs'] and metrics['total_jobs'] > 0:
        results['strengths'].append('✅ All positions include dates')

    if metrics['quantified_achievements'] >= 5:
        results['strengths'].append(
            f"✅ {metrics['quantified_achievements']} quantified achievements"
        )

    if metrics['action_verbs_used'] >= 8:
        results['strengths'].append(
            f"✅ Strong use of action verbs ({metrics['action_verbs_used']} found)"
        )

    # ── Improvements (specific things to fix) ────────────────────────────
    if metrics['total_jobs'] < 2:
        results['improvements'].append('📝 Add more work experience entries if available')

    if metrics['jobs_with_dates'] < metrics['total_jobs']:
        missing = metrics['total_jobs'] - metrics['jobs_with_dates']
        results['improvements'].append(
            f'📝 Add dates to {missing} job(s) missing date information'
        )

    if metrics['quantified_achievements'] < 3:
        results['improvements'].append(
            '📝 Add more quantified achievements (numbers, percentages, metrics)'
        )

    if metrics['action_verbs_used'] < 5:
        results['improvements'].append(
            '📝 Use more action verbs to describe accomplishments'
        )

    if metrics['jobs_with_bullets'] < metrics['total_jobs'] and metrics['total_jobs'] > 0:
        results['improvements'].append(
            '📝 Use bullet points to list responsibilities and achievements'
        )

    # ── Overall feedback (one summary line based on score tier) ──────────
    if score >= 16:
        results['feedback'].append('🌟 Excellent experience section with strong details')
    elif score >= 12:
        results['feedback'].append('✅ Good experience section with room for improvement')
    elif score >= 8:
        results['feedback'].append('⚠️ Experience section needs more detail and quantification')
    else:
        results['feedback'].append('❌ Experience section requires significant improvement')


def get_default_experience_results() -> Dict:
    """
    Return a safe default result when experience analysis cannot run.

    📌 TEACHING NOTE — Default/Fallback Values:
        If the analysis crashes or data is unavailable, callers get a
        safe result (score=10, neutral feedback) instead of an exception.
        The score of 10.0 (half of 20 max) represents "unknown/neutral" —
        not great, not terrible. It won't unfairly penalize the user for
        a system error.

        This pattern is called "Null Object Pattern" — instead of returning
        None (which requires callers to always null-check), we return a
        real object with sensible defaults.

    Returns:
        Dict with neutral default values for all expected keys
    """
    return {
        'score': 10.0,       # Neutral score — not penalizing for system errors
        'max_score': 20.0,
        'job_entries': [],
        'metrics': {
            'total_jobs': 0,
            'jobs_with_dates': 0,
            'jobs_with_bullets': 0,
            'jobs_with_metrics': 0,
            'action_verbs_used': 0,
            'quantified_achievements': 0
        },
        'feedback': ['Experience analysis not available'],
        'strengths': [],
        'improvements': []
    }