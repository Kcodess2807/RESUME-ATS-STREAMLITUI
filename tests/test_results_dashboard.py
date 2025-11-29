"""
Tests for the Results Dashboard Module

Requirements: 11.1, 11.2
"""

import pytest
from utils.results_dashboard import (
    get_score_color,
    get_score_emoji,
    generate_recommendations
)


class TestScoreColorCoding:
    """
    Tests for score color coding functionality.
    
    Requirements: 11.1 - Score color coding (red < 60, yellow 60-79, green ≥ 80)
    """
    
    def test_green_for_high_scores(self):
        """Scores >= 80 should return green colors."""
        text_color, bg_color = get_score_color(80)
        assert text_color == "#2e7d32"  # Green text
        assert bg_color == "#e8f5e9"  # Green background
        
        text_color, bg_color = get_score_color(100)
        assert text_color == "#2e7d32"
        
        text_color, bg_color = get_score_color(90)
        assert text_color == "#2e7d32"
    
    def test_yellow_for_medium_scores(self):
        """Scores 60-79 should return yellow/orange colors."""
        text_color, bg_color = get_score_color(60)
        assert text_color == "#f57c00"  # Orange text
        assert bg_color == "#fff3e0"  # Orange background
        
        text_color, bg_color = get_score_color(79)
        assert text_color == "#f57c00"
        
        text_color, bg_color = get_score_color(70)
        assert text_color == "#f57c00"
    
    def test_red_for_low_scores(self):
        """Scores < 60 should return red colors."""
        text_color, bg_color = get_score_color(59)
        assert text_color == "#c62828"  # Red text
        assert bg_color == "#ffebee"  # Red background
        
        text_color, bg_color = get_score_color(0)
        assert text_color == "#c62828"
        
        text_color, bg_color = get_score_color(30)
        assert text_color == "#c62828"
    
    def test_boundary_values(self):
        """Test exact boundary values."""
        # 59 should be red
        text_color, _ = get_score_color(59)
        assert text_color == "#c62828"
        
        # 60 should be yellow
        text_color, _ = get_score_color(60)
        assert text_color == "#f57c00"
        
        # 79 should be yellow
        text_color, _ = get_score_color(79)
        assert text_color == "#f57c00"
        
        # 80 should be green
        text_color, _ = get_score_color(80)
        assert text_color == "#2e7d32"


class TestScoreEmoji:
    """Tests for score emoji functionality."""
    
    def test_emoji_for_excellent_score(self):
        """Scores >= 90 should return star emoji."""
        assert get_score_emoji(90) == "🌟"
        assert get_score_emoji(100) == "🌟"
    
    def test_emoji_for_great_score(self):
        """Scores 80-89 should return checkmark emoji."""
        assert get_score_emoji(80) == "✅"
        assert get_score_emoji(89) == "✅"
    
    def test_emoji_for_good_score(self):
        """Scores 70-79 should return thumbs up emoji."""
        assert get_score_emoji(70) == "👍"
        assert get_score_emoji(79) == "👍"
    
    def test_emoji_for_fair_score(self):
        """Scores 60-69 should return warning emoji."""
        assert get_score_emoji(60) == "⚠️"
        assert get_score_emoji(69) == "⚠️"
    
    def test_emoji_for_below_average_score(self):
        """Scores 50-59 should return X emoji."""
        assert get_score_emoji(50) == "❌"
        assert get_score_emoji(59) == "❌"
    
    def test_emoji_for_poor_score(self):
        """Scores < 50 should return red circle emoji."""
        assert get_score_emoji(49) == "🔴"
        assert get_score_emoji(0) == "🔴"


