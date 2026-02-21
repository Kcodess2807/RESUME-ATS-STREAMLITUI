"""
Progress Indicator Module

This module provides progress tracking functionality for the resume analysis process.
It manages progress state, displays progress bars, and tracks processing stages.

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import streamlit as st
from typing import Optional, Dict, List, Tuple


# Define all processing stages with emojis and percentage ranges
# Requirements: 4.4 - Stage identification with emojis
PROCESSING_STAGES = [
    {
        "name": "File Validation",
        "emoji": "🔍",
        "start_percent": 0,
        "end_percent": 10,
        "description": "Validating file type and size"
    },
    {
        "name": "Text Extraction",
        "emoji": "📄",
        "start_percent": 10,
        "end_percent": 25,
        "description": "Extracting text from document"
    },
    {
        "name": "NLP Processing",
        "emoji": "🧠",
        "start_percent": 25,
        "end_percent": 45,
        "description": "Analyzing resume structure and content"
    },
    {
        "name": "Skill Validation",
        "emoji": "✅",
        "start_percent": 45,
        "end_percent": 60,
        "description": "Validating skills against projects"
    },
    {
        "name": "Experience Analysis",
        "emoji": "💼",
        "start_percent": 60,
        "end_percent": 75,
        "description": "Analyzing experience section quality"
    },
    {
        "name": "Location Detection",
        "emoji": "📍",
        "start_percent": 75,
        "end_percent": 85,
        "description": "Detecting privacy-sensitive information"
    },
    {
        "name": "Score Calculation",
        "emoji": "🎯",
        "start_percent": 85,
        "end_percent": 95,
        "description": "Calculating ATS compatibility scores"
    },
    {
        "name": "Generating Results",
        "emoji": "✨",
        "start_percent": 95,
        "end_percent": 100,
        "description": "Preparing recommendations and feedback"
    }
]


def initialize_progress() -> None:
    """
    Initialize progress tracking in session state.
    
    Requirements: 4.1 - Progress initialization at zero percent
    
    This function sets up the session state variables needed for progress tracking.
    It should be called before starting any analysis operation.
    """
    if 'progress_percent' not in st.session_state:
        st.session_state['progress_percent'] = 0
    
    if 'progress_stage' not in st.session_state:
        st.session_state['progress_stage'] = None
    
    if 'progress_stage_index' not in st.session_state:
        st.session_state['progress_stage_index'] = -1
    
    # Reset to initial state
    st.session_state['progress_percent'] = 0
    st.session_state['progress_stage'] = None
    st.session_state['progress_stage_index'] = -1


def update_progress(stage_name: str, percent: Optional[float] = None) -> None:
    """
    Update the progress indicator to a specific stage and percentage.
    
    Requirements: 4.2 - Progress monotonicity (never decreases)
    Requirements: 4.4 - Stage identification
    
    Args:
        stage_name: Name of the current processing stage
        percent: Optional specific percentage (0-100). If not provided,
                uses the start percentage of the stage.
    
    Note:
        Progress will only increase, never decrease, to maintain monotonicity.
    """
    # Find the stage by name
    stage_info = None
    stage_index = -1
    
    for idx, stage in enumerate(PROCESSING_STAGES):
        if stage["name"] == stage_name:
            stage_info = stage
            stage_index = idx
            break
    
    if stage_info is None:
        # Stage not found, skip update
        return
    
    # Determine the target percentage
    if percent is not None:
        # Use provided percentage, but clamp to stage range
        target_percent = max(stage_info["start_percent"], 
                           min(percent, stage_info["end_percent"]))
    else:
        # Use stage start percentage
        target_percent = stage_info["start_percent"]
    
    # Ensure monotonicity - never decrease progress
    # Requirements: 4.2 - Progress monotonicity
    current_percent = st.session_state.get('progress_percent', 0)
    if target_percent < current_percent:
        target_percent = current_percent
    
    # Update session state
    st.session_state['progress_percent'] = target_percent
    st.session_state['progress_stage'] = stage_info
    st.session_state['progress_stage_index'] = stage_index


def complete_progress() -> None:
    """
    Mark progress as complete (100%).
    
    Requirements: 4.3 - Progress completion at one hundred percent
    
    This function should be called when all processing stages are complete.
    """
    st.session_state['progress_percent'] = 100
    
    # Set to the last stage
    if PROCESSING_STAGES:
        last_stage = PROCESSING_STAGES[-1]
        st.session_state['progress_stage'] = last_stage
        st.session_state['progress_stage_index'] = len(PROCESSING_STAGES) - 1


def display_progress_bar() -> Tuple[any, any]:
    """
    Display the progress bar component with percentage and stage information.
    
    Requirements: 4.1 - Progress indicator display
    Requirements: 4.2 - Progress updates with percentage
    Requirements: 4.4 - Stage name and emoji display
    
    Returns:
        Tuple of (progress_bar, status_text) Streamlit components that can be updated
    
    Note:
        This function creates Streamlit components that display the current progress.
        The returned components can be updated by calling update_progress().
    """
    # Get current progress state
    percent = st.session_state.get('progress_percent', 0)
    stage = st.session_state.get('progress_stage', None)
    
    # Create status text container
    status_container = st.empty()
    
    # Display stage information with emoji
    if stage:
        # Requirements: 4.4 - Display stage name with emoji
        stage_text = f"{stage['emoji']} **{stage['name']}** - {stage['description']}"
        status_container.markdown(stage_text)
    else:
        status_container.markdown("⏳ **Initializing** - Preparing to analyze...")
    
    # Create progress bar
    # Requirements: 4.1, 4.2 - Progress bar with percentage display
    progress_bar = st.progress(percent / 100.0)
    
    # Display percentage
    percent_text = st.empty()
    percent_text.markdown(f"<div style='text-align: center; color: #666;'>{percent:.0f}%</div>", 
                         unsafe_allow_html=True)
    
    return progress_bar, status_container, percent_text


def get_current_progress() -> Dict:
    """
    Get the current progress state.
    
    Returns:
        Dictionary containing current progress information:
        - percent: Current percentage (0-100)
        - stage: Current stage information (dict) or None
        - stage_index: Index of current stage or -1
    """
    return {
        'percent': st.session_state.get('progress_percent', 0),
        'stage': st.session_state.get('progress_stage', None),
        'stage_index': st.session_state.get('progress_stage_index', -1)
    }


def get_stage_names() -> List[str]:
    """
    Get a list of all stage names.
    
    Returns:
        List of stage names in order
    """
    return [stage["name"] for stage in PROCESSING_STAGES]


def get_stage_info(stage_name: str) -> Optional[Dict]:
    """
    Get information about a specific stage.
    
    Args:
        stage_name: Name of the stage
    
    Returns:
        Stage information dictionary or None if not found
    """
    for stage in PROCESSING_STAGES:
        if stage["name"] == stage_name:
            return stage
    return None
