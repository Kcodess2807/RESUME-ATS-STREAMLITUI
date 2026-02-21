# Module 04 - Document Parser Part 2 (Contact Info & NER)

**Duration**: 25 minutes  
**Type**: NLP Development

---

## 🎯 Learning Objectives
- Extract contact information using regex
- Implement Named Entity Recognition with spaCy
- Extract names, organizations, locations
- Validate extracted information

---

## 📁 Files to Modify

**Primary Files**:
- `backend/parser.py` - Add NER and contact extraction
- `backend/utils.py` - Add regex helper functions

**Config to Use**:
- `EMAIL_REGEX` from `backend/config.py`
- `PHONE_REGEX` from `backend/config.py`
- `LINKEDIN_REGEX` from `backend/config.py`
- `GITHUB_REGEX` from `backend/config.py`
- `SPACY_MODEL` from `backend/config.py`

---

## 📋 Code to Add

### 1. Update backend/utils.py

```python
# Add to backend/utils.py

import re
from typing import List, Optional

def extract_emails(text: str) -> List[str]:
    """Extract email addresses using regex"""
    from backend.config import EMAIL_REGEX
    emails = re.findall(EMAIL_REGEX, text)
    return list(set(emails))  # Remove duplicates

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers using regex"""
    from backend.config import PHONE_REGEX
    phones = re.findall(PHONE_REGEX, text)
    # Clean up phone numbers
    cleaned = []
    for phone in phones:
        # Remove extra characters
        clean = re.sub(r'[^\d+]', '', ''.join(phone) if isinstance(phone, tuple) else phone)
        if len(clean) >= 10:  # Valid phone number
            cleaned.append(clean)
    return list(set(cleaned))

def extract_linkedin_url(text: str) -> Optional[str]:
    """Extract LinkedIn URL"""
    from backend.config import LINKEDIN_REGEX
    matches = re.findall(LINKEDIN_REGEX, text, re.IGNORECASE)
    return matches[0] if matches else None

def extract_github_url(text: str) -> Optional[str]:
    """Extract GitHub URL"""
    from backend.config import GITHUB_REGEX
    matches = re.findall(GITHUB_REGEX, text, re.IGNORECASE)
    return matches[0] if matches else None
```

### 2. Update backend/parser.py (Add NER Functions)

```python
# Add to backend/parser.py

import spacy
from typing import Dict, List, Optional
from backend.config import SPACY_MODEL
from backend.utils import (
    extract_emails,
    extract_phone_numbers,
    extract_linkedin_url,
    extract_github_url
)

# Load spaCy model (global, load once)
try:
    nlp = spacy.load(SPACY_MODEL)
    logger.info(f"✅ Loaded spaCy model: {SPACY_MODEL}")
except:
    nlp = None
    logger.warning(f"⚠️  spaCy model not found: {SPACY_MODEL}")


def extract_contact_info(text: str) -> Dict:
    """
    Extract contact information from resume text
    
    Args:
        text: Resume text
        
    Returns:
        Dict with contact information
    """
    contact_info = {
        'emails': [],
        'phones': [],
        'linkedin': None,
        'github': None
    }
    
    # Extract emails
    contact_info['emails'] = extract_emails(text)
    
    # Extract phone numbers
    contact_info['phones'] = extract_phone_numbers(text)
    
    # Extract LinkedIn
    contact_info['linkedin'] = extract_linkedin_url(text)
    
    # Extract GitHub
    contact_info['github'] = extract_github_url(text)
    
    logger.info(f"Extracted contact info: {len(contact_info['emails'])} emails, "
               f"{len(contact_info['phones'])} phones")
    
    return contact_info


def extract_entities_with_spacy(text: str) -> Dict:
    """
    Extract named entities using spaCy NER
    
    Args:
        text: Resume text
        
    Returns:
        Dict with extracted entities
    """
    if nlp is None:
        logger.warning("spaCy model not loaded, skipping NER")
        return {
            'names': [],
            'organizations': [],
            'locations': [],
            'dates': []
        }
    
    # Process text with spaCy
    doc = nlp(text)
    
    entities = {
        'names': [],
        'organizations': [],
        'locations': [],
        'dates': []
    }
    
    # Extract entities by type
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            entities['names'].append(ent.text)
        elif ent.label_ == 'ORG':
            entities['organizations'].append(ent.text)
        elif ent.label_ in ['GPE', 'LOC']:  # Geo-political entity, Location
            entities['locations'].append(ent.text)
        elif ent.label_ == 'DATE':
            entities['dates'].append(ent.text)
    
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    logger.info(f"Extracted entities: {len(entities['names'])} names, "
               f"{len(entities['organizations'])} orgs, "
               f"{len(entities['locations'])} locations")
    
    return entities


def extract_name_from_entities(entities: Dict, text: str) -> Optional[str]:
    """
    Extract candidate name from entities
    Usually the first PERSON entity in the document
    
    Args:
        entities: Dict from extract_entities_with_spacy
        text: Original text
        
    Returns:
        Candidate name or None
    """
    if entities['names']:
        # Return first name (usually at top of resume)
        return entities['names'][0]
    
    # Fallback: try to find name in first few lines
    lines = text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        # Simple heuristic: short line with capital letters
        if len(line) < 50 and len(line.split()) <= 4:
            if any(word[0].isupper() for word in line.split() if word):
                return line
    
    return None


# Update parse_resume function to include contact info and NER
def parse_resume(file_path: str) -> Dict:
    """
    Main parser function - now includes contact info and NER
    
    Args:
        file_path: Path to resume file
        
    Returns:
        Dict with parsed data including contact info and entities
    """
    # ... (previous code for file parsing)
    
    # Get basic parsed data
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        raw_text = parse_pdf(file_path)
    elif ext == '.docx':
        raw_text = parse_docx(file_path)
    elif ext == '.txt':
        raw_text = parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    cleaned_text = clean_text(raw_text)
    
    # NEW: Extract contact information
    contact_info = extract_contact_info(cleaned_text)
    
    # NEW: Extract entities with spaCy
    entities = extract_entities_with_spacy(cleaned_text)
    
    # NEW: Extract candidate name
    candidate_name = extract_name_from_entities(entities, cleaned_text)
    
    # Return enhanced structured data
    return {
        'raw_text': raw_text,
        'cleaned_text': cleaned_text,
        'file_path': file_path,
        'file_type': ext,
        'text_length': len(cleaned_text),
        
        # NEW fields
        'contact_info': contact_info,
        'entities': entities,
        'name': candidate_name,
    }
```

