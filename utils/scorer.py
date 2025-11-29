"""
Scoring Engine Module for ATS Resume Scorer

This module calculates all component scores and the overall ATS compatibility score.
Implements the scoring algorithm with proper bounds checking and penalty/bonus application.

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 16.1, 16.2
"""

from typing import Dict, List, Optional, Tuple
import re
import streamlit as st
import hashlib


def calculate_formatting_score(sections: Dict[str, str], text: str) -> float:
    """
    Evaluates section presence, bullet points, and structure.
    
    Args:
        sections: Dictionary of extracted resume sections
        text: Full resume text
        
    Returns:
        Formatting score (0-20 points)
        
    Validates:
        - Requirements 9.1: Formatting score calculation (0-20 points)
    """
    score = 0.0
    
    # Section presence (10 points total)
    # Core sections: experience (3), education (2), skills (2)
    # Optional sections: summary (1.5), projects (1.5)
    if sections.get('experience') and len(sections['experience']) > 50:
        score += 3.0
    if sections.get('education') and len(sections['education']) > 20:
        score += 2.0
    if sections.get('skills') and len(sections['skills']) > 10:
        score += 2.0
    if sections.get('summary') and len(sections['summary']) > 30:
        score += 1.5
    if sections.get('projects') and len(sections['projects']) > 30:
        score += 1.5
    
    # Bullet point usage (5 points)
    bullet_patterns = [r'^\s*[•\-\*\◦]', r'^\s*\d+\.']
    bullet_count = 0
    for line in text.split('\n'):
        for pattern in bullet_patterns:
            if re.match(pattern, line):
                bullet_count += 1
                break
    
    # Award points based on bullet usage
    if bullet_count >= 15:
        score += 5.0
    elif bullet_count >= 10:
        score += 4.0
    elif bullet_count >= 5:
        score += 3.0
    elif bullet_count >= 3:
        score += 2.0
    elif bullet_count >= 1:
        score += 1.0
    
    # Structure and organization (5 points)
    # Check for clear section headers
    section_headers_found = 0
    for section_name in ['experience', 'education', 'skills', 'summary', 'projects']:
        if sections.get(section_name):
            section_headers_found += 1
    
    # Award points for well-organized structure
    if section_headers_found >= 4:
        score += 5.0
    elif section_headers_found >= 3:
        score += 4.0
    elif section_headers_found >= 2:
        score += 3.0
    elif section_headers_found >= 1:
        score += 2.0
    
    # Ensure score is within bounds
    return min(20.0, max(0.0, score))


def calculate_keywords_score(
    resume_keywords: List[str],
    skills: List[str],
    jd_keywords: Optional[List[str]] = None
) -> float:
    """
    Evaluates keyword presence and matching.
    
    Args:
        resume_keywords: Keywords extracted from resume
        skills: Skills extracted from resume
        jd_keywords: Optional keywords from job description
        
    Returns:
        Keywords and skills score (0-25 points)
        
    Validates:
        - Requirements 9.2: Keywords and skills score calculation (0-25 points)
    """
    score = 0.0
    
    # Base keyword count (10 points)
    keyword_count = len(resume_keywords)
    if keyword_count >= 20:
        score += 10.0
    elif keyword_count >= 15:
        score += 8.0
    elif keyword_count >= 10:
        score += 6.0
    elif keyword_count >= 5:
        score += 4.0
    elif keyword_count >= 3:
        score += 2.0
    
    # Skills count (10 points)
    skills_count = len(skills)
    if skills_count >= 15:
        score += 10.0
    elif skills_count >= 10:
        score += 8.0
    elif skills_count >= 7:
        score += 6.0
    elif skills_count >= 5:
        score += 4.0
    elif skills_count >= 3:
        score += 2.0
    
    # Job description matching bonus (5 points)
    if jd_keywords:
        # Calculate keyword overlap
        resume_kw_set = set(kw.lower() for kw in resume_keywords)
        jd_kw_set = set(kw.lower() for kw in jd_keywords)
        
        if jd_kw_set:
            overlap = len(resume_kw_set & jd_kw_set)
            match_percentage = overlap / len(jd_kw_set)
            
            if match_percentage >= 0.7:
                score += 5.0
            elif match_percentage >= 0.5:
                score += 4.0
            elif match_percentage >= 0.3:
                score += 3.0
            elif match_percentage >= 0.2:
                score += 2.0
            elif match_percentage >= 0.1:
                score += 1.0
    else:
        # If no JD provided, award partial points for having keywords
        if keyword_count >= 10:
            score += 3.0
    
    # Ensure score is within bounds
    return min(25.0, max(0.0, score))


