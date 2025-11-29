"""
Realistic end-to-end test of the scoring engine.
Tests with a complete, realistic resume scenario.
"""

import pytest
from utils.scorer import calculate_overall_score


def test_realistic_resume_scoring():
    """Test scoring with a realistic, well-structured resume."""
    
    # Realistic resume text
    text = """
    Jane Smith
    jane.smith@email.com | (555) 123-4567 | linkedin.com/in/janesmith | github.com/janesmith
    San Francisco, CA
    
    PROFESSIONAL SUMMARY
    Results-driven Software Engineer with 5+ years of experience building scalable web applications.
    Expertise in Python, JavaScript, and cloud technologies. Proven track record of delivering
    high-quality solutions that improve system performance by 40% and reduce costs by $200K annually.
    
    TECHNICAL SKILLS
    Languages: Python, JavaScript, TypeScript, SQL, HTML/CSS
    Frameworks: React, Django, Flask, Node.js, Express
    Databases: PostgreSQL, MongoDB, Redis
    Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD
    Tools: Git, JIRA, Jenkins, Terraform
    
    PROFESSIONAL EXPERIENCE
    
    Senior Software Engineer | Tech Company Inc. | Jan 2021 - Present
    • Architected and developed microservices-based e-commerce platform using Python and Django
    • Improved system performance by 45% through database optimization and caching strategies
    • Led team of 4 engineers in migrating legacy monolith to cloud-native architecture
    • Reduced infrastructure costs by $250K annually by optimizing AWS resource usage
    • Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes
    
    Software Engineer | StartUp Co. | Jun 2019 - Dec 2020
    • Built RESTful APIs using Flask and PostgreSQL serving 100K+ daily active users
    • Developed React-based admin dashboard improving operational efficiency by 30%
    • Implemented automated testing suite achieving 85% code coverage
    • Collaborated with product team to deliver 15+ features on schedule
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of California, Berkeley | 2015 - 2019
    GPA: 3.8/4.0
    
    PROJECTS
    
    Open Source Contribution - Django REST Framework
    • Contributed 10+ pull requests improving API documentation and error handling
    • Technologies: Python, Django, REST APIs, Git
    
    Personal Finance Tracker
    • Built full-stack web application for expense tracking and budget management
    • Implemented data visualization using Chart.js showing spending trends
    • Technologies: React, Node.js, MongoDB, Express, Docker
    
    Machine Learning Model Deployment
    • Deployed ML model for sentiment analysis using Flask and AWS Lambda
    • Achieved 92% accuracy on test dataset with 50ms average response time
    • Technologies: Python, TensorFlow, Flask, AWS Lambda, Docker
    """
    
    # Extracted sections
    sections = {
        'summary': 'Results-driven Software Engineer with 5+ years of experience building scalable web applications. Expertise in Python, JavaScript, and cloud technologies. Proven track record of delivering high-quality solutions that improve system performance by 40% and reduce costs by $200K annually.',
        'experience': """Senior Software Engineer | Tech Company Inc. | Jan 2021 - Present
• Architected and developed microservices-based e-commerce platform using Python and Django
• Improved system performance by 45% through database optimization and caching strategies
• Led team of 4 engineers in migrating legacy monolith to cloud-native architecture
• Reduced infrastructure costs by $250K annually by optimizing AWS resource usage
• Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes

Software Engineer | StartUp Co. | Jun 2019 - Dec 2020
• Built RESTful APIs using Flask and PostgreSQL serving 100K+ daily active users
• Developed React-based admin dashboard improving operational efficiency by 30%
• Implemented automated testing suite achieving 85% code coverage
• Collaborated with product team to deliver 15+ features on schedule""",
        'education': """Bachelor of Science in Computer Science
University of California, Berkeley | 2015 - 2019
GPA: 3.8/4.0""",
        'skills': """Languages: Python, JavaScript, TypeScript, SQL, HTML/CSS
Frameworks: React, Django, Flask, Node.js, Express
Databases: PostgreSQL, MongoDB, Redis
Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD
Tools: Git, JIRA, Jenkins, Terraform""",
        'projects': """Open Source Contribution - Django REST Framework
• Contributed 10+ pull requests improving API documentation and error handling
• Technologies: Python, Django, REST APIs, Git

Personal Finance Tracker
• Built full-stack web application for expense tracking and budget management
• Implemented data visualization using Chart.js showing spending trends
• Technologies: React, Node.js, MongoDB, Express, Docker

Machine Learning Model Deployment
• Deployed ML model for sentiment analysis using Flask and AWS Lambda
• Achieved 92% accuracy on test dataset with 50ms average response time
• Technologies: Python, TensorFlow, Flask, AWS Lambda, Docker"""
    }
    
    # Extracted skills
    skills = [
        'Python', 'JavaScript', 'TypeScript', 'SQL', 'HTML/CSS',
        'React', 'Django', 'Flask', 'Node.js', 'Express',
        'PostgreSQL', 'MongoDB', 'Redis',
        'AWS', 'Docker', 'Kubernetes', 'CI/CD',
        'Git', 'JIRA', 'Jenkins', 'Terraform'
    ]
    
    # Extracted keywords
    keywords = [
        'software engineer', 'python', 'javascript', 'react', 'django',
        'flask', 'aws', 'docker', 'kubernetes', 'microservices',
        'api', 'database', 'cloud', 'devops', 'machine learning'
    ]
    
    # Detected action verbs
    action_verbs = [
        'architected', 'developed', 'improved', 'led', 'reduced',
        'implemented', 'built', 'collaborated', 'contributed',
        'deployed', 'achieved'
    ]
    
    # Skill validation results (most skills validated)
    skill_validation_results = {
        'validation_score': 13.5,  # 90% of skills validated
        'validation_percentage': 0.9,
        'validated_skills': [
            {'skill': 'Python', 'projects': ['Django REST Framework', 'ML Model Deployment']},
            {'skill': 'JavaScript', 'projects': ['Personal Finance Tracker']},
            {'skill': 'React', 'projects': ['Personal Finance Tracker']},
            {'skill': 'Django', 'projects': ['Django REST Framework']},
            {'skill': 'Flask', 'projects': ['ML Model Deployment']},
            {'skill': 'Node.js', 'projects': ['Personal Finance Tracker']},
            {'skill': 'MongoDB', 'projects': ['Personal Finance Tracker']},
            {'skill': 'Docker', 'projects': ['Personal Finance Tracker', 'ML Model Deployment']},
            {'skill': 'AWS', 'projects': ['ML Model Deployment']},
        ],
        'unvalidated_skills': ['TypeScript', 'Terraform']
    }
    
    # Grammar results (perfect grammar)
    grammar_results = {
        'penalty_applied': 0.0,
        'total_errors': 0,
        'critical_errors': [],
        'moderate_errors': [],
        'minor_errors': []
    }
    
    # Location results (acceptable city/state in header)
    location_results = {
        'penalty_applied': 0.0,
        'privacy_risk': 'none',
        'detected_locations': []
    }
    
    # Calculate score
    result = calculate_overall_score(
        text, sections, skills, keywords, action_verbs,
        skill_validation_results, grammar_results, location_results
    )
    
    # Assertions for a high-quality resume
    print(f"\nScoring Results:")
    print(f"Overall Score: {result['overall_score']}/100")
    print(f"Interpretation: {result['overall_interpretation']}")
    print(f"\nComponent Scores:")
    print(f"  Formatting: {result['formatting_score']}/20")
    print(f"  Keywords: {result['keywords_score']}/25")
    print(f"  Content: {result['content_score']}/25")
    print(f"  Skill Validation: {result['skill_validation_score']}/15")
    print(f"  ATS Compatibility: {result['ats_compatibility_score']}/15")
    print(f"\nBonuses: {result['bonuses']}")
    print(f"Penalties: {result['penalties']}")
    
    # This is a high-quality resume, should score well
    assert result['overall_score'] >= 80, f"Expected score >= 80, got {result['overall_score']}"
    
    # Check individual components
    assert result['formatting_score'] >= 15, "Should have excellent formatting"
    assert result['keywords_score'] >= 15, "Should have strong keywords"
    assert result['content_score'] >= 20, "Should have excellent content"
    assert result['skill_validation_score'] >= 12, "Should have good skill validation"
    assert result['ats_compatibility_score'] >= 13, "Should have good ATS compatibility"
    
    # Should have bonuses
    assert len(result['bonuses']) > 0, "Should have bonuses for excellent resume"
    
    # Should have no penalties
    assert len(result['penalties']) == 0, "Should have no penalties"
    
    # Interpretation should be positive
    assert any(word in result['overall_interpretation'].lower() 
               for word in ['excellent', 'great', 'good']), \
           "Should have positive interpretation"


