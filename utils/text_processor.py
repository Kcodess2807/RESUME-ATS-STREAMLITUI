"""
Text Processor Module for ATS Resume Scorer

This module handles NLP processing of resume text including section extraction,
contact information extraction, skills extraction, project extraction, keyword
extraction, and action verb detection.
"""

import re
import streamlit as st
import spacy
from typing import Dict, List, Optional, Tuple
from collections import Counter
import string


@st.cache_resource
def load_spacy_model(model_name: str = "en_core_web_md"):
    """
    Load and cache spaCy language model.
    
    Args:
        model_name: Name of the spaCy model to load
        
    Returns:
        Loaded spaCy Language object
        
    Validates:
        - Requirements 14.1: Load spaCy model from local storage
        - Requirements 14.4: Cache models in memory
    """
    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError:
        # Try smaller model as fallback
        try:
            nlp = spacy.load("en_core_web_sm")
            st.warning(f"Could not load {model_name}, using en_core_web_sm instead")
            return nlp
        except OSError:
            st.error(
                f"spaCy model not found. Please run: python -m spacy download {model_name}"
            )
            raise


# Section headers patterns for resume parsing
SECTION_PATTERNS = {
    'summary': [
        r'\b(professional\s+summary|summary|profile|objective|career\s+objective)\b',
    ],
    'experience': [
        r'\b(work\s+experience|professional\s+experience|experience|employment\s+history|work\s+history)\b',
    ],
    'education': [
        r'\b(education|academic\s+background|qualifications)\b',
    ],
    'skills': [
        r'\b(skills|technical\s+skills|core\s+competencies|competencies|expertise)\b',
    ],
    'projects': [
        r'\b(projects|personal\s+projects|key\s+projects|portfolio)\b',
    ]
}

# Contact information patterns
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
LINKEDIN_PATTERN = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
GITHUB_PATTERN = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
PORTFOLIO_PATTERN = r'(?:https?://)?(?:www\.)?[\w-]+\.(?:com|net|org|io|dev|me)(?:/[\w-]*)?'

# Common action verbs for resume analysis
ACTION_VERBS = {
    'achieved', 'adapted', 'administered', 'analyzed', 'architected', 'automated',
    'built', 'collaborated', 'completed', 'conducted', 'configured', 'created',
    'delivered', 'demonstrated', 'designed', 'developed', 'directed', 'drove',
    'enhanced', 'established', 'executed', 'expanded', 'facilitated', 'generated',
    'implemented', 'improved', 'increased', 'initiated', 'integrated', 'launched',
    'led', 'maintained', 'managed', 'migrated', 'optimized', 'orchestrated',
    'organized', 'performed', 'planned', 'produced', 'programmed', 'reduced',
    'refactored', 'resolved', 'restructured', 'scaled', 'spearheaded', 'streamlined',
    'strengthened', 'supervised', 'supported', 'transformed', 'upgraded'
}

# Common technical skills for categorization
TECHNICAL_SKILLS_KEYWORDS = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
    'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'express',
    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
    'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'devops'
}


def extract_sections(text: str, nlp: spacy.Language) -> Dict[str, str]:
    """
    Identifies and extracts resume sections using pattern matching.
    
    Args:
        text: Resume text content
        nlp: Loaded spaCy Language model
        
    Returns:
        Dictionary mapping section names to their content
        Example: {"summary": "...", "experience": "...", "education": "...", 
                  "skills": "...", "projects": "..."}
                  
    Validates:
        - Requirements 5.1: Extract summary section
        - Requirements 5.2: Extract experience section
        - Requirements 5.3: Extract education section
        - Requirements 5.4: Extract skills section
        - Requirements 5.5: Extract projects section
    """
    sections = {
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'projects': ''
    }
    
    # Split text into lines for processing
    lines = text.split('\n')
    current_section = None
    section_content = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Skip empty lines at the start
        if not line_stripped:
            if current_section and section_content:
                section_content.append(line)
            continue
        
        # Check if this line is a section header
        section_found = False
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                # Check if line matches pattern and is likely a header (short, uppercase, etc.)
                if re.search(pattern, line_lower, re.IGNORECASE):
                    # Additional check: headers are usually short and may be in caps
                    if len(line_stripped) < 100:
                        # Save previous section content
                        if current_section and section_content:
                            sections[current_section] = '\n'.join(section_content).strip()
                        
                        # Start new section
                        current_section = section_name
                        section_content = []
                        section_found = True
                        break
            if section_found:
                break
        
        # Add line to current section if not a header
        if not section_found and current_section:
            section_content.append(line)
    
    # Save last section
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content).strip()
    
    return sections


