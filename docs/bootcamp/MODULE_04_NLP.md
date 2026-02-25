# Module 04: NLP & NER (25 min)

## Objective
Use spaCy to extract structured information from resume text: sections, entities, keywords.

## Files to Create
- `app/core/processor.py`
- `data/skills_database.json`
- `data/action_verbs.json`

## Script

### Part 1: Why NLP Matters (3 min)

"We have raw text from the parser. Now we need to understand it.

**The Challenge:**
```
'Developed Python applications using Django and React...'
```

We need to extract:
- Skills: Python, Django, React
- Action verb: Developed
- Context: applications

**spaCy gives us:**
- Tokenization: Break into words
- POS Tagging: Identify verbs, nouns
- NER: Find entities (organizations, dates)
- Dependency parsing: Understand relationships

This is the foundation for everything else."

### Part 2: Loading spaCy Model (5 min)

**Create app/core/processor.py:**

```python
"""
NLP Processor Module
Uses spaCy for text analysis and information extraction
"""

import spacy
from typing import Dict, List, Set
import re
from functools import lru_cache

# Load model once and cache it
@lru_cache(maxsize=1)
def load_spacy_model():
    """
    Load spaCy model with caching
    
    Why @lru_cache?
    - Model loading is expensive (~2 seconds)
    - We only need one instance
    - Cache persists across function calls
    - Huge performance improvement
    """
    try:
        # Try to load medium model (better accuracy)
        nlp = spacy.load("en_core_web_md")
    except OSError:
        # Fallback to small model
        print("Loading en_core_web_sm (fallback)")
        nlp = spacy.load("en_core_web_sm")
    
    return nlp


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Why clean?
    - Remove extra whitespace
    - Normalize line breaks
    - Remove special characters that confuse NLP
    """
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\-\(\)]', '', text)
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n')
    
    return text.strip()
```

**Explain:**
"The `@lru_cache` decorator is crucial:
- First call: Loads model (slow)
- Subsequent calls: Returns cached model (instant)
- Saves 2 seconds per analysis!

Text cleaning:
- `\s+` matches multiple whitespace → single space
- Keeps punctuation (helps with sentence detection)
- Removes weird characters from PDFs"

### Part 3: Section Detection (8 min)

```python
# Section headers we look for
SECTION_PATTERNS = {
    'experience': [
        r'work\s+experience',
        r'professional\s+experience',
        r'employment\s+history',
        r'work\s+history',
        r'experience'
    ],
    'education': [
        r'education',
        r'academic\s+background',
        r'qualifications'
    ],
    'skills': [
        r'skills',
        r'technical\s+skills',
        r'core\s+competencies',
        r'expertise'
    ],
    'projects': [
        r'projects',
        r'personal\s+projects',
        r'key\s+projects'
    ],
    'summary': [
        r'summary',
        r'profile',
        r'objective',
        r'about\s+me'
    ]
}


def detect_sections(text: str) -> Dict[str, str]:
    """
    Split resume into sections
    
    How it works:
    1. Find section headers using regex
    2. Extract text between headers
    3. Return dictionary of sections
    
    Why this matters:
    - Different sections have different importance
    - Skills section = high weight
    - Summary = lower weight
    """
    sections = {}
    lines = text.split('\n')
    
    current_section = 'other'
    section_content = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if this line is a section header
        found_section = None
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, line_lower):
                    found_section = section_name
                    break
            if found_section:
                break
        
        if found_section:
            # Save previous section
            if section_content:
                sections[current_section] = '\n'.join(section_content)
            
            # Start new section
            current_section = found_section
            section_content = []
        else:
            # Add to current section
            if line.strip():
                section_content.append(line)
    
    # Save last section
    if section_content:
        sections[current_section] = '\n'.join(section_content)
    
    return sections
```

**Explain:**
"Section detection is pattern matching:
- We define regex patterns for each section
- Scan line by line
- When we find a header, start new section
- Everything until next header goes in that section

Why regex patterns?
- 'Experience' vs 'Work Experience' vs 'Professional Experience'
- All mean the same thing
- Patterns catch variations

The `\s+` in regex:
- Matches one or more spaces
- 'work experience' or 'work    experience' both match"

### Part 4: Keyword Extraction (6 min)

```python
def extract_keywords(text: str, nlp) -> List[str]:
    """
    Extract important keywords using spaCy
    
    What we extract:
    - Nouns (technologies, tools)
    - Proper nouns (company names, products)
    - Adjectives (senior, experienced)
    
    Why these?
    - ATS systems look for nouns (skills, tools)
    - Proper nouns show experience with specific tech
    - Adjectives show seniority level
    """
    doc = nlp(text)
    
    keywords = set()
    
    for token in doc:
        # Skip short words and stop words
        if len(token.text) < 3 or token.is_stop:
            continue
        
        # Extract based on POS tag
        if token.pos_ in ['NOUN', 'PROPN', 'ADJ']:
            # Lemmatize (convert to base form)
            # 'developed' -> 'develop'
            # 'applications' -> 'application'
            keywords.add(token.lemma_.lower())
    
    return list(keywords)


def extract_skills(text: str, skills_database: Set[str]) -> List[str]:
    """
    Extract skills by matching against known skills
    
    Why a database?
    - 'Python' is a skill
    - 'python' (the snake) is not
    - Context matters
    - Database has verified skills
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in skills_database:
        # Use word boundaries to avoid partial matches
        # 'Java' should match, but not in 'JavaScript'
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return found_skills
```