def calculate_content_score(
    text: str,
    action_verbs: List[str],
    grammar_results: Dict
) -> float:
    """
    Evaluates action verbs, achievements, and grammar quality.
    
    Args:
        text: Full resume text
        action_verbs: List of detected action verbs
        grammar_results: Grammar check results
        
    Returns:
        Content quality score (0-25 points)
        
    Validates:
        - Requirements 9.3: Content quality score calculation (0-25 points)
    """
    score = 0.0
    
    # Action verbs usage (10 points)
    action_verb_count = len(action_verbs)
    if action_verb_count >= 15:
        score += 10.0
    elif action_verb_count >= 10:
        score += 8.0
    elif action_verb_count >= 7:
        score += 6.0
    elif action_verb_count >= 5:
        score += 4.0
    elif action_verb_count >= 3:
        score += 2.0
    
    # Quantifiable achievements (5 points)
    # Look for numbers, percentages, and metrics
    number_patterns = [
        r'\d+%',  # Percentages
        r'\$\d+',  # Dollar amounts
        r'\d+[kKmMbB]',  # Abbreviated numbers (10k, 5M, etc.)
        r'\d+\s*(?:users|customers|clients|projects|hours|days|months|years)',  # Metrics
        r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+',  # Impact statements
    ]
    
    achievement_count = 0
    for pattern in number_patterns:
        achievement_count += len(re.findall(pattern, text, re.IGNORECASE))
    
    if achievement_count >= 10:
        score += 5.0
    elif achievement_count >= 7:
        score += 4.0
    elif achievement_count >= 5:
        score += 3.0
    elif achievement_count >= 3:
        score += 2.0
    elif achievement_count >= 1:
        score += 1.0
    
    # Grammar quality (10 points)
    # Start with 10 points and subtract grammar penalty
    grammar_penalty = grammar_results.get('penalty_applied', 0.0)
    grammar_score = max(0.0, 10.0 - grammar_penalty / 2.0)  # Scale penalty to 10 points
    score += grammar_score
    
    # Ensure score is within bounds
    return min(25.0, max(0.0, score))


def calculate_skill_validation_score(validation_results: Dict) -> float:
    """
    Calculates skill validation component score.
    
    Args:
        validation_results: Results from skill validation
        
    Returns:
        Skill validation score (0-15 points)
        
    Validates:
        - Requirements 9.4: Skill validation score calculation (0-15 points)
    """
    # Get validation score directly from results
    # Formula: (validated_skills / total_skills) × 15
    score = validation_results.get('validation_score', 0.0)
    
    # Ensure score is within bounds
    return min(15.0, max(0.0, score))


def calculate_ats_compatibility_score(
    text: str,
    location_results: Dict,
    sections: Dict[str, str]
) -> float:
    """
    Evaluates ATS-friendly formatting and privacy considerations.
    
    Args:
        text: Full resume text
        location_results: Location detection results
        sections: Extracted resume sections
        
    Returns:
        ATS compatibility score (0-15 points)
        
    Validates:
        - Requirements 9.5: ATS compatibility score calculation (0-15 points)
    """
    score = 15.0  # Start with full score and deduct for issues
    
    # Location privacy penalty (0-5 points)
    location_penalty = location_results.get('penalty_applied', 0.0)
    score -= location_penalty
    
    # Check for ATS-unfriendly elements
    # Tables, columns, headers/footers are hard to detect in plain text
    # Focus on what we can detect
    
    # Penalize excessive special characters (may indicate complex formatting)
    special_char_count = len(re.findall(r'[│┤├┼┴┬╔╗╚╝═║╠╣╦╩╬]', text))
    if special_char_count > 20:
        score -= 2.0
    elif special_char_count > 10:
        score -= 1.0
    
    # Penalize very short sections (may indicate parsing issues)
    short_sections = 0
    for section_name, content in sections.items():
        if section_name in ['experience', 'education', 'skills']:
            if content and len(content) < 20:
                short_sections += 1
    
    if short_sections >= 2:
        score -= 2.0
    elif short_sections >= 1:
        score -= 1.0
    
    # Bonus for clean, parseable structure
    if len(sections.get('experience', '')) > 100 and len(sections.get('skills', '')) > 20:
        score += 1.0
    
    # Ensure score is within bounds
    return min(15.0, max(0.0, score))