def extract_contact_info(text: str, nlp: spacy.Language) -> Dict[str, Optional[str]]:
    """
    Extracts contact information from resume text.
    
    Args:
        text: Resume text content
        nlp: Loaded spaCy Language model
        
    Returns:
        Dictionary with contact information
        Example: {"email": "...", "phone": "...", "linkedin": "...", 
                  "github": "...", "portfolio": "..."}
                  
    Validates:
        - Requirements 5.6: Extract contact information (email, phone, LinkedIn, GitHub, portfolio)
    """
    contact_info = {
        'email': None,
        'phone': None,
        'linkedin': None,
        'github': None,
        'portfolio': None
    }
    
    # Extract email
    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        contact_info['email'] = email_match.group(0)
    
    # Extract phone
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        contact_info['phone'] = phone_match.group(0)
    
    # Extract LinkedIn
    linkedin_match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group(0)
    
    # Extract GitHub
    github_match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = github_match.group(0)
    
    # Extract portfolio (excluding LinkedIn and GitHub)
    portfolio_matches = re.finditer(PORTFOLIO_PATTERN, text, re.IGNORECASE)
    for match in portfolio_matches:
        url = match.group(0)
        if 'linkedin' not in url.lower() and 'github' not in url.lower():
            contact_info['portfolio'] = url
            break
    
    return contact_info


def extract_skills(text: str, skills_section: str, nlp: spacy.Language) -> List[str]:
    """
    Extracts technical and soft skills from the skills section and full text.
    
    Args:
        text: Full resume text content
        skills_section: Extracted skills section content
        nlp: Loaded spaCy Language model
        
    Returns:
        List of identified skills
        
    Validates:
        - Requirements 5.4: Extract skills with technical and soft skills categorization
    """
    skills = set()
    
    # Primary extraction from skills section
    if skills_section:
        # Split by common delimiters
        skill_text = skills_section.replace('•', ',').replace('|', ',').replace(';', ',')
        potential_skills = [s.strip() for s in skill_text.split(',')]
        
        for skill in potential_skills:
            if skill and len(skill) > 1 and len(skill) < 50:
                # Clean up the skill
                skill_clean = skill.strip(string.punctuation + string.whitespace)
                if skill_clean:
                    skills.add(skill_clean)
    
    # Use NER to find additional skills from full text
    doc = nlp(text[:10000])  # Limit to first 10k chars for performance
    
    # Extract technical terms and product names
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
            skill_text = ent.text.strip()
            if len(skill_text) > 1 and len(skill_text) < 50:
                # Check if it's a known technical skill
                if any(tech in skill_text.lower() for tech in TECHNICAL_SKILLS_KEYWORDS):
                    skills.add(skill_text)
    
    # Extract noun chunks that might be skills
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        if any(tech in chunk_text for tech in TECHNICAL_SKILLS_KEYWORDS):
            skills.add(chunk.text.strip())
    
    return sorted(list(skills))


def extract_projects(text: str, projects_section: str, nlp: spacy.Language) -> List[Dict[str, str]]:
    """
    Extracts project descriptions with titles and details.
    
    Args:
        text: Full resume text content
        projects_section: Extracted projects section content
        nlp: Loaded spaCy Language model
        
    Returns:
        List of project dictionaries
        Example: [{"title": "...", "description": "...", "technologies": [...]}, ...]
        
    Validates:
        - Requirements 5.5: Extract projects section with title and description parsing
    """
    projects = []
    
    if not projects_section:
        return projects
    
    # Split projects by common patterns (bullet points, numbers, blank lines)
    project_blocks = re.split(r'\n\s*\n|(?=\n\s*[•\-\*]\s)|(?=\n\s*\d+\.)', projects_section)
    
    for block in project_blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue
        
        # Try to identify project title (usually first line or bolded text)
        lines = block.split('\n')
        title = lines[0].strip().strip('•-*0123456789. ')
        
        # Rest is description
        description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else block
        
        # Extract technologies mentioned
        technologies = []
        doc = nlp(block[:1000])  # Limit for performance
        
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'ORG']:
                tech = ent.text.strip()
                if any(keyword in tech.lower() for keyword in TECHNICAL_SKILLS_KEYWORDS):
                    technologies.append(tech)
        
        projects.append({
            'title': title[:200],  # Limit title length
            'description': description[:1000],  # Limit description length
            'technologies': list(set(technologies))
        })
    
    return projects