---

## 🎬 Video Walkthrough

### Part 1: Explain NER and Contact Extraction (5 min)
- What is Named Entity Recognition?
- Why use regex for contact info?
- Why use spaCy for names/orgs/locations?
- Show examples of entities

### Part 2: Build Contact Extraction (7 min)
- Add regex functions to utils.py
- Extract emails
- Extract phone numbers
- Extract LinkedIn/GitHub URLs
- Test with sample text

### Part 3: Implement spaCy NER (8 min)
- Load spaCy model
- Process text with NER
- Extract PERSON, ORG, GPE, DATE entities
- Remove duplicates
- Test with sample resume

### Part 4: Extract Candidate Name (3 min)
- Use first PERSON entity
- Fallback heuristics
- Validate extraction

### Part 5: Update Main Parser (2 min)
- Integrate contact extraction
- Integrate NER
- Return enhanced data structure
- Test complete parser

---

## 🧪 Testing

### Test Contact Extraction:
```python
# Test in Python REPL
from backend.utils import extract_emails, extract_phone_numbers

text = """
John Doe
Email: john.doe@email.com
Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johndoe
"""

print("Emails:", extract_emails(text))
print("Phones:", extract_phone_numbers(text))
```

### Test spaCy NER:
```python
from backend.parser import extract_entities_with_spacy

text = """
John Doe worked at Google in California from 2020 to 2023.
He then joined Microsoft in Seattle.
"""

entities = extract_entities_with_spacy(text)
print("Names:", entities['names'])
print("Organizations:", entities['organizations'])
print("Locations:", entities['locations'])
```

### Test Complete Parser:
```bash
python test_parser.py uploads/sample_resume.pdf
```

Expected output should now include:
- Contact info (emails, phones, LinkedIn, GitHub)
- Entities (names, organizations, locations, dates)
- Candidate name

---

## 🎤 Key Talking Points

**Why Regex for Contact Info?**:
- Structured patterns (email format, phone format)
- Fast and reliable
- No ML needed for structured data

**Why spaCy for NER?**:
- Unstructured data (names, companies)
- Pre-trained on millions of documents
- Understands context
- Production-ready

**Entity Types**:
- PERSON: Names of people
- ORG: Companies, organizations
- GPE: Countries, cities, states
- LOC: Non-GPE locations
- DATE: Dates and date ranges

**Common Issues**:
- spaCy might miss some names
- Phone regex might catch non-phone numbers
- Need validation and cleaning

---

## ✅ Module Completion Checklist

Students should have:
- [ ] Contact extraction functions in utils.py
- [ ] spaCy NER integration in parser.py
- [ ] Name extraction logic
- [ ] Updated parse_resume() function
- [ ] Successfully tested with sample resumes
- [ ] Understanding of NER concepts

---

## 🔗 Next Module

**Module 05**: Document Parser Part 3 (Sections & Skills)
- Section detection (Education, Experience, Skills)
- Skills extraction from database
- Experience parsing with dates
- Education parsing
- Complete resume structure
