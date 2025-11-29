# Grammar Checker Module

## Overview

The Grammar Checker module provides comprehensive grammar and spelling checking functionality for resume text using LanguageTool. It categorizes errors by severity, filters out technical term false positives, and calculates penalties according to the scoring formula.

## Key Features

- **Comprehensive Error Detection**: Detects spelling, grammar, punctuation, and style issues
- **Error Categorization**: Classifies errors as critical, moderate, or minor
- **Technical Terms Whitelist**: Filters out false positives for common technical terms
- **Penalty Calculation**: Applies scoring penalties based on error severity (max 20 points)
- **Context Extraction**: Provides context around errors for easy identification
- **Correction Suggestions**: Offers suggestions for fixing detected errors

## Functions

### `load_grammar_checker(language: str = "en-US") -> LanguageTool`

Loads and caches LanguageTool for grammar checking using Streamlit's `@st.cache_resource`.

**Parameters:**
- `language`: Language code for grammar checking (default: "en-US")

**Returns:**
- Loaded LanguageTool object

**Raises:**
- `Exception`: If LanguageTool fails to load

### `check_grammar_and_spelling(text: str, language_tool: LanguageTool = None) -> Dict`

Performs comprehensive grammar and spelling check on text.

**Parameters:**
- `text`: Text to check
- `language_tool`: Optional pre-loaded LanguageTool instance

**Returns:**
Dictionary containing:
- `total_errors`: Total number of errors
- `critical_errors`: List of critical error details
- `moderate_errors`: List of moderate error details
- `minor_errors`: List of minor error details
- `grammar_score`: Score after applying penalties (0-100)
- `penalty_applied`: Total penalty points (0-20)
- `error_free_percentage`: Percentage of text without errors

**Example:**
```python
from utils.grammar_checker import check_grammar_and_spelling, load_grammar_checker

# Load grammar checker
grammar_tool = load_grammar_checker()

# Check text
text = "This is a sample resume text with some erors."
results = check_grammar_and_spelling(text, grammar_tool)

print(f"Total errors: {results['total_errors']}")
print(f"Penalty: {results['penalty_applied']} points")
```

### `categorize_error(error: Match) -> str`

Categorizes a grammar error as critical, moderate, or minor.

**Error Categories:**

**Critical Errors** (5 points each):
- Spelling mistakes in common words
- Subject-verb agreement errors
- Wrong verb tense
- Incorrect word usage (e.g., their/there/they're)

**Moderate Errors** (2 points each):
- Punctuation issues
- Capitalization errors
- Missing or wrong articles
- Redundant phrases

**Minor Errors** (0.5 points each):
- Style suggestions
- Whitespace issues
- Formatting suggestions

**Parameters:**
- `error`: LanguageTool Match object

**Returns:**
- Category string: "critical", "moderate", or "minor"

### `calculate_grammar_penalty(errors: Dict) -> float`

Calculates score penalty based on error counts.

**Formula:**
```
penalty = (critical_count × 5) + (moderate_count × 2) + (minor_count × 0.5)
Maximum penalty: 20 points
```

**Parameters:**
- `errors`: Dictionary with 'critical_errors', 'moderate_errors', 'minor_errors' lists

**Returns:**
- Penalty value (0-20)

### `filter_technical_term_errors(errors: List[Match], text: str) -> List[Match]`

Filters out errors related to technical terms in the whitelist.

**Parameters:**
- `errors`: List of LanguageTool Match objects
- `text`: Original text being checked

**Returns:**
- Filtered list of errors

### `generate_grammar_feedback(grammar_results: Dict) -> List[str]`

Generates user-friendly feedback messages based on grammar check results.

**Parameters:**
- `grammar_results`: Results from `check_grammar_and_spelling()`

**Returns:**
- List of feedback messages

**Example:**
```python
feedback = generate_grammar_feedback(results)
for message in feedback:
    print(message)
```

### `get_top_errors(grammar_results: Dict, max_errors: int = 5) -> List[Dict]`

Gets the most important errors to display to the user, prioritized by severity.

**Parameters:**
- `grammar_results`: Results from `check_grammar_and_spelling()`
- `max_errors`: Maximum number of errors to return

**Returns:**
- List of error details, prioritized by severity (critical → moderate → minor)

## Technical Terms Whitelist

The module includes a comprehensive whitelist of technical terms to avoid false positives:

- **Programming Languages**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, etc.
- **Frameworks**: React, Angular, Vue, Django, Flask, Spring, TensorFlow, etc.
- **Databases**: MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch, etc.
- **Cloud & DevOps**: AWS, Azure, GCP, Kubernetes, Docker, Jenkins, etc.
- **Tools**: Git, JIRA, Postman, Swagger, GraphQL, etc.
- **Methodologies**: Agile, Scrum, DevOps, CI/CD, Microservices, etc.

## Error Detail Structure

Each error in the results contains:

```python
{
    'message': 'Error description',
    'context': '...text around the error...',
    'suggestions': ['suggestion1', 'suggestion2', 'suggestion3'],
    'rule_id': 'RULE_ID',
    'offset': 123,  # Character position in text
    'error_length': 5,  # Length of error
    'error_text': 'eror',  # The actual error text
    'severity': 'critical'  # Added by get_top_errors()
}
```

## Usage Example

```python
import streamlit as st
from utils.grammar_checker import (
    load_grammar_checker,
    check_grammar_and_spelling,
    generate_grammar_feedback,
    get_top_errors
)

# Load grammar checker (cached)
grammar_tool = load_grammar_checker()

# Check resume text
resume_text = """
This is a sample resume with some erors.
I have experience in Python, React, and AWS.
I worked on varios projects involving machine learning.
"""

results = check_grammar_and_spelling(resume_text, grammar_tool)

# Display results
st.write(f"Total Errors: {results['total_errors']}")
st.write(f"Grammar Score: {results['grammar_score']}/100")
st.write(f"Penalty Applied: {results['penalty_applied']} points")

# Show feedback
feedback = generate_grammar_feedback(results)
for message in feedback:
    st.info(message)

# Show top errors
top_errors = get_top_errors(results, max_errors=5)
for error in top_errors:
    st.error(f"**{error['severity'].upper()}**: {error['message']}")
    st.write(f"Context: {error['context']}")
    if error['suggestions']:
        st.write(f"Suggestions: {', '.join(error['suggestions'])}")
```

## Requirements Validation

This module validates the following requirements:

- **7.1**: Detects all spelling errors using LanguageTool
- **7.2**: Detects all grammar mistakes using LanguageTool
- **7.3**: Detects punctuation errors and tense inconsistencies
- **7.4**: Categorizes each error as critical, moderate, or minor
- **7.5**: Provides correction suggestions for each error
- **7.6**: Calculates penalties: 5×critical + 2×moderate + 0.5×minor (max 20)
- **14.3**: Initializes LanguageTool locally
- **14.4**: Caches LanguageTool using @st.cache_resource

## Performance Considerations

- **Caching**: LanguageTool is cached using `@st.cache_resource` to avoid reloading
- **Filtering**: Technical terms are filtered to reduce false positives
- **Context Extraction**: Limited to 50 characters before/after error for performance
- **Suggestion Limit**: Only top 3 suggestions per error are returned

## Error Handling

The module handles errors gracefully:
- If LanguageTool fails to load, an error is displayed with troubleshooting steps
- If text is empty, returns zero errors
- If technical terms trigger false positives, they are filtered out
- Penalty is always capped at 20 points maximum