def extract_keywords(text: str, nlp: spacy.Language, top_n: int = 20) -> List[str]:
    """
    Extracts key terms using spaCy NER and frequency analysis.
    
    Args:
        text: Resume text content
        nlp: Loaded spaCy Language model
        top_n: Number of top keywords to return
        
    Returns:
        List of extracted keywords
        
    Validates:
        - Requirements 5.4: Keyword extraction using spaCy NER and frequency analysis
    """
    doc = nlp(text[:10000])  # Limit for performance
    
    keywords = []
    
    # Extract named entities
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE', 'SKILL', 'GPE', 'NORP']:
            keywords.append(ent.text.lower())
    
    # Extract important noun chunks
    for chunk in doc.noun_chunks:
        # Filter out very short or very long chunks
        if 2 <= len(chunk.text.split()) <= 4:
            keywords.append(chunk.text.lower())
    
    # Extract technical terms based on POS tags
    for token in doc:
        # Look for proper nouns and technical terms
        if token.pos_ in ['PROPN', 'NOUN'] and not token.is_stop:
            if len(token.text) > 2:
                keywords.append(token.text.lower())
    
    # Count frequency and return top keywords
    keyword_counts = Counter(keywords)
    top_keywords = [kw for kw, count in keyword_counts.most_common(top_n)]
    
    return top_keywords


def detect_action_verbs(text: str, nlp: spacy.Language) -> List[str]:
    """
    Identifies action verbs at the start of bullet points.
    
    Args:
        text: Resume text content
        nlp: Loaded spaCy Language model
        
    Returns:
        List of detected action verbs
        
    Validates:
        - Requirements 5.4: Action verb detection
    """
    detected_verbs = set()
    
    # Split text into lines
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Check if line starts with a bullet point
        if re.match(r'^\s*[•\-\*\◦]\s+', line):
            # Remove bullet point
            line = re.sub(r'^\s*[•\-\*\◦]\s+', '', line)
        
        # Get first word
        words = line.split()
        if words:
            first_word = words[0].lower().strip(string.punctuation)
            
            # Check if it's in our action verbs list
            if first_word in ACTION_VERBS:
                detected_verbs.add(first_word)
            else:
                # Use spaCy to check if it's a verb
                doc = nlp(first_word)
                if doc and doc[0].pos_ == 'VERB':
                    detected_verbs.add(first_word)
    
    return sorted(list(detected_verbs))


def extract_jd_keywords(jd_text: str, nlp: spacy.Language, top_n: int = 30) -> List[str]:
    """
    Extracts keywords from job description text.
    Uses similar approach to resume keyword extraction but focuses on requirements.
    
    Args:
        jd_text: Job description text content
        nlp: Loaded spaCy Language model
        top_n: Number of top keywords to return
        
    Returns:
        List of extracted keywords from job description
        
    Validates:
        - Requirements 10.1: Extract keywords from job description
    """
    # Use the same keyword extraction logic as resumes
    return extract_keywords(jd_text, nlp, top_n)


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_process_resume(text_hash: str, text: str, _nlp) -> Dict:
    """
    Internal cached version of resume processing.
    
    Args:
        text_hash: Hash of text content for cache key
        text: Resume text content
        _nlp: spaCy model (underscore prefix excludes from hashing)
        
    Returns:
        Dictionary containing all extracted information
        
    Validates:
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    # Extract all components
    sections = extract_sections(text, _nlp)
    contact_info = extract_contact_info(text, _nlp)
    skills = extract_skills(text, sections.get('skills', ''), _nlp)
    projects = extract_projects(text, sections.get('projects', ''), _nlp)
    keywords = extract_keywords(text, _nlp)
    action_verbs = detect_action_verbs(text, _nlp)
    
    return {
        'sections': sections,
        'contact_info': contact_info,
        'skills': skills,
        'projects': projects,
        'keywords': keywords,
        'action_verbs': action_verbs
    }


def process_resume_text(text: str, nlp: Optional[spacy.Language] = None, use_cache: bool = True) -> Dict:
    """
    Complete text processing pipeline for resume analysis.
    
    Args:
        text: Resume text content
        nlp: Optional pre-loaded spaCy model (will load if not provided)
        use_cache: Whether to use caching for results (default: True)
        
    Returns:
        Dictionary containing all extracted information:
        {
            'sections': {...},
            'contact_info': {...},
            'skills': [...],
            'projects': [...],
            'keywords': [...],
            'action_verbs': [...]
        }
        
    Validates:
        - Requirements 5.1-5.6: All section and information extraction
        - Requirements 14.1: Use locally loaded spaCy model
        - Requirements 16.1: Cache model for reuse
        - Requirements 16.2: Cache results for identical inputs
    """
    # Load model if not provided
    if nlp is None:
        nlp = load_spacy_model()
    
    if use_cache:
        # Generate hash for caching
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_process_resume(text_hash, text, nlp)
    else:
        # Direct processing without cache
        sections = extract_sections(text, nlp)
        contact_info = extract_contact_info(text, nlp)
        skills = extract_skills(text, sections.get('skills', ''), nlp)
        projects = extract_projects(text, sections.get('projects', ''), nlp)
        keywords = extract_keywords(text, nlp)
        action_verbs = detect_action_verbs(text, nlp)
        
        return {
            'sections': sections,
            'contact_info': contact_info,
            'skills': skills,
            'projects': projects,
            'keywords': keywords,
            'action_verbs': action_verbs
        }
