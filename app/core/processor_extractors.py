import re
import streamlit as st
import spacy
from typing import Dict, List, Optional, Tuple
from collections import Counter
import string

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

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
LINKEDIN_PATTERN = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
GITHUB_PATTERN = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
PORTFOLIO_PATTERN = r'(?:https?://)?(?:www\.)?[\w-]+\.(?:com|net|org|io|dev|me)(?:/[\w-]*)?'

ACTION_VERBS = {
    'achieved', 'adapted', 'administered', 'analyzed', 'architected', 'automated',
    'built', 'collaborated', 'completed', 'conducted', 'configured', 'created',
    'delivered', 'demonstrated', 'designed', 'developed', 'directed', 'drove',
    'enhanced', 'established', 'executed', 'expanded', 'facilitated', 'generated',
    'implemented', 'improved', 'increased', 'initiated', 'integrated', 'launched',
    'led', 'maintained', 'managed', 'optimized', 'organized', 'performed',
    'planned', 'produced', 'programmed', 'reduced', 'resolved', 'streamlined',
    'strengthened', 'supervised', 'supported', 'trained', 'transformed', 'upgraded'
}

TECHNICAL_SKILLS_KEYWORDS = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
    'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'express',
    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
    'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'devops'
}


def extract_sections(text: str, nlp: spacy.Language) ->Dict[str, str]:
    sections = {'summary': '', 'experience': '', 'education': '', 'skills':
        '', 'projects': ''}
    lines = text.split('\n')
    current_section = None
    section_content = []
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        if not line_stripped:
            if current_section and section_content:
                section_content.append(line)
            continue
        section_found = False
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    if len(line_stripped) < 100:
                        if current_section and section_content:
                            sections[current_section] = '\n'.join(
                                section_content).strip()
                        current_section = section_name
                        section_content = []
                        section_found = True
                        break
            if section_found:
                break
        if not section_found and current_section:
            section_content.append(line)
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content).strip()
    return sections


def extract_contact_info(text: str, nlp: spacy.Language) ->Dict[str,
    Optional[str]]:
    contact_info = {'email': None, 'phone': None, 'linkedin': None,
        'github': None, 'portfolio': None}
    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        contact_info['email'] = email_match.group(0)
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        contact_info['phone'] = phone_match.group(0)
    linkedin_match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group(0)
    github_match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = github_match.group(0)
    portfolio_matches = re.finditer(PORTFOLIO_PATTERN, text, re.IGNORECASE)
    for match in portfolio_matches:
        url = match.group(0)
        if 'linkedin' not in url.lower() and 'github' not in url.lower():
            contact_info['portfolio'] = url
            break
    return contact_info


def extract_skills(text: str, skills_section: str, nlp: spacy.Language) ->List[
    str]:
    skills = set()
    if skills_section:
        skill_text = skills_section.replace('•', ',').replace('|', ','
            ).replace(';', ',')
        potential_skills = [s.strip() for s in skill_text.split(',')]
        for skill in potential_skills:
            if skill and len(skill) > 1 and len(skill) < 50:
                skill_clean = skill.strip(string.punctuation + string.
                    whitespace)
                if skill_clean:
                    skills.add(skill_clean)
    doc = nlp(text[:10000])
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
            skill_text = ent.text.strip()
            if len(skill_text) > 1 and len(skill_text) < 50:
                if any(tech in skill_text.lower() for tech in
                    TECHNICAL_SKILLS_KEYWORDS):
                    skills.add(skill_text)
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        if any(tech in chunk_text for tech in TECHNICAL_SKILLS_KEYWORDS):
            skills.add(chunk.text.strip())
    return sorted(list(skills))


def extract_projects(text: str, projects_section: str, nlp: spacy.Language
    ) ->List[Dict[str, str]]:
    projects = []
    if not projects_section:
        return projects
    project_blocks = re.split(
        '\\n\\s*\\n|(?=\\n\\s*[•\\-\\*]\\s)|(?=\\n\\s*\\d+\\.)',
        projects_section)
    for block in project_blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue
        lines = block.split('\n')
        title = lines[0].strip().strip('•-*0123456789. ')
        description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else block
        technologies = []
        doc = nlp(block[:1000])
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'ORG']:
                tech = ent.text.strip()
                if any(keyword in tech.lower() for keyword in
                    TECHNICAL_SKILLS_KEYWORDS):
                    technologies.append(tech)
        projects.append({'title': title[:200], 'description': description[:
            1000], 'technologies': list(set(technologies))})
    return projects


def extract_keywords(text: str, nlp: spacy.Language, top_n: int=20) ->List[str
    ]:
    doc = nlp(text[:10000])
    keywords = []
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE', 'SKILL', 'GPE', 'NORP'
            ]:
            keywords.append(ent.text.lower())
    for chunk in doc.noun_chunks:
        if 2 <= len(chunk.text.split()) <= 4:
            keywords.append(chunk.text.lower())
    for token in doc:
        if token.pos_ in ['PROPN', 'NOUN'] and not token.is_stop:
            if len(token.text) > 2:
                keywords.append(token.text.lower())
    keyword_counts = Counter(keywords)
    top_keywords = [kw for kw, count in keyword_counts.most_common(top_n)]
    return top_keywords


def detect_action_verbs(text: str, nlp: spacy.Language) ->List[str]:
    detected_verbs = set()
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if re.match('^\\s*[•\\-\\*\\◦]\\s+', line):
            line = re.sub('^\\s*[•\\-\\*\\◦]\\s+', '', line)
        words = line.split()
        if words:
            first_word = words[0].lower().strip(string.punctuation)
            if first_word in ACTION_VERBS:
                detected_verbs.add(first_word)
            else:
                doc = nlp(first_word)
                if doc and doc[0].pos_ == 'VERB':
                    detected_verbs.add(first_word)
    return sorted(list(detected_verbs))


def extract_jd_keywords(jd_text: str, nlp: spacy.Language, top_n: int=30
    ) ->List[str]:
    return extract_keywords(jd_text, nlp, top_n)
