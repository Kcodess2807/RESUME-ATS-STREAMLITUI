"""
Unit Tests for Progress Indicator Module

Tests the progress tracking functionality including initialization,
updates, completion, and stage management.

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock streamlit before importing the module
sys.modules['streamlit'] = MagicMock()

from utils.progress_indicator import (
    initialize_progress,
    update_progress,
    complete_progress,
    get_current_progress,
    get_stage_names,
    get_stage_info,
    PROCESSING_STAGES
)


class TestProgressIndicator:
    """Test suite for progress indicator functionality"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        # Mock session state
        import streamlit as st
        st.session_state = {}
    
    def test_initialize_progress_sets_zero_percent(self):
        """
        Test that initialize_progress sets progress to 0%.
        Requirements: 4.1 - Progress initialization at zero percent
        """
        import streamlit as st
        
        initialize_progress()
        
        assert st.session_state['progress_percent'] == 0
        assert st.session_state['progress_stage'] is None
        assert st.session_state['progress_stage_index'] == -1
    
    def test_initialize_progress_resets_existing_state(self):
        """
        Test that initialize_progress resets existing progress state.
        Requirements: 4.1 - Progress initialization
        """
        import streamlit as st
        
        # Set some existing state
        st.session_state['progress_percent'] = 50
        st.session_state['progress_stage'] = {'name': 'Test'}
        st.session_state['progress_stage_index'] = 3
        
        # Initialize should reset
        initialize_progress()
        
        assert st.session_state['progress_percent'] == 0
        assert st.session_state['progress_stage'] is None
        assert st.session_state['progress_stage_index'] == -1
    
    def test_update_progress_sets_stage(self):
        """
        Test that update_progress correctly sets the stage.
        Requirements: 4.4 - Stage identification
        """
        import streamlit as st
        
        initialize_progress()
        update_progress("Text Extraction")
        
        assert st.session_state['progress_stage'] is not None
        assert st.session_state['progress_stage']['name'] == "Text Extraction"
        assert st.session_state['progress_stage']['emoji'] == "📄"
        assert st.session_state['progress_percent'] == 10  # Start of Text Extraction stage
    
    def test_update_progress_with_custom_percent(self):
        """
        Test that update_progress accepts custom percentage.
        Requirements: 4.2 - Progress updates with percentage
        """
        import streamlit as st
        
        initialize_progress()
        update_progress("NLP Processing", 35)
        
        assert st.session_state['progress_percent'] == 35
        assert st.session_state['progress_stage']['name'] == "NLP Processing"
    
    def test_update_progress_clamps_to_stage_range(self):
        """
        Test that update_progress clamps percentage to stage range.
        Requirements: 4.2 - Progress updates
        """
        import streamlit as st
        
        initialize_progress()
        
        # Try to set percentage beyond stage range
        update_progress("Text Extraction", 50)  # Text Extraction is 10-25%
        
        # Should be clamped to stage end
        assert st.session_state['progress_percent'] == 25
    
    def test_update_progress_maintains_monotonicity(self):
        """
        Test that progress never decreases (monotonicity).
        Requirements: 4.2 - Progress monotonicity
        """
        import streamlit as st
        
        initialize_progress()
        
        # Set progress to 50%
        update_progress("Skill Validation", 50)
        assert st.session_state['progress_percent'] == 50
        
        # Try to update to earlier stage with lower percentage
        update_progress("Text Extraction", 15)
        
        # Progress should not decrease
        assert st.session_state['progress_percent'] == 50
    
    def test_update_progress_ignores_invalid_stage(self):
        """
        Test that update_progress handles invalid stage names gracefully.
        """
        import streamlit as st
        
        initialize_progress()
        initial_percent = st.session_state['progress_percent']
        
        # Try to update with invalid stage
        update_progress("Invalid Stage Name")
        
        # State should remain unchanged
        assert st.session_state['progress_percent'] == initial_percent
        assert st.session_state['progress_stage'] is None
    
    def test_complete_progress_sets_hundred_percent(self):
        """
        Test that complete_progress sets progress to 100%.
        Requirements: 4.3 - Progress completion at one hundred percent
        """
        import streamlit as st
        
        initialize_progress()
        complete_progress()
        
        assert st.session_state['progress_percent'] == 100
        assert st.session_state['progress_stage'] is not None
        assert st.session_state['progress_stage']['name'] == "Generating Results"
    
    def test_get_current_progress_returns_state(self):
        """
        Test that get_current_progress returns current state.
        """
        import streamlit as st
        
        initialize_progress()
        update_progress("Grammar Check", 65)
        
        progress = get_current_progress()
        
        assert progress['percent'] == 65
        assert progress['stage']['name'] == "Grammar Check"
        assert progress['stage_index'] >= 0
    
    def test_get_stage_names_returns_all_stages(self):
        """
        Test that get_stage_names returns all stage names.
        Requirements: 4.4 - Stage identification
        """
        stage_names = get_stage_names()
        
        assert len(stage_names) == len(PROCESSING_STAGES)
        assert "File Validation" in stage_names
        assert "Text Extraction" in stage_names
        assert "Generating Results" in stage_names
    
    def test_get_stage_info_returns_correct_info(self):
        """
        Test that get_stage_info returns correct stage information.
        Requirements: 4.4 - Stage identification
        """
        info = get_stage_info("Skill Validation")
        
        assert info is not None
        assert info['name'] == "Skill Validation"
        assert info['emoji'] == "✅"
        assert info['start_percent'] == 45
        assert info['end_percent'] == 60
        assert 'description' in info
    
    def test_get_stage_info_returns_none_for_invalid(self):
        """
        Test that get_stage_info returns None for invalid stage names.
        """
        info = get_stage_info("Invalid Stage")
        
        assert info is None
    
    def test_all_stages_have_required_fields(self):
        """
        Test that all stages have required fields.
        Requirements: 4.4 - Stage identification with emojis
        """
        required_fields = ['name', 'emoji', 'start_percent', 'end_percent', 'description']
        
        for stage in PROCESSING_STAGES:
            for field in required_fields:
                assert field in stage, f"Stage {stage.get('name', 'unknown')} missing field: {field}"
    
    def test_stages_have_non_overlapping_ranges(self):
        """
        Test that stage percentage ranges don't overlap.
        """
        for i in range(len(PROCESSING_STAGES) - 1):
            current_stage = PROCESSING_STAGES[i]
            next_stage = PROCESSING_STAGES[i + 1]
            
            # Current stage end should equal next stage start
            assert current_stage['end_percent'] == next_stage['start_percent'], \
                f"Gap or overlap between {current_stage['name']} and {next_stage['name']}"
    
    def test_stages_cover_full_range(self):
        """
        Test that stages cover the full 0-100% range.
        """
        assert PROCESSING_STAGES[0]['start_percent'] == 0
        assert PROCESSING_STAGES[-1]['end_percent'] == 100
    
    def test_progress_through_all_stages(self):
        """
        Test progressing through all stages in sequence.
        Requirements: 4.1, 4.2, 4.3, 4.4 - Complete progress flow
        """
        import streamlit as st
        
        initialize_progress()
        assert st.session_state['progress_percent'] == 0
        
        # Progress through each stage
        for stage in PROCESSING_STAGES:
            update_progress(stage['name'])
            
            # Verify progress increased
            assert st.session_state['progress_percent'] >= stage['start_percent']
            assert st.session_state['progress_stage']['name'] == stage['name']
        
        # Complete
        complete_progress()
        assert st.session_state['progress_percent'] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
