# Job Description Comparator Module

## Overview

The Job Description Comparator module provides functionality to compare resumes against job descriptions, calculating semantic similarity, identifying keyword matches and gaps, and analyzing skills alignment.

## Features

### 1. Semantic Similarity Calculation
- Uses Sentence-Transformers embeddings to calculate semantic similarity between resume and JD
- Returns similarity score between 0.0 and 1.0
- Handles text length limits for performance

### 2. Keyword Matching
- Identifies keywords present in both resume and job description
- Identifies critical keywords missing from resume
- Case-insensitive matching

### 3. Skills Gap Analysis
- Extracts skill-like terms from job description
- Compares against resume skills
- Identifies skills mentioned in JD but not demonstrated in resume

### 4. Match Percentage
- Combines keyword overlap (60%) and semantic similarity (40%)
- Returns overall match percentage between 0-100
- Provides quantitative measure of resume-JD alignment

## Functions

### `calculate_semantic_similarity(resume_text, jd_text, embedder)`
Calculates semantic similarity using sentence embeddings.

**Parameters:**
- `resume_text` (str): Resume text content
- `jd_text` (str): Job description text content
- `embedder` (SentenceTransformer): Loaded embedding model

**Returns:**
- `float`: Similarity score between 0.0 and 1.0

**Validates:** Requirements 10.2

### `identify_matched_keywords(resume_keywords, jd_keywords)`
Identifies keywords present in both documents.

**Parameters:**
- `resume_keywords` (List[str]): Keywords from resume
- `jd_keywords` (List[str]): Keywords from job description

**Returns:**
- `List[str]`: Keywords present in both documents

**Validates:** Requirements 10.3

### `identify_missing_keywords(resume_keywords, jd_keywords, top_n=15)`
Identifies keywords in JD but missing from resume.

**Parameters:**
- `resume_keywords` (List[str]): Keywords from resume
- `jd_keywords` (List[str]): Keywords from job description
- `top_n` (int): Maximum number of missing keywords to return

**Returns:**
- `List[str]`: Keywords missing from resume

**Validates:** Requirements 10.4

### `analyze_skills_gap(resume_skills, jd_text, nlp)`
Analyzes skills gap between resume and JD requirements.

**Parameters:**
- `resume_skills` (List[str]): Skills from resume
- `jd_text` (str): Job description text
- `nlp` (spacy.Language): Loaded spaCy model

**Returns:**
- `List[str]`: Skills mentioned in JD but not in resume

**Validates:** Requirements 10.5

### `calculate_match_percentage(resume_keywords, jd_keywords, semantic_similarity)`
Calculates overall match percentage.

**Parameters:**
- `resume_keywords` (List[str]): Keywords from resume
- `jd_keywords` (List[str]): Keywords from job description
- `semantic_similarity` (float): Semantic similarity score

**Returns:**
- `float`: Match percentage between 0 and 100

**Validates:** Requirements 10.5

### `compare_resume_with_jd(resume_text, resume_keywords, resume_skills, jd_text, jd_keywords, embedder, nlp)`
Performs comprehensive comparison between resume and job description.

**Parameters:**
- `resume_text` (str): Full resume text
- `resume_keywords` (List[str]): Keywords from resume
- `resume_skills` (List[str]): Skills from resume
- `jd_text` (str): Full job description text
- `jd_keywords` (List[str]): Keywords from job description
- `embedder` (SentenceTransformer): Loaded embedding model
- `nlp` (spacy.Language): Loaded spaCy model

**Returns:**
- `Dict`: Comparison results containing:
  - `semantic_similarity`: float (0.0-1.0)
  - `matched_keywords`: List[str]
  - `missing_keywords`: List[str]
  - `skills_gap`: List[str]
  - `match_percentage`: float (0-100)

**Validates:** Requirements 10.1, 10.2, 10.3, 10.4, 10.5

## Usage Example

```python
from utils.jd_comparator import compare_resume_with_jd
from utils.text_processor import extract_keywords, extract_jd_keywords, extract_skills
from utils.model_loader import load_sentence_transformer, load_spacy_model

# Load models
embedder = load_sentence_transformer()
nlp = load_spacy_model()

# Extract information from resume
resume_keywords = extract_keywords(resume_text, nlp)
resume_skills = extract_skills(resume_text, skills_section, nlp)

# Extract information from job description
jd_keywords = extract_jd_keywords(jd_text, nlp)

# Compare resume with job description
comparison_results = compare_resume_with_jd(
    resume_text=resume_text,
    resume_keywords=resume_keywords,
    resume_skills=resume_skills,
    jd_text=jd_text,
    jd_keywords=jd_keywords,
    embedder=embedder,
    nlp=nlp
)

# Access results
print(f"Match Percentage: {comparison_results['match_percentage']:.1f}%")
print(f"Semantic Similarity: {comparison_results['semantic_similarity']:.2f}")
print(f"Matched Keywords: {len(comparison_results['matched_keywords'])}")
print(f"Missing Keywords: {comparison_results['missing_keywords'][:5]}")
print(f"Skills Gap: {comparison_results['skills_gap'][:5]}")
```

## Algorithm Details

### Semantic Similarity
- Uses cosine similarity between sentence embeddings
- Embeddings generated using all-MiniLM-L6-v2 model
- Text limited to 5000 characters for performance
- Result clipped to [0.0, 1.0] range

### Match Percentage Formula
```
match_percentage = (keyword_overlap * 0.6 + semantic_similarity * 0.4) * 100
```
- 60% weight on keyword overlap
- 40% weight on semantic similarity
- Result bounded between 0 and 100

### Skills Gap Analysis
- Extracts entities labeled as PRODUCT, ORG, LANGUAGE from JD
- Extracts noun chunks (1-4 words) as potential skills
- Compares against resume skills using substring matching
- Returns top 20 missing skills

## Requirements Validation

This module validates the following requirements:

- **10.1**: Extract keywords from both resume and job description
- **10.2**: Calculate semantic similarity between documents
- **10.3**: Identify keywords present in both documents
- **10.4**: Identify critical keywords missing from resume
- **10.5**: Calculate match percentage and perform skills gap analysis

## Performance Considerations

- Text limited to 5000 characters for embedding generation
- Skills gap analysis limited to top 20 results
- Missing keywords limited to top 15 by default
- Uses efficient set operations for keyword matching

## Dependencies

- `numpy`: Numerical operations and similarity calculations
- `sentence-transformers`: Semantic embeddings
- `spacy`: NLP processing for skills extraction
- `typing`: Type hints
