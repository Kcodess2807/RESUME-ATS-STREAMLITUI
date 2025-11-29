"""
Integration tests for the scoring engine with other modules.
Tests that the scorer works correctly with real data from other components.
"""

import pytest
from utils.scorer import calculate_overall_score


def test_scorer_with_minimal_data():
    """Test scorer with minimal valid data."""
    text = "Simple resume text"
    sections = {
        'summary': '',
        'experience': 'Work experience',
        'education': 'Education',
        'skills': 'Python',
        'projects': ''
    }
    skills = ['Python']
    keywords = ['python', 'work']
    action_verbs = []
    
    skill_validation_results = {
        'validation_score': 0.0,
        'validation_percentage': 0.0,
        'unvalidated_skills': ['Python']
    }
    
    grammar_results = {
        'penalty_applied': 0.0,
        'total_errors': 0,
        'critical_errors': [],
        'moderate_errors': [],
        'minor_errors': []
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
    
    # Verify all required fields are present
    assert 'overall_score' in result
    assert 'overall_interpretation' in result
    assert 'formatting_score' in result
    assert 'keywords_score' in result
    assert 'content_score' in result
    assert 'skill_validation_score' in result
    assert 'ats_compatibility_score' in result
    assert 'component_messages' in result
    assert 'penalties' in result
    assert 'bonuses' in result
    
    # Verify score bounds
    assert 0 <= result['overall_score'] <= 100
    assert isinstance(result['overall_interpretation'], str)


def test_scorer_with_penalties():
    """Test scorer applies penalties correctly."""
    text = "Resume with issues"
    sections = {
        'summary': '',
        'experience': 'Work',
        'education': 'School',
        'skills': 'Skill',
        'projects': ''
    }
    skills = ['Skill']
    keywords = ['work']
    action_verbs = []
    
    skill_validation_results = {
        'validation_score': 0.0,
        'validation_percentage': 0.0,
        'unvalidated_skills': ['Skill']
    }
    
    # High grammar penalty
    grammar_results = {
        'penalty_applied': 15.0,
        'total_errors': 10,
        'critical_errors': [{'message': 'error'}] * 3,
        'moderate_errors': [],
        'minor_errors': []
    }
    
    # High location penalty
    location_results = {
        'penalty_applied': 5.0,
        'privacy_risk': 'high',
        'detected_locations': [{'text': '123 Main St', 'type': 'address'}]
    }
    
    result = calculate_overall_score(
        text, sections, skills, keywords, action_verbs,
        skill_validation_results, grammar_results, location_results
    )
    
    # Verify penalties are tracked
    assert 'grammar' in result['penalties']
    assert 'location_privacy' in result['penalties']
    assert result['penalties']['grammar'] == 15.0
    assert result['penalties']['location_privacy'] == 5.0


def test_scorer_with_bonuses():
    """Test scorer applies bonuses correctly."""
    text = "Excellent resume"
    sections = {
        'summary': 'Summary text',
        'experience': 'Work experience',
        'education': 'Education',
        'skills': 'Python, JavaScript',
        'projects': 'Project details'
    }
    skills = ['Python', 'JavaScript']
    keywords = ['python', 'javascript']
    action_verbs = ['developed', 'created']
    
    # Excellent skill validation
    skill_validation_results = {
        'validation_score': 15.0,
        'validation_percentage': 0.95,
        'unvalidated_skills': []
    }
    
    # Perfect grammar
    grammar_results = {
        'penalty_applied': 0.0,
        'total_errors': 0,
        'critical_errors': [],
        'moderate_errors': [],
        'minor_errors': []
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
    
    # Verify bonuses are applied
    assert len(result['bonuses']) > 0
    assert 'excellent_skill_validation' in result['bonuses'] or 'good_skill_validation' in result['bonuses']
    assert 'perfect_grammar' in result['bonuses']


def test_scorer_with_jd_keywords():
    """Test scorer with job description keywords."""
    text = "Resume text"
    sections = {
        'summary': '',
        'experience': 'Work',
        'education': 'School',
        'skills': 'Python, JavaScript, React',
        'projects': ''
    }
    skills = ['Python', 'JavaScript', 'React']
    keywords = ['python', 'javascript', 'react', 'web']
    action_verbs = []
    
    # JD keywords that overlap with resume
    jd_keywords = ['python', 'javascript', 'react', 'django', 'aws']
    
    skill_validation_results = {
        'validation_score': 10.0,
        'validation_percentage': 0.67,
        'unvalidated_skills': ['React']
    }
    
    grammar_results = {
        'penalty_applied': 0.0,
        'total_errors': 0,
        'critical_errors': [],
        'moderate_errors': [],
        'minor_errors': []
    }
    
    location_results = {
        'penalty_applied': 0.0,
        'privacy_risk': 'none',
        'detected_locations': []
    }
    
    result = calculate_overall_score(
        text, sections, skills, keywords, action_verbs,
        skill_validation_results, grammar_results, location_results,
        jd_keywords=jd_keywords
    )
    
    # Keywords score should benefit from JD matching
    assert result['keywords_score'] > 0


def test_component_messages_present():
    """Test that component messages are generated."""
    text = "Resume"
    sections = {'experience': 'Work', 'education': 'School', 'skills': 'Skills', 'summary': '', 'projects': ''}
    skills = ['Skill']
    keywords = ['keyword']
    action_verbs = []
    
    skill_validation_results = {
        'validation_score': 5.0,
        'validation_percentage': 0.5,
        'unvalidated_skills': []
    }
    
    grammar_results = {
        'penalty_applied': 0.0,
        'total_errors': 0,
        'critical_errors': [],
        'moderate_errors': [],
        'minor_errors': []
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
    
    # Verify all component messages are present
    assert 'formatting' in result['component_messages']
    assert 'keywords' in result['component_messages']
    assert 'content' in result['component_messages']
    assert 'skill_validation' in result['component_messages']
    assert 'ats_compatibility' in result['component_messages']
    
    # All messages should be non-empty strings
    for message in result['component_messages'].values():
        assert isinstance(message, str)
        assert len(message) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
