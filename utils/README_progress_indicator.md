# Progress Indicator Module

## Overview

The progress indicator module provides comprehensive progress tracking functionality for the resume analysis process. It manages progress state using Streamlit session state, displays animated progress bars, and tracks processing stages with visual feedback.

## Requirements

This module implements the following requirements:
- **4.1**: Progress initialization at zero percent
- **4.2**: Progress monotonicity (never decreases) with percentage updates
- **4.3**: Progress completion at one hundred percent
- **4.4**: Stage identification with names and emojis

## Processing Stages

The module defines 8 processing stages, each with:
- **Name**: Descriptive stage name
- **Emoji**: Visual indicator for the stage
- **Percentage Range**: Start and end percentages
- **Description**: Detailed description of what happens in this stage

### Stage Breakdown

1. **File Validation** 🔍 (0-10%)
   - Validating file type and size

2. **Text Extraction** 📄 (10-25%)
   - Extracting text from document

3. **NLP Processing** 🧠 (25-45%)
   - Analyzing resume structure and content

4. **Skill Validation** ✅ (45-60%)
   - Validating skills against projects

5. **Grammar Check** 📝 (60-75%)
   - Checking grammar and spelling

6. **Location Detection** 📍 (75-85%)
   - Detecting privacy-sensitive information

7. **Score Calculation** 🎯 (85-95%)
   - Calculating ATS compatibility scores

8. **Generating Results** ✨ (95-100%)
   - Preparing recommendations and feedback

## Key Functions

### `initialize_progress()`

Initializes progress tracking in session state. Must be called before starting any analysis operation.

**Requirements**: 4.1 - Progress initialization

```python
from utils.progress_indicator import initialize_progress

# Start of analysis
initialize_progress()
```

### `update_progress(stage_name, percent=None)`

Updates the progress indicator to a specific stage and percentage.

**Requirements**: 4.2 - Progress monotonicity, 4.4 - Stage identification

**Parameters**:
- `stage_name` (str): Name of the current processing stage
- `percent` (float, optional): Specific percentage (0-100). If not provided, uses stage start percentage.

**Features**:
- Ensures monotonicity - progress never decreases
- Automatically clamps percentage to stage range
- Updates session state with current stage information

```python
from utils.progress_indicator import update_progress

# Update to a specific stage
update_progress("Text Extraction")

# Update with specific percentage
update_progress("NLP Processing", 35)
```

### `complete_progress()`

Marks progress as complete (100%).

**Requirements**: 4.3 - Progress completion

```python
from utils.progress_indicator import complete_progress

# When all processing is done
complete_progress()
```

### `display_progress_bar()`

Displays the progress bar component with percentage and stage information.

**Requirements**: 4.1, 4.2, 4.4 - Progress display with stage information

**Returns**: Tuple of (progress_bar, status_container, percent_text) Streamlit components

```python
from utils.progress_indicator import display_progress_bar

# Display the progress bar
progress_bar, status_text, percent_text = display_progress_bar()
```

### `get_current_progress()`

Gets the current progress state.

**Returns**: Dictionary with:
- `percent`: Current percentage (0-100)
- `stage`: Current stage information (dict) or None
- `stage_index`: Index of current stage or -1

```python
from utils.progress_indicator import get_current_progress

progress = get_current_progress()
print(f"Current progress: {progress['percent']}%")
```

### `get_stage_names()`

Gets a list of all stage names in order.

```python
from utils.progress_indicator import get_stage_names

stages = get_stage_names()
# ['File Validation', 'Text Extraction', ...]
```

### `get_stage_info(stage_name)`

Gets detailed information about a specific stage.

```python
from utils.progress_indicator import get_stage_info

info = get_stage_info("Text Extraction")
# {'name': 'Text Extraction', 'emoji': '📄', 'start_percent': 10, ...}
```

## Usage Example

### Basic Usage

```python
import streamlit as st
from utils.progress_indicator import (
    initialize_progress,
    update_progress,
    display_progress_bar,
    complete_progress
)

# Initialize progress
initialize_progress()

# Display progress bar
progress_bar, status_text, percent_text = display_progress_bar()

# Update progress through stages
update_progress("File Validation")
# ... perform file validation ...

update_progress("Text Extraction")
# ... extract text ...

update_progress("NLP Processing", 30)
# ... process with NLP ...

# Continue through all stages...

# Mark as complete
complete_progress()
```

### Integration with Analysis Pipeline

```python
import streamlit as st
from utils.progress_indicator import initialize_progress, update_progress, display_progress_bar, complete_progress
from utils.file_parser import extract_text
from utils.text_processor import extract_sections
from utils.scorer import calculate_overall_score

def analyze_resume(file):
    """Complete resume analysis with progress tracking"""
    
    # Initialize progress
    initialize_progress()
    
    # Display progress bar
    progress_bar, status_text, percent_text = display_progress_bar()
    
    try:
        # Stage 1: File Validation
        update_progress("File Validation")
        # ... validation logic ...
        
        # Stage 2: Text Extraction
        update_progress("Text Extraction")
        text = extract_text(file)
        
        # Stage 3: NLP Processing
        update_progress("NLP Processing")
        sections = extract_sections(text)
        
        # Stage 4: Skill Validation
        update_progress("Skill Validation")
        # ... skill validation logic ...
        
        # Stage 5: Grammar Check
        update_progress("Grammar Check")
        # ... grammar check logic ...
        
        # Stage 6: Location Detection
        update_progress("Location Detection")
        # ... location detection logic ...
        
        # Stage 7: Score Calculation
        update_progress("Score Calculation")
        scores = calculate_overall_score(...)
        
        # Stage 8: Generating Results
        update_progress("Generating Results")
        # ... prepare results ...
        
        # Complete
        complete_progress()
        
        return results
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None
```

## Session State Variables

The module uses the following session state variables:

- `progress_percent` (float): Current progress percentage (0-100)
- `progress_stage` (dict): Current stage information
- `progress_stage_index` (int): Index of current stage in PROCESSING_STAGES list

## Design Principles

### Monotonicity

Progress always increases, never decreases. This ensures users see consistent forward movement through the analysis process.

### Stage-Based Progress

Progress is organized into logical stages that correspond to actual processing steps, making it clear what the system is doing at any moment.

### Visual Feedback

Each stage has an emoji and descriptive text, providing clear visual feedback about the current operation.

### Smooth Animations

Streamlit's built-in progress bar provides smooth animations as progress updates, creating a polished user experience.

## Testing

The module should be tested for:

1. **Progress Initialization** (Property 10): Progress starts at 0%
2. **Progress Monotonicity** (Property 11): Progress never decreases
3. **Progress Completion** (Property 12): Progress reaches 100% when complete
4. **Stage Identification** (Property 13): Stage name and emoji are displayed

See the test files for property-based tests that verify these behaviors.

## Error Handling

The module is designed to be robust:
- Invalid stage names are silently ignored (no update occurs)
- Progress is clamped to valid ranges (0-100%)
- Session state is safely initialized if not present

## Performance Considerations

- Session state updates are lightweight
- Progress bar updates are handled efficiently by Streamlit
- No external dependencies or heavy computations

## Future Enhancements

Potential improvements:
- Estimated time remaining calculation
- Pause/resume functionality
- Progress history tracking
- Customizable stage definitions
- Progress callbacks for external monitoring