def test_poor_resume_scoring():
    """Test scoring with a poorly structured resume."""
    
    text = "John Doe. I worked at company. I know Python."
    
    sections = {
        'summary': '',
        'experience': 'I worked at company',
        'education': '',
        'skills': 'Python',
        'projects': ''
    }
    
    skills = ['Python']
    keywords = ['python', 'worked']
    action_verbs = []
    
    skill_validation_results = {
        'validation_score': 0.0,
        'validation_percentage': 0.0,
        'validated_skills': [],
        'unvalidated_skills': ['Python']
    }
    
    grammar_results = {
        'penalty_applied': 10.0,
        'total_errors': 5,
        'critical_errors': [{'message': 'error'}] * 2,
        'moderate_errors': [{'message': 'error'}] * 3,
        'minor_errors': []
    }
    
    location_results = {
        'penalty_applied': 5.0,
        'privacy_risk': 'high',
        'detected_locations': [{'text': '123 Main St', 'type': 'address'}]
    }
    
    result = calculate_overall_score(
        text, sections, skills, keywords, action_verbs,
        skill_validation_results, grammar_results, location_results
    )
    
    print(f"\nPoor Resume Scoring Results:")
    print(f"Overall Score: {result['overall_score']}/100")
    print(f"Interpretation: {result['overall_interpretation']}")
    
    # Poor resume should score low
    assert result['overall_score'] < 50, f"Expected score < 50, got {result['overall_score']}"
    
    # Should have penalties
    assert len(result['penalties']) > 0, "Should have penalties"
    
    # Interpretation should indicate issues
    assert any(word in result['overall_interpretation'].lower() 
               for word in ['poor', 'below', 'fair']), \
           "Should have negative interpretation"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
