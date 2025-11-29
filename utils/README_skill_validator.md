# Skill Validator Module

## Overview

The Skill Validator module validates that claimed skills in a resume are actually demonstrated in the candidate's projects and experience. It uses both exact text matching and semantic similarity analysis with embeddings to determine if skills are backed by evidence.

## Features

- **Exact Skill Matching**: Case-insensitive text matching to find skills in project descriptions
- **Semantic Similarity**: Uses Sentence-Transformers embeddings to find semantically similar content
- **Validation Threshold**: Configurable threshold (default 0.6) for semantic similarity
- **Skill-Project Mapping**: Generates complete mapping of which projects demonstrate each skill
- **Validation Scoring**: Calculates score based on percentage of validated skills (0-15 points)
- **Feedback Generation**: Provides user-friendly feedback messages

## Requirements Validated

- **6.1**: Exact skill matching in project descriptions
- **6.2**: Semantic similarity calculation using embeddings
- **6.3**: Validation threshold logic (0.6 threshold)
- **6.4**: Unmatched skill detection
- **6.5**: Skill-project mapping generation
- **6.6**: Validation score calculation: (validated / total) × 15
- **14.2**: Load Sentence-Transformers model from local storage
- **14.4**: Cache models in memory using @st.cache_resource

## Functions

### `load_embedder(model_name: str = "all-MiniLM-L6-v2")`

Loads and caches the Sentence-Transformers model for generating embeddings.

**Parameters:**
- `model_name`: Name of the Sentence-Transformers model (default: "all-MiniLM-L6-v2")

**Returns:**
- Loaded SentenceTransformer object

**Caching:**
- Uses `@st.cache_resource` to cache the model in memory

### `exact_skill_match(skill: str, text: str) -> bool`

Checks if a skill appears exactly in the text (case-insensitive).

**Parameters:**
- `skill`: Skill text to search for
- `text`: Text to search in

**Returns:**
- `True` if skill appears in text, `False` otherwise

**Example:**
```python
exact_skill_match("Python", "I used Python for this project")  # True
exact_skill_match("Python", "I used Java for this project")    # False
```

### `calculate_semantic_similarity(skill: str, text: str, embedder: SentenceTransformer) -> float`

Calculates cosine similarity between skill and text embeddings.

**Parameters:**
- `skill`: Skill text to validate
- `text`: Project or experience text to check against
- `embedder`: Loaded SentenceTransformer model

**Returns:**
- Similarity score between 0.0 and 1.0

**Example:**
```python
embedder = load_embedder()
similarity = calculate_semantic_similarity("Python", "Built with Python", embedder)
# Returns: ~0.95 (high similarity)
```

### `validate_skill_against_projects(skill, projects, experience, embedder, threshold=0.6)`

Validates a single skill against projects and experience.

**Parameters:**
- `skill`: Skill to validate
- `projects`: List of project dictionaries with 'title', 'description', 'technologies'
- `experience`: Experience section text
- `embedder`: Loaded SentenceTransformer model
- `threshold`: Similarity threshold for validation (default 0.6)

**Returns:**
- Tuple of `(is_validated, matching_projects, max_similarity)`

### `validate_skills_with_projects(skills, projects, experience, embedder=None, threshold=0.6)`

Main validation function that validates all skills against projects and experience.

**Parameters:**
- `skills`: List of skills to validate
- `projects`: List of project dictionaries
- `experience`: Experience section text
- `embedder`: Optional pre-loaded SentenceTransformer model (will load if not provided)
- `threshold`: Similarity threshold for validation (default 0.6)

**Returns:**
Dictionary with validation results:
```python
{
    "validated_skills": [
        {"skill": "Python", "projects": ["ML Pipeline"], "similarity": 0.95}
    ],
    "unvalidated_skills": ["Cooking"],
    "validation_percentage": 0.75,  # 75%
    "skill_project_mapping": {
        "Python": ["ML Pipeline", "Experience Section"],
        "Cooking": []
    },
    "validation_score": 11.25  # (0.75 * 15)
}
```

