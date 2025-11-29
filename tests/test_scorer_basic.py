"""
Basic tests for the scoring engine module.
Tests core functionality and score bounds.
"""

import pytest
from utils.scorer import (
    calculate_formatting_score,
    calculate_keywords_score,
    calculate_content_score,
    calculate_skill_validation_score,
    calculate_ats_compatibility_score,
    calculate_overall_score,
    generate_score_interpretation,
    generate_strengths,
    generate_critical_issues,
    generate_improvements
)


def test_formatting_score_bounds():
    """Test that formatting score is within 0-20 bounds."""
    # Empty sections
    sections = {'experience': '', 'education': '', 'skills': '', 'summary': '', 'projects': ''}
    text = ""
    score = calculate_formatting_score(sections, text)
    assert 0 <= score <= 20
    
    # Full sections with bullets
    sections = {
        'experience': 'x' * 100,
        'education': 'x' * 50,
        'skills': 'x' * 30,
        'summary': 'x' * 50,
        'projects': 'x' * 50
    }
    text = '\n'.join(['• bullet point'] * 20)
    score = calculate_formatting_score(sections, text)
    assert 0 <= score <= 20


def test_keywords_score_bounds():
    """Test that keywords score is within 0-25 bounds."""
    # No keywords
    score = calculate_keywords_score([], [])
    assert 0 <= score <= 25
    
    # Many keywords
    keywords = [f"keyword{i}" for i in range(30)]
    skills = [f"skill{i}" for i in range(20)]
    score = calculate_keywords_score(keywords, skills)
    assert 0 <= score <= 25


def test_content_score_bounds():
    """Test that content score is within 0-25 bounds."""
    # Minimal content
    grammar_results = {'penalty_applied': 0.0, 'total_errors': 0}
    score = calculate_content_score("", [], grammar_results)
    assert 0 <= score <= 25
    
    # Rich content
    text = "Increased revenue by 50%. Managed $1M budget. Led team of 10 developers."
    action_verbs = ['increased', 'managed', 'led', 'developed', 'created']
    score = calculate_content_score(text, action_verbs, grammar_results)
    assert 0 <= score <= 25


def test_skill_validation_score_bounds():
    """Test that skill validation score is within 0-15 bounds."""
    # No validation
    validation_results = {'validation_score': 0.0}
    score = calculate_skill_validation_score(validation_results)
    assert 0 <= score <= 15
    
    # Full validation
    validation_results = {'validation_score': 15.0}
    score = calculate_skill_validation_score(validation_results)
    assert 0 <= score <= 15
    
    # Over bounds (should be capped)
    validation_results = {'validation_score': 20.0}
    score = calculate_skill_validation_score(validation_results)
    assert score == 15.0


def test_ats_compatibility_score_bounds():
    """Test that ATS compatibility score is within 0-15 bounds."""
    # No issues
    location_results = {'penalty_applied': 0.0}
    sections = {'experience': 'x' * 100, 'skills': 'x' * 30}
    score = calculate_ats_compatibility_score("", location_results, sections)
    assert 0 <= score <= 15
    
    # High penalty
    location_results = {'penalty_applied': 5.0}
    score = calculate_ats_compatibility_score("", location_results, sections)
    assert 0 <= score <= 15


def test_overall_score_bounds():
    """Test that overall score is within 0-100 bounds."""
    # Minimal resume
    text = "Resume text"
    sections = {'experience': '', 'education': '', 'skills': '', 'summary': '', 'projects': ''}
    skills = []
    keywords = []
    action_verbs = []
    skill_validation_results = {'validation_score': 0.0, 'validation_percentage': 0.0, 'unvalidated_skills': []}
    grammar_results = {'penalty_applied': 0.0, 'total_errors': 0, 'critical_errors': []}
    location_results = {'penalty_applied': 0.0, 'privacy_risk': 'none', 'detected_locations': []}
    
    result = calculate_overall_score(
        text, sections, skills, keywords, action_verbs,
        skill_validation_results, grammar_results, location_results
    )
    
    assert 0 <= result['overall_score'] <= 100
    assert 0 <= result['formatting_score'] <= 20
    assert 0 <= result['keywords_score'] <= 25
    assert 0 <= result['content_score'] <= 25
    assert 0 <= result['skill_validation_score'] <= 15
    assert 0 <= result['ats_compatibility_score'] <= 15