def apply_penalties_and_bonuses(
    base_score: float,
    grammar_results: Dict,
    location_results: Dict,
    skill_validation_results: Dict
) -> Tuple[float, Dict, Dict]:
    """
    Apply additional penalties and bonuses to the overall score.
    
    Args:
        base_score: Sum of all component scores
        grammar_results: Grammar check results
        location_results: Location detection results
        skill_validation_results: Skill validation results
        
    Returns:
        Tuple of (adjusted_score, penalties_dict, bonuses_dict)
    """
    penalties = {}
    bonuses = {}
    adjusted_score = base_score
    
    # Grammar penalty (already applied in content score, but track it)
    grammar_penalty = grammar_results.get('penalty_applied', 0.0)
    if grammar_penalty > 0:
        penalties['grammar'] = grammar_penalty
    
    # Location privacy penalty (already applied in ATS score, but track it)
    location_penalty = location_results.get('penalty_applied', 0.0)
    if location_penalty > 0:
        penalties['location_privacy'] = location_penalty
    
    # Bonus for high skill validation
    validation_percentage = skill_validation_results.get('validation_percentage', 0.0)
    if validation_percentage >= 0.9:
        bonus = 2.0
        bonuses['excellent_skill_validation'] = bonus
        adjusted_score += bonus
    elif validation_percentage >= 0.8:
        bonus = 1.0
        bonuses['good_skill_validation'] = bonus
        adjusted_score += bonus
    
    # Bonus for error-free grammar
    if grammar_results.get('total_errors', 0) == 0:
        bonus = 2.0
        bonuses['perfect_grammar'] = bonus
        adjusted_score += bonus
    
    # Ensure final score is within bounds
    adjusted_score = min(100.0, max(0.0, adjusted_score))
    
    return adjusted_score, penalties, bonuses


def generate_score_interpretation(overall_score: float) -> str:
    """
    Generate interpretation message based on overall score.
    
    Args:
        overall_score: Overall ATS compatibility score (0-100)
        
    Returns:
        Interpretation message string
    """
    if overall_score >= 90:
        return "🌟 Excellent! Your resume is highly optimized for ATS systems."
    elif overall_score >= 80:
        return "✅ Great! Your resume should perform well with most ATS systems."
    elif overall_score >= 70:
        return "👍 Good! Your resume is ATS-friendly with room for minor improvements."
    elif overall_score >= 60:
        return "⚠️ Fair. Your resume needs some improvements to be fully ATS-compatible."
    elif overall_score >= 50:
        return "❌ Below Average. Significant improvements needed for ATS compatibility."
    else:
        return "🔴 Poor. Your resume requires major revisions to pass ATS screening."


def generate_score_breakdown_messages(
    formatting_score: float,
    keywords_score: float,
    content_score: float,
    skill_validation_score: float,
    ats_compatibility_score: float
) -> Dict[str, str]:
    """
    Generate interpretation messages for each component score.
    
    Args:
        formatting_score: Formatting component score
        keywords_score: Keywords component score
        content_score: Content quality component score
        skill_validation_score: Skill validation component score
        ats_compatibility_score: ATS compatibility component score
        
    Returns:
        Dictionary mapping component names to interpretation messages
    """
    messages = {}
    
    # Formatting (0-20)
    if formatting_score >= 18:
        messages['formatting'] = "Excellent structure and organization"
    elif formatting_score >= 15:
        messages['formatting'] = "Good formatting with minor improvements possible"
    elif formatting_score >= 12:
        messages['formatting'] = "Adequate formatting, consider adding more structure"
    else:
        messages['formatting'] = "Needs improvement: add sections and bullet points"
    
    # Keywords (0-25)
    if keywords_score >= 22:
        messages['keywords'] = "Excellent keyword optimization"
    elif keywords_score >= 18:
        messages['keywords'] = "Good keyword presence"
    elif keywords_score >= 14:
        messages['keywords'] = "Adequate keywords, could add more relevant terms"
    else:
        messages['keywords'] = "Needs more keywords and skills"
    
    # Content (0-25)
    if content_score >= 22:
        messages['content'] = "Excellent content quality with strong action verbs"
    elif content_score >= 18:
        messages['content'] = "Good content with measurable achievements"
    elif content_score >= 14:
        messages['content'] = "Adequate content, add more quantifiable results"
    else:
        messages['content'] = "Needs improvement: add action verbs and metrics"
    
    # Skill Validation (0-15)
    if skill_validation_score >= 13:
        messages['skill_validation'] = "Excellent skill validation"
    elif skill_validation_score >= 10:
        messages['skill_validation'] = "Good skill validation"
    elif skill_validation_score >= 7:
        messages['skill_validation'] = "Some skills lack supporting evidence"
    else:
        messages['skill_validation'] = "Many skills are not validated by projects"
    
    # ATS Compatibility (0-15)
    if ats_compatibility_score >= 13:
        messages['ats_compatibility'] = "Excellent ATS compatibility"
    elif ats_compatibility_score >= 11:
        messages['ats_compatibility'] = "Good ATS compatibility"
    elif ats_compatibility_score >= 9:
        messages['ats_compatibility'] = "Adequate ATS compatibility with minor issues"
    else:
        messages['ats_compatibility'] = "ATS compatibility needs improvement"
    
    return messages