**Example:**
```python
from utils.skill_validator import validate_skills_with_projects

skills = ['Python', 'Machine Learning', 'Docker']
projects = [
    {
        'title': 'ML Pipeline',
        'description': 'Built a machine learning pipeline using Python',
        'technologies': ['Python', 'scikit-learn']
    }
]
experience = 'Worked on Docker containerization projects'

result = validate_skills_with_projects(skills, projects, experience)
print(f"Validation score: {result['validation_score']:.2f}/15.00")
```

### `generate_validation_feedback(validation_results: Dict) -> List[str]`

Generates user-friendly feedback messages for validated/unvalidated skills.

**Parameters:**
- `validation_results`: Results from `validate_skills_with_projects`

**Returns:**
- List of feedback messages

**Example Output:**
```
✅ Excellent! 100% of your skills are validated by your projects and experience.

✅ Validated Skills (3):
  • Python - demonstrated in 2 projects
  • Machine Learning - demonstrated in ML Pipeline
  • Docker - demonstrated in Container Deployment
```

### `calculate_skill_validation_score(validation_results: Dict) -> float`

Calculates the skill validation component score.

**Parameters:**
- `validation_results`: Results from `validate_skills_with_projects`

**Returns:**
- Score between 0.0 and 15.0

## Usage Example

```python
import streamlit as st
from utils.skill_validator import validate_skills_with_projects, generate_validation_feedback
from utils.text_processor import process_resume_text, load_spacy_model

# Load models
nlp = load_spacy_model()

# Process resume
resume_text = "..."  # Your resume text
processed = process_resume_text(resume_text, nlp)

# Validate skills
validation_results = validate_skills_with_projects(
    skills=processed['skills'],
    projects=processed['projects'],
    experience=processed['sections']['experience']
)

# Display results
st.write(f"Validation Score: {validation_results['validation_score']:.2f}/15.00")

# Show feedback
feedback = generate_validation_feedback(validation_results)
for message in feedback:
    st.write(message)
```

## Validation Logic

1. **Exact Matching**: First checks if skill text appears exactly in project descriptions (case-insensitive)
2. **Semantic Similarity**: If no exact match, calculates semantic similarity using embeddings
3. **Threshold Check**: Skill is validated if similarity >= 0.6
4. **Experience Check**: Also checks the experience section for skill validation
5. **Scoring**: Final score = (validated_skills / total_skills) × 15

## Performance Considerations

- **Model Caching**: The Sentence-Transformers model is cached using `@st.cache_resource` to avoid reloading
- **Embedding Calculation**: Embeddings are calculated on-demand for each validation
- **Text Limits**: Project descriptions are limited to 1000 characters for performance

## Error Handling

- Returns 0.0 similarity for empty inputs
- Handles model loading failures with clear error messages
- Continues validation even if individual similarity calculations fail
- Provides warnings for calculation errors without stopping the process

## Testing

The module includes comprehensive validation:
- Exact matching with various cases
- Semantic similarity calculations
- Empty input handling
- Score calculation accuracy
- Feedback generation

Run tests with:
```bash
pytest tests/test_skill_validator_unit.py
pytest tests/test_skill_validator_properties.py
```

## Dependencies

- `streamlit`: For caching and UI integration
- `sentence-transformers`: For semantic similarity embeddings
- `numpy`: For cosine similarity calculations

## Model Information

**Default Model**: `all-MiniLM-L6-v2`
- Size: ~80MB
- Speed: Fast inference
- Quality: Good for semantic similarity tasks
- Embedding dimension: 384

## Future Enhancements

- Support for skill synonyms (e.g., "JS" → "JavaScript")
- Industry-specific skill databases
- Skill level detection (beginner, intermediate, expert)
- Multi-language skill validation