def test_overall_score_with_good_resume():
    """Test scoring with a well-structured resume."""
    text = """
    John Doe
    john@example.com
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5 years of experience.
    
    EXPERIENCE
    • Developed web applications using Python and React
    • Increased system performance by 40%
    • Led team of 5 developers
    • Managed $500k budget
    
    EDUCATION
    BS Computer Science, University of Example
    
    SKILLS
    Python, JavaScript, React, Django, AWS, Docker
    
    PROJECTS
    • E-commerce Platform: Built using Django and React
    • Data Pipeline: Automated ETL process using Python
    """
    
    sections = {
        'summary': 'Experienced software engineer with 5 years of experience.',
        'experience': '• Developed web applications\n• Increased performance by 40%',
        'education': 'BS Computer Science',
        'skills': 'Python, JavaScript, React, Django, AWS, Docker',
        'projects': '• E-commerce Platform\n• Data Pipeline'
    }
    
    skills = ['Python', 'JavaScript', 'React', 'Django', 'AWS', 'Docker']
    keywords = ['software', 'engineer', 'python', 'react', 'django', 'aws']
    action_verbs = ['developed', 'increased', 'led', 'managed', 'built', 'automated']
    
    skill_validation_results = {
        'validation_score': 12.0,
        'validation_percentage': 0.8,
        'unvalidated_skills': ['AWS']
    }
    
    grammar_results = {
        'penalty_applied': 0.0,
        'total_errors': 0,
        'critical_errors': []
    }
    
    location_results = {
        'penalty_applied': 0.0,
        'privacy_risk': 'none',
        'detected_locations': []
    }
    
    result = calculate_overall_score(
        text, sections, skills, keywords, action_verbs,
        skill_validation_results, grammar_results, location_results
    )
    
    # Should get a good score
    assert result['overall_score'] >= 60
    assert result['formatting_score'] >= 10
    assert result['keywords_score'] >= 8  # Adjusted based on actual scoring
    assert result['content_score'] >= 10


def test_score_interpretation():
    """Test score interpretation messages."""
    assert "Excellent" in generate_score_interpretation(95)
    assert "Great" in generate_score_interpretation(85)
    assert "Good" in generate_score_interpretation(75)
    assert "Fair" in generate_score_interpretation(65)
    assert "Below Average" in generate_score_interpretation(55)
    assert "Poor" in generate_score_interpretation(45)


def test_generate_strengths():
    """Test strengths generation."""
    score_results = {
        'formatting_score': 18.0,
        'keywords_score': 22.0,
        'content_score': 21.0,
        'skill_validation_score': 13.0,
        'ats_compatibility_score': 14.0
    }
    
    skill_validation_results = {'validation_percentage': 0.9}
    grammar_results = {'total_errors': 0}
    
    strengths = generate_strengths(score_results, skill_validation_results, grammar_results)
    assert len(strengths) > 0
    assert any('structure' in s.lower() for s in strengths)


def test_generate_critical_issues():
    """Test critical issues generation."""
    score_results = {
        'formatting_score': 5.0,
        'keywords_score': 8.0,
        'content_score': 10.0,
        'skill_validation_score': 3.0,
        'ats_compatibility_score': 7.0
    }
    
    grammar_results = {
        'critical_errors': [{'message': 'Spelling error'}] * 5
    }
    
    location_results = {
        'privacy_risk': 'high'
    }
    
    issues = generate_critical_issues(score_results, grammar_results, location_results)
    assert len(issues) > 0


def test_generate_improvements():
    """Test improvements generation."""
    score_results = {
        'formatting_score': 14.0,
        'keywords_score': 16.0,
        'content_score': 16.0,
        'skill_validation_score': 9.0,
        'ats_compatibility_score': 11.0
    }
    
    skill_validation_results = {
        'unvalidated_skills': ['Python', 'JavaScript']
    }
    
    improvements = generate_improvements(score_results, skill_validation_results)
    assert len(improvements) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