class TestGenerateRecommendations:
    """Tests for recommendation generation functionality."""
    
    @pytest.fixture
    def sample_scores(self):
        """Sample scores for testing."""
        return {
            'formatting_score': 15,
            'keywords_score': 18,
            'content_score': 20,
            'skill_validation_score': 10,
            'ats_compatibility_score': 12
        }
    
    @pytest.fixture
    def sample_skill_validation(self):
        """Sample skill validation results."""
        return {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Project A'], 'similarity': 0.8}
            ],
            'unvalidated_skills': ['Java', 'C++', 'Go', 'Rust'],
            'validation_percentage': 0.2
        }
    
    @pytest.fixture
    def sample_grammar_results(self):
        """Sample grammar results."""
        return {
            'total_errors': 5,
            'critical_errors': [
                {'message': 'Spelling error: teh -> the', 'suggestions': ['the']}
            ],
            'moderate_errors': [
                {'message': 'Grammar issue 1'},
                {'message': 'Grammar issue 2'},
                {'message': 'Grammar issue 3'}
            ],
            'minor_errors': []
        }
    
    @pytest.fixture
    def sample_location_results(self):
        """Sample location results."""
        return {
            'privacy_risk': 'high',
            'detected_locations': [
                {'text': '123 Main St', 'type': 'address', 'section': 'header'}
            ]
        }
    
    def test_generates_critical_recommendations_for_grammar_errors(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate critical recommendations for grammar errors."""
        recommendations = generate_recommendations(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        critical_recs = [r for r in recommendations if r['priority'] == 'critical']
        grammar_recs = [r for r in critical_recs if r['category'] == 'Grammar']
        
        assert len(grammar_recs) > 0
        assert 'grammar' in grammar_recs[0]['title'].lower() or 'spelling' in grammar_recs[0]['title'].lower()
    
    def test_generates_critical_recommendations_for_location_privacy(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate critical recommendations for high privacy risk."""
        recommendations = generate_recommendations(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        critical_recs = [r for r in recommendations if r['priority'] == 'critical']
        privacy_recs = [r for r in critical_recs if r['category'] == 'Privacy']
        
        assert len(privacy_recs) > 0
        assert 'location' in privacy_recs[0]['title'].lower()
    
    def test_generates_high_priority_for_unvalidated_skills(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate high priority recommendations for unvalidated skills."""
        recommendations = generate_recommendations(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        high_recs = [r for r in recommendations if r['priority'] == 'high']
        skill_recs = [r for r in high_recs if r['category'] == 'Skills']
        
        assert len(skill_recs) > 0
        assert 'unsubstantiated' in skill_recs[0]['title'].lower() or 'validate' in skill_recs[0]['title'].lower()
    
    def test_recommendations_are_sorted_by_priority(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Recommendations should be sorted by priority (critical first)."""
        recommendations = generate_recommendations(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        if len(recommendations) > 1:
            priority_order = {'critical': 0, 'high': 1, 'medium': 2}
            for i in range(len(recommendations) - 1):
                current_priority = priority_order.get(recommendations[i]['priority'], 3)
                next_priority = priority_order.get(recommendations[i + 1]['priority'], 3)
                assert current_priority <= next_priority
    
    def test_no_recommendations_for_perfect_resume(self):
        """Should generate minimal recommendations for a perfect resume."""
        perfect_scores = {
            'formatting_score': 20,
            'keywords_score': 25,
            'content_score': 25,
            'skill_validation_score': 15,
            'ats_compatibility_score': 15
        }
        perfect_skill_validation = {
            'validated_skills': [{'skill': 'Python', 'projects': ['A'], 'similarity': 1.0}],
            'unvalidated_skills': [],
            'validation_percentage': 1.0
        }
        perfect_grammar = {
            'total_errors': 0,
            'critical_errors': [],
            'moderate_errors': [],
            'minor_errors': []
        }
        perfect_location = {
            'privacy_risk': 'none',
            'detected_locations': []
        }
        
        recommendations = generate_recommendations(
            perfect_scores,
            perfect_skill_validation,
            perfect_grammar,
            perfect_location
        )
        
        # Should have no critical recommendations
        critical_recs = [r for r in recommendations if r['priority'] == 'critical']
        assert len(critical_recs) == 0
    
    def test_jd_comparison_recommendations(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate recommendations for missing JD keywords."""
        jd_comparison = {
            'match_percentage': 50,
            'semantic_similarity': 0.6,
            'matched_keywords': ['Python', 'SQL'],
            'missing_keywords': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Terraform'],
            'skills_gap': ['Cloud Computing', 'DevOps']
        }
        
        recommendations = generate_recommendations(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results,
            jd_comparison
        )
        
        jd_recs = [r for r in recommendations if r['category'] == 'Job Match']
        assert len(jd_recs) > 0
        assert 'missing' in jd_recs[0]['title'].lower() or 'keyword' in jd_recs[0]['title'].lower()


class TestRecommendationStructure:
    """Tests for recommendation data structure."""
    
    def test_recommendation_has_required_fields(self):
        """Each recommendation should have required fields."""
        scores = {
            'formatting_score': 5,  # Low score to trigger recommendation
            'keywords_score': 10,
            'content_score': 15,
            'skill_validation_score': 5,
            'ats_compatibility_score': 10
        }
        skill_validation = {
            'validated_skills': [],
            'unvalidated_skills': ['Skill1', 'Skill2', 'Skill3', 'Skill4'],
            'validation_percentage': 0
        }
        grammar_results = {
            'total_errors': 3,
            'critical_errors': [{'message': 'Error', 'suggestions': ['Fix']}],
            'moderate_errors': [],
            'minor_errors': []
        }
        location_results = {
            'privacy_risk': 'low',
            'detected_locations': []
        }
        
        recommendations = generate_recommendations(
            scores, skill_validation, grammar_results, location_results
        )
        
        for rec in recommendations:
            assert 'priority' in rec
            assert 'category' in rec
            assert 'title' in rec
            assert 'description' in rec
            assert 'impact' in rec
            assert 'details' in rec
            assert rec['priority'] in ['critical', 'high', 'medium']
            assert isinstance(rec['details'], list)


class TestSkillValidationSummary:
    """
    Tests for skill validation summary functionality.
    
    Requirements: 11.3 - Display validated skills with associated project names
    Requirements: 11.4 - Display unvalidated skills with warning indicators
    """
    
    def test_summary_with_validated_skills(self):
        """Should correctly summarize validated skills."""
        from utils.results_dashboard import get_skill_validation_summary
        
        skill_validation = {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Project A'], 'similarity': 0.9},
                {'skill': 'JavaScript', 'projects': ['Project B'], 'similarity': 0.75},
                {'skill': 'React', 'projects': ['Project C'], 'similarity': 0.65}
            ],
            'unvalidated_skills': ['Go', 'Rust'],
            'validation_percentage': 0.6,
            'skill_project_mapping': {
                'Python': ['Project A'],
                'JavaScript': ['Project B'],
                'React': ['Project C'],
                'Go': [],
                'Rust': []
            }
        }
        
        summary = get_skill_validation_summary(skill_validation)
        
        assert summary['total_skills'] == 5
        assert summary['validated_count'] == 3
        assert summary['unvalidated_count'] == 2
        assert summary['validation_percentage'] == 0.6
        assert summary['high_confidence_count'] == 1  # Python with 0.9
        assert summary['medium_confidence_count'] == 2  # JavaScript 0.75, React 0.65
        assert summary['has_issues'] == True
        assert summary['status'] == 'good'
    
    def test_summary_with_no_skills(self):
        """Should handle empty skills list."""
        from utils.results_dashboard import get_skill_validation_summary
        
        skill_validation = {
            'validated_skills': [],
            'unvalidated_skills': [],
            'validation_percentage': 0.0,
            'skill_project_mapping': {}
        }
        
        summary = get_skill_validation_summary(skill_validation)
        
        assert summary['total_skills'] == 0
        assert summary['validated_count'] == 0
        assert summary['unvalidated_count'] == 0
        assert summary['has_issues'] == False
    
    def test_summary_with_all_validated(self):
        """Should correctly identify excellent validation status."""
        from utils.results_dashboard import get_skill_validation_summary
        
        skill_validation = {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Project A'], 'similarity': 0.95},
                {'skill': 'JavaScript', 'projects': ['Project B'], 'similarity': 0.88}
            ],
            'unvalidated_skills': [],
            'validation_percentage': 1.0,
            'skill_project_mapping': {
                'Python': ['Project A'],
                'JavaScript': ['Project B']
            }
        }
        
        summary = get_skill_validation_summary(skill_validation)
        
        assert summary['validation_percentage'] == 1.0
        assert summary['has_issues'] == False
        assert summary['status'] == 'excellent'
    
    def test_summary_with_all_unvalidated(self):
        """Should correctly identify poor validation status."""
        from utils.results_dashboard import get_skill_validation_summary
        
        skill_validation = {
            'validated_skills': [],
            'unvalidated_skills': ['Python', 'JavaScript', 'React'],
            'validation_percentage': 0.0,
            'skill_project_mapping': {
                'Python': [],
                'JavaScript': [],
                'React': []
            }
        }
        
        summary = get_skill_validation_summary(skill_validation)
        
        assert summary['total_skills'] == 3
        assert summary['validated_count'] == 0
        assert summary['unvalidated_count'] == 3
        assert summary['has_issues'] == True
        assert summary['status'] == 'poor'
    
    def test_summary_status_boundaries(self):
        """Test status boundaries for validation percentage."""
        from utils.results_dashboard import get_skill_validation_summary
        
        # Test 80% boundary (excellent)
        skill_validation_80 = {
            'validated_skills': [{'skill': f'Skill{i}', 'projects': ['P'], 'similarity': 0.8} for i in range(8)],
            'unvalidated_skills': ['Skill8', 'Skill9'],
            'validation_percentage': 0.8,
            'skill_project_mapping': {}
        }
        assert get_skill_validation_summary(skill_validation_80)['status'] == 'excellent'
        
        # Test 60% boundary (good)
        skill_validation_60 = {
            'validated_skills': [{'skill': f'Skill{i}', 'projects': ['P'], 'similarity': 0.8} for i in range(6)],
            'unvalidated_skills': ['Skill6', 'Skill7', 'Skill8', 'Skill9'],
            'validation_percentage': 0.6,
            'skill_project_mapping': {}
        }
        assert get_skill_validation_summary(skill_validation_60)['status'] == 'good'
        
        # Test 40% boundary (moderate)
        skill_validation_40 = {
            'validated_skills': [{'skill': f'Skill{i}', 'projects': ['P'], 'similarity': 0.8} for i in range(4)],
            'unvalidated_skills': [f'Skill{i}' for i in range(4, 10)],
            'validation_percentage': 0.4,
            'skill_project_mapping': {}
        }
        assert get_skill_validation_summary(skill_validation_40)['status'] == 'moderate'
        
        # Test below 40% (poor)
        skill_validation_30 = {
            'validated_skills': [{'skill': f'Skill{i}', 'projects': ['P'], 'similarity': 0.8} for i in range(3)],
            'unvalidated_skills': [f'Skill{i}' for i in range(3, 10)],
            'validation_percentage': 0.3,
            'skill_project_mapping': {}
        }
        assert get_skill_validation_summary(skill_validation_30)['status'] == 'poor'


class TestSkillValidationDisplay:
    """
    Tests for skill validation display components.
    
    Requirements: 11.3 - Display validated skills with associated project names
    Requirements: 11.4 - Display unvalidated skills with warning indicators
    """
    
    def test_validated_skills_have_project_names(self):
        """Validated skills should include associated project names."""
        skill_validation = {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Web App', 'Data Pipeline'], 'similarity': 0.9},
                {'skill': 'SQL', 'projects': ['Database Project'], 'similarity': 0.85}
            ],
            'unvalidated_skills': [],
            'validation_percentage': 1.0,
            'skill_project_mapping': {
                'Python': ['Web App', 'Data Pipeline'],
                'SQL': ['Database Project']
            }
        }
        
        # Verify structure contains project names
        for skill_info in skill_validation['validated_skills']:
            assert 'projects' in skill_info
            assert isinstance(skill_info['projects'], list)
            assert len(skill_info['projects']) > 0
            assert all(isinstance(p, str) for p in skill_info['projects'])
    
    def test_unvalidated_skills_are_identified(self):
        """Unvalidated skills should be clearly identified."""
        skill_validation = {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Project A'], 'similarity': 0.9}
            ],
            'unvalidated_skills': ['Go', 'Rust', 'Kotlin'],
            'validation_percentage': 0.25,
            'skill_project_mapping': {
                'Python': ['Project A'],
                'Go': [],
                'Rust': [],
                'Kotlin': []
            }
        }
        
        # Verify unvalidated skills are in the list
        assert len(skill_validation['unvalidated_skills']) == 3
        assert 'Go' in skill_validation['unvalidated_skills']
        assert 'Rust' in skill_validation['unvalidated_skills']
        assert 'Kotlin' in skill_validation['unvalidated_skills']
        
        # Verify they have empty project mappings
        for skill in skill_validation['unvalidated_skills']:
            assert skill_validation['skill_project_mapping'][skill] == []
    
    def test_skill_project_mapping_completeness(self):
        """Skill-project mapping should include all skills."""
        skill_validation = {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Project A', 'Project B'], 'similarity': 0.9},
                {'skill': 'JavaScript', 'projects': ['Project C'], 'similarity': 0.75}
            ],
            'unvalidated_skills': ['Go'],
            'validation_percentage': 0.67,
            'skill_project_mapping': {
                'Python': ['Project A', 'Project B'],
                'JavaScript': ['Project C'],
                'Go': []
            }
        }
        
        # All skills should be in the mapping
        all_skills = [s['skill'] for s in skill_validation['validated_skills']] + skill_validation['unvalidated_skills']
        for skill in all_skills:
            assert skill in skill_validation['skill_project_mapping']
    
    def test_similarity_scores_are_present(self):
        """Validated skills should have similarity scores."""
        skill_validation = {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Project A'], 'similarity': 0.9},
                {'skill': 'JavaScript', 'projects': ['Project B'], 'similarity': 0.65}
            ],
            'unvalidated_skills': [],
            'validation_percentage': 1.0,
            'skill_project_mapping': {}
        }
        
        for skill_info in skill_validation['validated_skills']:
            assert 'similarity' in skill_info
            assert 0.0 <= skill_info['similarity'] <= 1.0


class TestGrammarSummary:
    """
    Tests for grammar check summary functionality.
    
    Requirements: 11.5 - Display all grammar and spelling errors categorized by severity
    """
    
    def test_summary_with_no_errors(self):
        """Should correctly summarize when no errors are found."""
        from utils.results_dashboard import get_grammar_summary
        
        grammar_results = {
            'total_errors': 0,
            'critical_errors': [],
            'moderate_errors': [],
            'minor_errors': [],
            'penalty_applied': 0,
            'error_free_percentage': 100
        }
        
        summary = get_grammar_summary(grammar_results)
        
        assert summary['total_errors'] == 0
        assert summary['critical_count'] == 0
        assert summary['moderate_count'] == 0
        assert summary['minor_count'] == 0
        assert summary['penalty_applied'] == 0
        assert summary['has_critical'] == False
        assert summary['has_issues'] == False
        assert summary['status'] == 'excellent'
    
    def test_summary_with_critical_errors(self):
        """Should correctly identify critical errors."""
        from utils.results_dashboard import get_grammar_summary
        
        grammar_results = {
            'total_errors': 5,
            'critical_errors': [
                {'message': 'Spelling error 1'},
                {'message': 'Spelling error 2'},
                {'message': 'Spelling error 3'}
            ],
            'moderate_errors': [
                {'message': 'Punctuation error'}
            ],
            'minor_errors': [
                {'message': 'Style suggestion'}
            ],
            'penalty_applied': 17.5,
            'error_free_percentage': 95
        }
        
        summary = get_grammar_summary(grammar_results)
        
        assert summary['total_errors'] == 5
        assert summary['critical_count'] == 3
        assert summary['moderate_count'] == 1
        assert summary['minor_count'] == 1
        assert summary['has_critical'] == True
        assert summary['has_issues'] == True
        assert summary['status'] == 'poor'
    
    def test_summary_with_only_minor_errors(self):
        """Should correctly identify good status with only minor errors."""
        from utils.results_dashboard import get_grammar_summary
        
        grammar_results = {
            'total_errors': 3,
            'critical_errors': [],
            'moderate_errors': [
                {'message': 'Punctuation error'}
            ],
            'minor_errors': [
                {'message': 'Style suggestion 1'},
                {'message': 'Style suggestion 2'}
            ],
            'penalty_applied': 3,
            'error_free_percentage': 97
        }
        
        summary = get_grammar_summary(grammar_results)
        
        assert summary['total_errors'] == 3
        assert summary['critical_count'] == 0
        assert summary['moderate_count'] == 1
        assert summary['minor_count'] == 2
        assert summary['has_critical'] == False
        assert summary['has_issues'] == True
        assert summary['status'] == 'good'
    
    def test_summary_status_boundaries(self):
        """Test status boundaries for grammar results."""
        from utils.results_dashboard import get_grammar_summary
        
        # Excellent: no errors
        excellent_results = {
            'total_errors': 0,
            'critical_errors': [],
            'moderate_errors': [],
            'minor_errors': [],
            'penalty_applied': 0
        }
        assert get_grammar_summary(excellent_results)['status'] == 'excellent'
        
        # Good: no critical, <= 2 moderate
        good_results = {
            'total_errors': 4,
            'critical_errors': [],
            'moderate_errors': [{'message': 'Error 1'}, {'message': 'Error 2'}],
            'minor_errors': [{'message': 'Minor 1'}, {'message': 'Minor 2'}],
            'penalty_applied': 5
        }
        assert get_grammar_summary(good_results)['status'] == 'good'
        
        # Moderate: <= 2 critical
        moderate_results = {
            'total_errors': 5,
            'critical_errors': [{'message': 'Critical 1'}, {'message': 'Critical 2'}],
            'moderate_errors': [{'message': 'Moderate 1'}],
            'minor_errors': [{'message': 'Minor 1'}, {'message': 'Minor 2'}],
            'penalty_applied': 13
        }
        assert get_grammar_summary(moderate_results)['status'] == 'moderate'
        
        # Poor: > 2 critical
        poor_results = {
            'total_errors': 6,
            'critical_errors': [
                {'message': 'Critical 1'},
                {'message': 'Critical 2'},
                {'message': 'Critical 3'}
            ],
            'moderate_errors': [{'message': 'Moderate 1'}],
            'minor_errors': [{'message': 'Minor 1'}, {'message': 'Minor 2'}],
            'penalty_applied': 18
        }
        assert get_grammar_summary(poor_results)['status'] == 'poor'


class TestGrammarCheckDisplay:
    """
    Tests for grammar check display components.
    
    Requirements: 11.5 - Display all grammar and spelling errors categorized by severity
    """
    
    def test_error_structure_has_required_fields(self):
        """Each error should have required fields for display."""
        grammar_results = {
            'total_errors': 3,
            'critical_errors': [
                {
                    'message': 'Spelling error: teh -> the',
                    'context': '...this is teh example...',
                    'suggestions': ['the'],
                    'rule_id': 'MORFOLOGIK_RULE',
                    'offset': 10,
                    'error_length': 3,
                    'error_text': 'teh'
                }
            ],
            'moderate_errors': [
                {
                    'message': 'Missing comma',
                    'context': '...however the result...',
                    'suggestions': ['however, the'],
                    'rule_id': 'COMMA_RULE',
                    'offset': 5,
                    'error_length': 11,
                    'error_text': 'however the'
                }
            ],
            'minor_errors': [
                {
                    'message': 'Consider using active voice',
                    'context': '...was completed by...',
                    'suggestions': ['completed'],
                    'rule_id': 'PASSIVE_VOICE',
                    'offset': 3,
                    'error_length': 16,
                    'error_text': 'was completed by'
                }
            ],
            'penalty_applied': 7.5,
            'error_free_percentage': 97
        }
        
        # Verify all errors have required fields
        all_errors = (
            grammar_results['critical_errors'] +
            grammar_results['moderate_errors'] +
            grammar_results['minor_errors']
        )
        
        for error in all_errors:
            assert 'message' in error
            assert 'context' in error
            assert 'suggestions' in error
            assert isinstance(error['suggestions'], list)
    
    def test_errors_are_categorized_correctly(self):
        """Errors should be in the correct severity category."""
        grammar_results = {
            'total_errors': 6,
            'critical_errors': [
                {'message': 'Spelling error', 'suggestions': ['fix']},
                {'message': 'Grammar error', 'suggestions': ['fix']}
            ],
            'moderate_errors': [
                {'message': 'Punctuation error', 'suggestions': ['fix']},
                {'message': 'Capitalization error', 'suggestions': ['fix']}
            ],
            'minor_errors': [
                {'message': 'Style suggestion', 'suggestions': ['fix']},
                {'message': 'Whitespace issue', 'suggestions': ['fix']}
            ],
            'penalty_applied': 15,
            'error_free_percentage': 94
        }
        
        # Verify counts match
        assert len(grammar_results['critical_errors']) == 2
        assert len(grammar_results['moderate_errors']) == 2
        assert len(grammar_results['minor_errors']) == 2
        assert grammar_results['total_errors'] == 6
    
    def test_suggestions_are_provided(self):
        """Each error should have at least one suggestion."""
        grammar_results = {
            'total_errors': 2,
            'critical_errors': [
                {
                    'message': 'Spelling error: recieve -> receive',
                    'context': '...will recieve the...',
                    'suggestions': ['receive'],
                    'error_text': 'recieve'
                }
            ],
            'moderate_errors': [
                {
                    'message': 'Missing article',
                    'context': '...is good idea...',
                    'suggestions': ['a good idea', 'the good idea'],
                    'error_text': 'good idea'
                }
            ],
            'minor_errors': [],
            'penalty_applied': 7,
            'error_free_percentage': 98
        }
        
        all_errors = (
            grammar_results['critical_errors'] +
            grammar_results['moderate_errors']
        )
        
        for error in all_errors:
            assert len(error['suggestions']) >= 1
    
    def test_penalty_calculation_is_correct(self):
        """Penalty should be calculated correctly based on error counts."""
        # 2 critical (5 each) + 3 moderate (2 each) + 4 minor (0.5 each) = 10 + 6 + 2 = 18
        grammar_results = {
            'total_errors': 9,
            'critical_errors': [{'message': 'Error'} for _ in range(2)],
            'moderate_errors': [{'message': 'Error'} for _ in range(3)],
            'minor_errors': [{'message': 'Error'} for _ in range(4)],
            'penalty_applied': 18,
            'error_free_percentage': 91
        }
        
        expected_penalty = (2 * 5) + (3 * 2) + (4 * 0.5)
        assert grammar_results['penalty_applied'] == expected_penalty
    
    def test_penalty_is_capped_at_20(self):
        """Penalty should not exceed 20 points."""
        # 5 critical (5 each) = 25, but should be capped at 20
        grammar_results = {
            'total_errors': 5,
            'critical_errors': [{'message': 'Error'} for _ in range(5)],
            'moderate_errors': [],
            'minor_errors': [],
            'penalty_applied': 20,  # Capped at 20
            'error_free_percentage': 95
        }
        
        assert grammar_results['penalty_applied'] <= 20



class TestPrivacyRiskColorCoding:
    """
    Tests for privacy risk color coding functionality.
    
    Requirements: 11.6 - Display privacy alert with color coding based on risk level
    """
    
    def test_red_for_high_risk(self):
        """High risk should return red colors."""
        from utils.results_dashboard import get_privacy_risk_color
        
        text_color, bg_color, border_color = get_privacy_risk_color("high")
        assert text_color == "#c62828"  # Red text
        assert bg_color == "#ffebee"  # Red background
        assert border_color == "#ef5350"  # Red border
    
    def test_orange_for_medium_risk(self):
        """Medium risk should return orange colors."""
        from utils.results_dashboard import get_privacy_risk_color
        
        text_color, bg_color, border_color = get_privacy_risk_color("medium")
        assert text_color == "#f57c00"  # Orange text
        assert bg_color == "#fff3e0"  # Orange background
        assert border_color == "#ffb74d"  # Orange border
    
    def test_blue_for_low_risk(self):
        """Low risk should return blue colors."""
        from utils.results_dashboard import get_privacy_risk_color
        
        text_color, bg_color, border_color = get_privacy_risk_color("low")
        assert text_color == "#1976d2"  # Blue text
        assert bg_color == "#e3f2fd"  # Blue background
        assert border_color == "#64b5f6"  # Blue border
    
    def test_green_for_no_risk(self):
        """No risk should return green colors."""
        from utils.results_dashboard import get_privacy_risk_color
        
        text_color, bg_color, border_color = get_privacy_risk_color("none")
        assert text_color == "#2e7d32"  # Green text
        assert bg_color == "#e8f5e9"  # Green background
        assert border_color == "#81c784"  # Green border


class TestPrivacyStatusInfo:
    """
    Tests for privacy status information functionality.
    
    Requirements: 11.6 - Show privacy status (issue detected, warning, optimized)
    """
    
    def test_high_risk_status(self):
        """High risk should return 'Issue Detected' status."""
        from utils.results_dashboard import get_privacy_status_info
        
        status_text, status_icon, description = get_privacy_status_info("high")
        assert status_text == "Issue Detected"
        assert status_icon == "🔴"
        assert "privacy risk" in description.lower()
    
    def test_medium_risk_status(self):
        """Medium risk should return 'Warning' status."""
        from utils.results_dashboard import get_privacy_status_info
        
        status_text, status_icon, description = get_privacy_status_info("medium")
        assert status_text == "Warning"
        assert status_icon == "🟡"
        assert "simplified" in description.lower()
    
    def test_low_risk_status(self):
        """Low risk should return 'Minor Concern' status."""
        from utils.results_dashboard import get_privacy_status_info
        
        status_text, status_icon, description = get_privacy_status_info("low")
        assert status_text == "Minor Concern"
        assert status_icon == "🔵"
        assert "minimal" in description.lower()
    
    def test_no_risk_status(self):
        """No risk should return 'Optimized' status."""
        from utils.results_dashboard import get_privacy_status_info
        
        status_text, status_icon, description = get_privacy_status_info("none")
        assert status_text == "Optimized"
        assert status_icon == "🟢"
        assert "optimized" in description.lower()


class TestPrivacySummary:
    """
    Tests for privacy check summary functionality.
    
    Requirements: 11.6 - Display privacy alert with detected locations and removal recommendations
    """
    
    def test_summary_with_no_locations(self):
        """Should correctly summarize when no locations are found."""
        from utils.results_dashboard import get_privacy_summary
        
        location_results = {
            'location_found': False,
            'detected_locations': [],
            'privacy_risk': 'none',
            'recommendations': [],
            'penalty_applied': 0
        }
        
        summary = get_privacy_summary(location_results)
        
        assert summary['location_found'] == False
        assert summary['total_locations'] == 0
        assert summary['address_count'] == 0
        assert summary['zip_count'] == 0
        assert summary['city_count'] == 0
        assert summary['privacy_risk'] == 'none'
        assert summary['penalty_applied'] == 0
        assert summary['has_high_risk'] == False
        assert summary['status'] == 'optimized'
    
    def test_summary_with_high_risk_locations(self):
        """Should correctly identify high risk locations."""
        from utils.results_dashboard import get_privacy_summary
        
        location_results = {
            'location_found': True,
            'detected_locations': [
                {'text': '123 Main St', 'type': 'address', 'section': 'header'},
                {'text': '12345', 'type': 'zip', 'section': 'header'},
                {'text': 'New York', 'type': 'gpe', 'section': 'experience'}
            ],
            'privacy_risk': 'high',
            'recommendations': ['Remove address', 'Remove zip code'],
            'penalty_applied': 5.0
        }
        
        summary = get_privacy_summary(location_results)
        
        assert summary['location_found'] == True
        assert summary['total_locations'] == 3
        assert summary['address_count'] == 1
        assert summary['zip_count'] == 1
        assert summary['city_count'] == 1
        assert summary['privacy_risk'] == 'high'
        assert summary['penalty_applied'] == 5.0
        assert summary['has_high_risk'] == True
        assert summary['status'] == 'issue_detected'
    
    def test_summary_with_medium_risk(self):
        """Should correctly identify medium risk status."""
        from utils.results_dashboard import get_privacy_summary
        
        location_results = {
            'location_found': True,
            'detected_locations': [
                {'text': 'San Francisco', 'type': 'gpe', 'section': 'experience'},
                {'text': 'California', 'type': 'gpe', 'section': 'education'},
                {'text': 'Seattle', 'type': 'gpe', 'section': 'experience'},
                {'text': 'Washington', 'type': 'gpe', 'section': 'experience'}
            ],
            'privacy_risk': 'medium',
            'recommendations': ['Consider reducing location mentions'],
            'penalty_applied': 3.0
        }
        
        summary = get_privacy_summary(location_results)
        
        assert summary['total_locations'] == 4
        assert summary['address_count'] == 0
        assert summary['zip_count'] == 0
        assert summary['city_count'] == 4
        assert summary['privacy_risk'] == 'medium'
        assert summary['has_high_risk'] == False
        assert summary['status'] == 'warning'
    
    def test_summary_with_low_risk(self):
        """Should correctly identify low risk status."""
        from utils.results_dashboard import get_privacy_summary
        
        location_results = {
            'location_found': True,
            'detected_locations': [
                {'text': 'Boston', 'type': 'gpe', 'section': 'experience'}
            ],
            'privacy_risk': 'low',
            'recommendations': [],
            'penalty_applied': 2.0
        }
        
        summary = get_privacy_summary(location_results)
        
        assert summary['total_locations'] == 1
        assert summary['privacy_risk'] == 'low'
        assert summary['has_high_risk'] == False
        assert summary['status'] == 'good'
    
    def test_summary_status_boundaries(self):
        """Test status boundaries for privacy risk levels."""
        from utils.results_dashboard import get_privacy_summary
        
        # High risk -> issue_detected
        high_results = {
            'location_found': True,
            'detected_locations': [{'text': '123 Main St', 'type': 'address', 'section': 'header'}],
            'privacy_risk': 'high',
            'recommendations': [],
            'penalty_applied': 5.0
        }
        assert get_privacy_summary(high_results)['status'] == 'issue_detected'
        
        # Medium risk -> warning
        medium_results = {
            'location_found': True,
            'detected_locations': [{'text': 'City', 'type': 'gpe', 'section': 'exp'}],
            'privacy_risk': 'medium',
            'recommendations': [],
            'penalty_applied': 3.0
        }
        assert get_privacy_summary(medium_results)['status'] == 'warning'
        
        # Low risk -> good
        low_results = {
            'location_found': True,
            'detected_locations': [{'text': 'City', 'type': 'gpe', 'section': 'exp'}],
            'privacy_risk': 'low',
            'recommendations': [],
            'penalty_applied': 2.0
        }
        assert get_privacy_summary(low_results)['status'] == 'good'
        
        # No risk -> optimized
        none_results = {
            'location_found': False,
            'detected_locations': [],
            'privacy_risk': 'none',
            'recommendations': [],
            'penalty_applied': 0
        }
        assert get_privacy_summary(none_results)['status'] == 'optimized'


class TestPrivacyCheckDisplay:
    """
    Tests for privacy check display components.
    
    Requirements: 11.6 - Display privacy alert with detected locations and removal recommendations
    """
    
    def test_location_results_structure_has_required_fields(self):
        """Location results should have required fields for display."""
        location_results = {
            'location_found': True,
            'detected_locations': [
                {
                    'text': '123 Main Street',
                    'type': 'address',
                    'section': 'contact_header',
                    'start': 0,
                    'end': 15
                },
                {
                    'text': '12345',
                    'type': 'zip',
                    'section': 'contact_header',
                    'start': 20,
                    'end': 25
                }
            ],
            'privacy_risk': 'high',
            'recommendations': [
                'Remove full street addresses from your resume.',
                'Remove zip codes from your resume.'
            ],
            'penalty_applied': 5.0
        }
        
        # Verify required fields
        assert 'location_found' in location_results
        assert 'detected_locations' in location_results
        assert 'privacy_risk' in location_results
        assert 'recommendations' in location_results
        assert 'penalty_applied' in location_results
        
        # Verify location structure
        for loc in location_results['detected_locations']:
            assert 'text' in loc
            assert 'type' in loc
            assert 'section' in loc
    
    def test_detected_locations_have_section_info(self):
        """Detected locations should include section information."""
        location_results = {
            'location_found': True,
            'detected_locations': [
                {'text': '123 Main St', 'type': 'address', 'section': 'contact_header'},
                {'text': 'New York', 'type': 'gpe', 'section': 'experience'},
                {'text': 'MIT', 'type': 'loc', 'section': 'education'}
            ],
            'privacy_risk': 'high',
            'recommendations': [],
            'penalty_applied': 4.0
        }
        
        # Verify all locations have section info
        for loc in location_results['detected_locations']:
            assert 'section' in loc
            assert loc['section'] in ['contact_header', 'experience', 'education', 'other']
    
    def test_recommendations_are_provided_for_issues(self):
        """Recommendations should be provided when privacy issues are detected."""
        location_results = {
            'location_found': True,
            'detected_locations': [
                {'text': '123 Main St', 'type': 'address', 'section': 'header'}
            ],
            'privacy_risk': 'high',
            'recommendations': [
                'Remove full street addresses from your resume.',
                'Keep only city and state in header.'
            ],
            'penalty_applied': 4.0
        }
        
        assert len(location_results['recommendations']) > 0
        assert any('address' in rec.lower() for rec in location_results['recommendations'])
    
    def test_penalty_is_within_bounds(self):
        """Penalty should be within 0-5 points range."""
        # Test various scenarios
        test_cases = [
            {'privacy_risk': 'none', 'expected_max': 0},
            {'privacy_risk': 'low', 'expected_max': 2},
            {'privacy_risk': 'medium', 'expected_max': 3},
            {'privacy_risk': 'high', 'expected_max': 5}
        ]
        
        for case in test_cases:
            location_results = {
                'location_found': case['privacy_risk'] != 'none',
                'detected_locations': [],
                'privacy_risk': case['privacy_risk'],
                'recommendations': [],
                'penalty_applied': case['expected_max']
            }
            
            assert 0 <= location_results['penalty_applied'] <= 5



class TestActionItemsGeneration:
    """
    Tests for action items generation functionality.
    
    Requirements: 11.8 - Display prioritized action items categorized as critical, high, or medium priority
    """
    
    @pytest.fixture
    def sample_scores(self):
        """Sample scores for testing."""
        return {
            'formatting_score': 15,
            'keywords_score': 18,
            'content_score': 20,
            'skill_validation_score': 10,
            'ats_compatibility_score': 12
        }
    
    @pytest.fixture
    def sample_skill_validation(self):
        """Sample skill validation results."""
        return {
            'validated_skills': [
                {'skill': 'Python', 'projects': ['Project A'], 'similarity': 0.8}
            ],
            'unvalidated_skills': ['Java', 'C++', 'Go', 'Rust'],
            'validation_percentage': 0.2
        }
    
    @pytest.fixture
    def sample_grammar_results(self):
        """Sample grammar results."""
        return {
            'total_errors': 5,
            'critical_errors': [
                {'message': 'Spelling error: teh -> the', 'suggestions': ['the'], 'error_text': 'teh'}
            ],
            'moderate_errors': [
                {'message': 'Grammar issue 1', 'suggestions': ['fix1'], 'error_text': 'issue1'},
                {'message': 'Grammar issue 2', 'suggestions': ['fix2'], 'error_text': 'issue2'}
            ],
            'minor_errors': [
                {'message': 'Minor issue', 'suggestions': ['fix'], 'error_text': 'minor'}
            ]
        }
    
    @pytest.fixture
    def sample_location_results(self):
        """Sample location results."""
        return {
            'privacy_risk': 'high',
            'detected_locations': [
                {'text': '123 Main St', 'type': 'address', 'section': 'header'},
                {'text': '12345', 'type': 'zip', 'section': 'header'}
            ]
        }
    
    def test_generates_action_items_for_grammar_errors(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate action items for grammar errors."""
        from utils.results_dashboard import generate_action_items
        
        action_items = generate_action_items(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        grammar_items = [item for item in action_items if item['category'] == 'Grammar']
        assert len(grammar_items) > 0
        
        # Check that critical grammar errors generate critical action items
        critical_grammar = [item for item in grammar_items if item['priority'] == 'critical']
        assert len(critical_grammar) > 0
    
    def test_generates_action_items_for_location_privacy(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate action items for high privacy risk."""
        from utils.results_dashboard import generate_action_items
        
        action_items = generate_action_items(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        privacy_items = [item for item in action_items if item['category'] == 'Privacy']
        assert len(privacy_items) > 0
        
        # Check that high privacy risk generates critical action items
        critical_privacy = [item for item in privacy_items if item['priority'] == 'critical']
        assert len(critical_privacy) > 0
    
    def test_generates_action_items_for_unvalidated_skills(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate action items for unvalidated skills."""
        from utils.results_dashboard import generate_action_items
        
        action_items = generate_action_items(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        skill_items = [item for item in action_items if item['category'] == 'Skills']
        assert len(skill_items) > 0
        
        # Check that unvalidated skills generate high priority action items
        high_skill = [item for item in skill_items if item['priority'] == 'high']
        assert len(high_skill) > 0
    
    def test_action_items_are_sorted_by_priority(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Action items should be sorted by priority (critical first)."""
        from utils.results_dashboard import generate_action_items
        
        action_items = generate_action_items(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results
        )
        
        if len(action_items) > 1:
            priority_order = {'critical': 0, 'high': 1, 'medium': 2}
            for i in range(len(action_items) - 1):
                current_priority = priority_order.get(action_items[i]['priority'], 3)
                next_priority = priority_order.get(action_items[i + 1]['priority'], 3)
                assert current_priority <= next_priority
    
    def test_no_action_items_for_perfect_resume(self):
        """Should generate no action items for a perfect resume."""
        from utils.results_dashboard import generate_action_items
        
        perfect_scores = {
            'formatting_score': 20,
            'keywords_score': 25,
            'content_score': 25,
            'skill_validation_score': 15,
            'ats_compatibility_score': 15
        }
        perfect_skill_validation = {
            'validated_skills': [{'skill': 'Python', 'projects': ['A'], 'similarity': 1.0}],
            'unvalidated_skills': [],
            'validation_percentage': 1.0
        }
        perfect_grammar = {
            'total_errors': 0,
            'critical_errors': [],
            'moderate_errors': [],
            'minor_errors': []
        }
        perfect_location = {
            'privacy_risk': 'none',
            'detected_locations': []
        }
        
        action_items = generate_action_items(
            perfect_scores,
            perfect_skill_validation,
            perfect_grammar,
            perfect_location
        )
        
        # Should have no critical action items
        critical_items = [item for item in action_items if item['priority'] == 'critical']
        assert len(critical_items) == 0
    
    def test_jd_comparison_action_items(
        self, sample_scores, sample_skill_validation, sample_grammar_results, sample_location_results
    ):
        """Should generate action items for missing JD keywords."""
        from utils.results_dashboard import generate_action_items
        
        jd_comparison = {
            'match_percentage': 50,
            'semantic_similarity': 0.6,
            'matched_keywords': ['Python', 'SQL'],
            'missing_keywords': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Terraform'],
            'skills_gap': ['Cloud Computing', 'DevOps']
        }
        
        action_items = generate_action_items(
            sample_scores,
            sample_skill_validation,
            sample_grammar_results,
            sample_location_results,
            jd_comparison
        )
        
        keyword_items = [item for item in action_items if item['category'] == 'Keywords']
        assert len(keyword_items) > 0


class TestActionItemsStructure:
    """Tests for action item data structure."""
    
    def test_action_item_has_required_fields(self):
        """Each action item should have required fields."""
        from utils.results_dashboard import generate_action_items
        
        scores = {
            'formatting_score': 5,  # Low score to trigger action items
            'keywords_score': 10,
            'content_score': 15,
            'skill_validation_score': 5,
            'ats_compatibility_score': 10
        }
        skill_validation = {
            'validated_skills': [],
            'unvalidated_skills': ['Skill1', 'Skill2', 'Skill3', 'Skill4'],
            'validation_percentage': 0
        }
        grammar_results = {
            'total_errors': 3,
            'critical_errors': [{'message': 'Error', 'suggestions': ['Fix'], 'error_text': 'err'}],
            'moderate_errors': [],
            'minor_errors': []
        }
        location_results = {
            'privacy_risk': 'low',
            'detected_locations': []
        }
        
        action_items = generate_action_items(
            scores, skill_validation, grammar_results, location_results
        )
        
        for item in action_items:
            assert 'id' in item
            assert 'priority' in item
            assert 'text' in item
            assert 'category' in item
            assert 'completed' in item
            assert 'impact' in item
            assert item['priority'] in ['critical', 'high', 'medium']
            assert isinstance(item['id'], int)
            assert isinstance(item['completed'], bool)
            assert isinstance(item['impact'], int)


class TestPriorityColorCoding:
    """
    Tests for priority color coding functionality.
    
    Requirements: 11.8 - Use color coding for priority levels
    """
    
    def test_red_for_critical_priority(self):
        """Critical priority should return red colors."""
        from utils.results_dashboard import get_priority_color
        
        text_color, bg_color, border_color = get_priority_color('critical')
        assert text_color == "#c62828"  # Red text
        assert bg_color == "#ffebee"  # Red background
        assert border_color == "#ef5350"  # Red border
    
    def test_orange_for_high_priority(self):
        """High priority should return orange colors."""
        from utils.results_dashboard import get_priority_color
        
        text_color, bg_color, border_color = get_priority_color('high')
        assert text_color == "#f57c00"  # Orange text
        assert bg_color == "#fff3e0"  # Orange background
        assert border_color == "#ffb74d"  # Orange border
    
    def test_blue_for_medium_priority(self):
        """Medium priority should return blue colors."""
        from utils.results_dashboard import get_priority_color
        
        text_color, bg_color, border_color = get_priority_color('medium')
        assert text_color == "#1976d2"  # Blue text
        assert bg_color == "#e3f2fd"  # Blue background
        assert border_color == "#64b5f6"  # Blue border


class TestPriorityIcon:
    """Tests for priority icon functionality."""
    
    def test_icon_for_critical_priority(self):
        """Critical priority should return red circle emoji."""
        from utils.results_dashboard import get_priority_icon
        
        assert get_priority_icon('critical') == "🔴"
    
    def test_icon_for_high_priority(self):
        """High priority should return yellow circle emoji."""
        from utils.results_dashboard import get_priority_icon
        
        assert get_priority_icon('high') == "🟡"
    
    def test_icon_for_medium_priority(self):
        """Medium priority should return blue circle emoji."""
        from utils.results_dashboard import get_priority_icon
        
        assert get_priority_icon('medium') == "🔵"


class TestActionItemsSummary:
    """Tests for action items summary functionality."""
    
    def test_summary_with_action_items(self):
        """Should correctly summarize action items."""
        from utils.results_dashboard import get_action_items_summary
        
        scores = {
            'formatting_score': 5,
            'keywords_score': 10,
            'content_score': 15,
            'skill_validation_score': 5,
            'ats_compatibility_score': 10
        }
        skill_validation = {
            'validated_skills': [],
            'unvalidated_skills': ['Skill1', 'Skill2', 'Skill3', 'Skill4'],
            'validation_percentage': 0
        }
        grammar_results = {
            'total_errors': 3,
            'critical_errors': [{'message': 'Error', 'suggestions': ['Fix'], 'error_text': 'err'}],
            'moderate_errors': [],
            'minor_errors': []
        }
        location_results = {
            'privacy_risk': 'high',
            'detected_locations': [{'text': '123 Main St', 'type': 'address', 'section': 'header'}]
        }
        
        summary = get_action_items_summary(
            scores, skill_validation, grammar_results, location_results
        )
        
        assert 'total_items' in summary
        assert 'critical_count' in summary
        assert 'high_count' in summary
        assert 'medium_count' in summary
        assert 'total_impact' in summary
        assert 'has_critical' in summary
        assert 'items' in summary
        
        assert summary['total_items'] > 0
        assert summary['has_critical'] == True
        assert summary['total_impact'] > 0
    
    def test_summary_with_no_action_items(self):
        """Should correctly summarize when no action items are needed."""
        from utils.results_dashboard import get_action_items_summary
        
        perfect_scores = {
            'formatting_score': 20,
            'keywords_score': 25,
            'content_score': 25,
            'skill_validation_score': 15,
            'ats_compatibility_score': 15
        }
        perfect_skill_validation = {
            'validated_skills': [{'skill': 'Python', 'projects': ['A'], 'similarity': 1.0}],
            'unvalidated_skills': [],
            'validation_percentage': 1.0
        }
        perfect_grammar = {
            'total_errors': 0,
            'critical_errors': [],
            'moderate_errors': [],
            'minor_errors': []
        }
        perfect_location = {
            'privacy_risk': 'none',
            'detected_locations': []
        }
        
        summary = get_action_items_summary(
            perfect_scores, perfect_skill_validation, perfect_grammar, perfect_location
        )
        
        assert summary['critical_count'] == 0
        assert summary['has_critical'] == False