def _compute_overall_score(
    text: str,
    sections: Dict[str, str],
    skills: List[str],
    keywords: List[str],
    action_verbs: List[str],
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    jd_keywords: Optional[List[str]] = None
) -> Dict:
    """
    Internal function to compute overall score.
    
    Args:
        text: Full resume text
        sections: Extracted resume sections
        skills: Extracted skills list
        keywords: Extracted keywords list
        action_verbs: Detected action verbs list
        skill_validation_results: Results from skill validation
        grammar_results: Results from grammar checking
        location_results: Results from location detection
        jd_keywords: Optional keywords from job description
        
    Returns:
        Dictionary containing all scores and interpretations
    """
    # Calculate component scores
    formatting_score = calculate_formatting_score(sections, text)
    keywords_score = calculate_keywords_score(keywords, skills, jd_keywords)
    content_score = calculate_content_score(text, action_verbs, grammar_results)
    skill_validation_score = calculate_skill_validation_score(skill_validation_results)
    ats_compatibility_score = calculate_ats_compatibility_score(text, location_results, sections)
    
    # Sum component scores
    base_score = (
        formatting_score +
        keywords_score +
        content_score +
        skill_validation_score +
        ats_compatibility_score
    )
    
    # Apply penalties and bonuses
    overall_score, penalties, bonuses = apply_penalties_and_bonuses(
        base_score,
        grammar_results,
        location_results,
        skill_validation_results
    )
    
    # Generate interpretation messages
    overall_interpretation = generate_score_interpretation(overall_score)
    component_messages = generate_score_breakdown_messages(
        formatting_score,
        keywords_score,
        content_score,
        skill_validation_score,
        ats_compatibility_score
    )
    
    return {
        "overall_score": round(overall_score, 1),
        "overall_interpretation": overall_interpretation,
        "formatting_score": round(formatting_score, 1),
        "keywords_score": round(keywords_score, 1),
        "content_score": round(content_score, 1),
        "skill_validation_score": round(skill_validation_score, 1),
        "ats_compatibility_score": round(ats_compatibility_score, 1),
        "component_messages": component_messages,
        "penalties": penalties,
        "bonuses": bonuses
    }


