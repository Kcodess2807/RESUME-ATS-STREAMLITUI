# Text Processor Module

## Overview

The `text_processor.py` module handles NLP processing of resume text using spaCy. It extracts structured information including sections, contact details, skills, projects, keywords, and action verbs.

## Features

### Section Extraction
Identifies and extracts standard resume sections:
- Professional Summary
- Work Experience
- Education
- Skills
- Projects

### Contact Information Extraction
Extracts contact details using regex patterns:
- Email addresses
- Phone numbers
- LinkedIn profiles
- GitHub profiles
- Portfolio URLs

### Skills Extraction
Identifies technical and soft skills from:
- Dedicated skills section
- Named entities (PRODUCT, ORG, LANGUAGE)
- Technical keywords throughout the resume

### Project Extraction
Parses project descriptions including:
- Project titles
- Descriptions
- Technologies used

### Keyword Extraction
Extracts important terms using:
- Named Entity Recognition (NER)
- Noun chunk analysis
- Frequency analysis
- Returns top N keywords

### Action Verb Detection
Identifies action verbs at the start of bullet points to assess resume quality.

## Usage

```python
from utils.text_processor import process_resume_text, load_spacy_model

# Load spaCy model (cached)
nlp = load_spacy_model()

# Process resume text
resume_text = "..."  # Your resume text
result = process_resume_text(resume_text, nlp)

# Access extracted information
sections = result['sections']
contact_info = result['contact_info']
skills = result['skills']
projects = result['projects']
keywords = result['keywords']
action_verbs = result['action_verbs']
```

## Requirements Validated

- **5.1**: Extract summary section
- **5.2**: Extract experience section
- **5.3**: Extract education section
- **5.4**: Extract skills section with categorization
- **5.5**: Extract projects section with parsing
- **5.6**: Extract contact information (email, phone, LinkedIn, GitHub, portfolio)
- **14.1**: Load spaCy model from local storage
- **14.4**: Cache models in memory using @st.cache_resource
- **16.1**: Model caching for performance

## Dependencies

- spacy (en_core_web_md or en_core_web_sm)
- streamlit (for caching)
- re (standard library)
- collections (standard library)

## Performance

- Uses @st.cache_resource for model caching
- Limits text processing to first 10k characters for performance
- Efficient regex patterns for contact info extraction
- Optimized section detection with pattern matching