**Explain:**
"POS tagging (Part-of-Speech):
- NOUN: 'Python', 'experience', 'application'
- PROPN: 'Google', 'AWS', 'Django'
- ADJ: 'senior', 'experienced', 'proficient'

Lemmatization:
- 'developed' → 'develop'
- 'applications' → 'application'
- Helps match variations

Word boundaries (`\b`):
- 'Java' matches in 'I know Java'
- 'Java' doesn't match in 'JavaScript'
- Prevents false positives"

### Part 5: Main Processing Function (3 min)

```python
def process_resume_text(text: str, nlp) -> Dict:
    """
    Main processing pipeline
    
    Returns complete structured data
    """
    # Clean text
    cleaned_text = clean_text(text)
    
    # Detect sections
    sections = detect_sections(cleaned_text)
    
    # Extract keywords from full text
    keywords = extract_keywords(cleaned_text, nlp)
    
    # Load skills database
    with open('data/skills_database.json', 'r') as f:
        skills_db = set(json.load(f))
    
    # Extract skills
    skills = extract_skills(cleaned_text, skills_db)
    
    # Extract from specific sections
    experience_text = sections.get('experience', '')
    education_text = sections.get('education', '')
    
    # Process with spaCy for entities
    doc = nlp(cleaned_text)
    
    # Extract entities
    entities = {
        'organizations': [],
        'dates': [],
        'locations': []
    }
    
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            entities['organizations'].append(ent.text)
        elif ent.label_ == 'DATE':
            entities['dates'].append(ent.text)
        elif ent.label_ in ['GPE', 'LOC']:
            entities['locations'].append(ent.text)
    
    return {
        'sections': sections,
        'keywords': keywords,
        'skills': skills,
        'entities': entities,
        'experience': experience_text,
        'education': education_text,
        'full_text': cleaned_text
    }
```

**Explain:**
"This is our pipeline:
1. Clean text
2. Detect sections
3. Extract keywords
4. Match skills
5. Find entities (companies, dates, locations)
6. Return structured data

Named Entity Recognition (NER):
- ORG: Organizations (Google, Microsoft)
- DATE: Dates (2020-2023, Jan 2022)
- GPE/LOC: Locations (San Francisco, USA)

This structured data feeds into scoring."

## Create Supporting Data Files

**Create data/skills_database.json:**

```json
[
  "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
  "React", "Angular", "Vue", "Django", "Flask", "FastAPI", "Spring Boot",
  "Node.js", "Express", "Next.js", "Svelte",
  "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
  "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
  "Git", "CI/CD", "Jenkins", "GitHub Actions",
  "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
  "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
  "REST API", "GraphQL", "Microservices", "Agile", "Scrum"
]
```

**Create data/action_verbs.json:**

```json
[
  "achieved", "accomplished", "administered", "analyzed", "architected",
  "built", "collaborated", "created", "delivered", "designed",
  "developed", "engineered", "enhanced", "established", "executed",
  "implemented", "improved", "increased", "initiated", "launched",
  "led", "managed", "optimized", "organized", "performed",
  "planned", "produced", "reduced", "resolved", "streamlined"
]
```

## Testing the Processor

**Create test script:**

```python
# test_processor.py
from app.core.processor import load_spacy_model, process_resume_text

# Sample resume text
sample_text = """
EXPERIENCE
Senior Python Developer at Google
- Developed microservices using Django and PostgreSQL
- Led team of 5 engineers
- Reduced latency by 40%

SKILLS
Python, Django, PostgreSQL, AWS, Docker
"""

nlp = load_spacy_model()
result = process_resume_text(sample_text, nlp)

print("Sections found:", list(result['sections'].keys()))
print("Skills extracted:", result['skills'])
print("Keywords:", result['keywords'][:10])
print("Organizations:", result['entities']['organizations'])
```

## Key Concepts to Emphasize

1. **Caching** - Load expensive resources once
2. **POS Tagging** - Understanding word types
3. **NER** - Finding entities automatically
4. **Pattern Matching** - Flexible section detection
5. **Lemmatization** - Normalizing word forms

## Common Issues

**Issue**: "Model not found"
**Solution**: `python -m spacy download en_core_web_md`

**Issue**: "Section not detected"
**Solution**: Add more patterns to SECTION_PATTERNS

**Issue**: "Too many false positive skills"
**Solution**: Use word boundaries in regex

## Checkpoint

Students should have:
- [ ] spaCy model loaded
- [ ] Text cleaning working
- [ ] Section detection working
- [ ] Keyword extraction working
- [ ] Skills matching working
- [ ] Test script running

## Transition to Module 05

"Great! We can now extract structured data. Next, we'll analyze the quality of that data: Are action verbs used? Are achievements quantified? Is experience described well?"