def calculate_overall_score(
    text: str,
    sections: Dict[str, str],
    skills: List[str],
    keywords: List[str],
    action_verbs: List[str],
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    jd_keywords: Optional[List[str]] = None,
    use_cache: bool = True
) -> Dict:
    """
    Calculates all component scores and overall ATS compatibility score.
    
    Args:
        text: Full resume text
        sections: Extracted resume sections
        skills: Extracted skills list
        keywords: Extracted keywords list
        action_verbs: Detected action verbs list
        skill_validation_results: Results from skill validation
        grammar_results: Results from grammar checking
        location_results: Results from location detection
        jd_keywords: Optional keywords from job description
        use_cache: Whether to use session state caching (default: True)
        
    Returns:
        Dictionary containing:
        {
            "overall_score": 0-100,
            "overall_interpretation": "...",
            "formatting_score": 0-20,
            "keywords_score": 0-25,
            "content_score": 0-25,
            "skill_validation_score": 0-15,
            "ats_compatibility_score": 0-15,
            "component_messages": {...},
            "penalties": {...},
            "bonuses": {...}
        }
        
    Validates:
        - Requirements 9.1: Formatting score calculation (0-20 points)
        - Requirements 9.2: Keywords and skills score calculation (0-25 points)
        - Requirements 9.3: Content quality score calculation (0-25 points)
        - Requirements 9.4: Skill validation score calculation (0-15 points)
        - Requirements 9.5: ATS compatibility score calculation (0-15 points)
        - Requirements 9.6: Overall score aggregation
        - Requirements 9.7: Apply penalties and bonuses
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    # Check if we're in a Streamlit context
    try:
        # Check if session_state is a proper Streamlit SessionState object
        # In tests, it may be a plain dict which doesn't support attribute assignment
        from streamlit.runtime.state import SessionState
        in_streamlit = isinstance(st.session_state, SessionState)
    except Exception:
        in_streamlit = False
    
    if use_cache and in_streamlit:
        # Generate cache key from inputs
        import json
        
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        skills_key = tuple(sorted(skills)) if skills else ()
        keywords_key = tuple(sorted(keywords)) if keywords else ()
        jd_key = tuple(sorted(jd_keywords)) if jd_keywords else ()
        
        cache_key = f"score_{text_hash}_{hash((skills_key, keywords_key, jd_key))}"
        
        # Check session state cache
        if 'score_cache' not in st.session_state:
            st.session_state.score_cache = {}
        
        if cache_key in st.session_state.score_cache:
            return st.session_state.score_cache[cache_key]
        
        # Compute and cache
        result = _compute_overall_score(
            text, sections, skills, keywords, action_verbs,
            skill_validation_results, grammar_results, location_results, jd_keywords
        )
        st.session_state.score_cache[cache_key] = result
        
        # Limit cache size
        if len(st.session_state.score_cache) > 20:
            oldest_key = next(iter(st.session_state.score_cache))
            del st.session_state.score_cache[oldest_key]
        
        return result
    else:
        return _compute_overall_score(
            text, sections, skills, keywords, action_verbs,
            skill_validation_results, grammar_results, location_results, jd_keywords
        )


def generate_strengths(score_results: Dict, skill_validation_results: Dict, grammar_results: Dict) -> List[str]:
    """
    Generate list of resume strengths based on scores.
    
    Args:
        score_results: Results from calculate_overall_score
        skill_validation_results: Skill validation results
        grammar_results: Grammar check results
        
    Returns:
        List of strength messages
    """
    strengths = []
    
    # Check each component
    if score_results['formatting_score'] >= 16:
        strengths.append("✅ Well-structured with clear sections and bullet points")
    
    if score_results['keywords_score'] >= 20:
        strengths.append("✅ Strong keyword optimization and skills presence")
    
    if score_results['content_score'] >= 20:
        strengths.append("✅ Excellent use of action verbs and quantifiable achievements")
    
    if score_results['skill_validation_score'] >= 12:
        validation_pct = skill_validation_results.get('validation_percentage', 0) * 100
        strengths.append(f"✅ {validation_pct:.0f}% of skills are validated by projects")
    
    if score_results['ats_compatibility_score'] >= 13:
        strengths.append("✅ Excellent ATS compatibility with clean formatting")
    
    if grammar_results.get('total_errors', 0) == 0:
        strengths.append("✅ Error-free grammar and spelling")
    
    if not strengths:
        strengths.append("Your resume has potential - focus on the recommendations below")
    
    return strengths


def generate_critical_issues(score_results: Dict, grammar_results: Dict, location_results: Dict) -> List[str]:
    """
    Generate list of critical issues that need immediate attention.
    
    Args:
        score_results: Results from calculate_overall_score
        grammar_results: Grammar check results
        location_results: Location detection results
        
    Returns:
        List of critical issue messages
    """
    issues = []
    
    # Critical grammar errors
    critical_errors = len(grammar_results.get('critical_errors', []))
    if critical_errors > 0:
        issues.append(f"🔴 {critical_errors} critical grammar/spelling error(s) detected")
    
    # Location privacy issues
    if location_results.get('privacy_risk') == 'high':
        issues.append("🔴 High privacy risk: Remove detailed location information")
    
    # Very low component scores
    if score_results['formatting_score'] < 10:
        issues.append("🔴 Poor formatting: Add clear sections and bullet points")
    
    if score_results['keywords_score'] < 12:
        issues.append("🔴 Insufficient keywords and skills")
    
    if score_results['skill_validation_score'] < 7:
        issues.append("🔴 Most skills lack supporting evidence in projects")
    
    return issues


def generate_improvements(score_results: Dict, skill_validation_results: Dict) -> List[str]:
    """
    Generate list of areas for improvement.
    
    Args:
        score_results: Results from calculate_overall_score
        skill_validation_results: Skill validation results
        
    Returns:
        List of improvement suggestions
    """
    improvements = []
    
    # Moderate issues that could be improved
    if 12 <= score_results['formatting_score'] < 16:
        improvements.append("📝 Add more bullet points and improve section organization")
    
    if 14 <= score_results['keywords_score'] < 20:
        improvements.append("📝 Include more relevant keywords and technical skills")
    
    if 14 <= score_results['content_score'] < 20:
        improvements.append("📝 Add more quantifiable achievements and action verbs")
    
    if 7 <= score_results['skill_validation_score'] < 12:
        unvalidated_count = len(skill_validation_results.get('unvalidated_skills', []))
        improvements.append(f"📝 Validate {unvalidated_count} skill(s) by adding relevant project details")
    
    if 9 <= score_results['ats_compatibility_score'] < 13:
        improvements.append("📝 Simplify formatting for better ATS compatibility")
    
    return improvements
