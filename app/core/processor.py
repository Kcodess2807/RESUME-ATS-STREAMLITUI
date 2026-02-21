import re
import streamlit as st
import spacy
from typing import Dict, List, Optional, Tuple
from collections import Counter
import string
from app.core.processor_extractors import extract_sections, extract_contact_info, extract_skills, extract_projects, extract_keywords, detect_action_verbs, extract_jd_keywords


@st.cache_resource
def load_spacy_model(model_name: str='en_core_web_md'):
    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError:
        try:
            nlp = spacy.load('en_core_web_sm')
            st.warning(
                f'Could not load {model_name}, using en_core_web_sm instead')
            return nlp
        except OSError:
            st.error(
                f'spaCy model not found. Please run: python -m spacy download {model_name}'
                )
            raise


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_process_resume(text_hash: str, text: str, _nlp) ->Dict:
    sections = extract_sections(text, _nlp)
    contact_info = extract_contact_info(text, _nlp)
    skills = extract_skills(text, sections.get('skills', ''), _nlp)
    projects = extract_projects(text, sections.get('projects', ''), _nlp)
    keywords = extract_keywords(text, _nlp)
    action_verbs = detect_action_verbs(text, _nlp)
    return {'sections': sections, 'contact_info': contact_info, 'skills':
        skills, 'projects': projects, 'keywords': keywords, 'action_verbs':
        action_verbs}


def process_resume_text(text: str, nlp: Optional[spacy.Language]=None,
    use_cache: bool=True) ->Dict:
    if nlp is None:
        nlp = load_spacy_model()
    if use_cache:
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_process_resume(text_hash, text, nlp)
    else:
        sections = extract_sections(text, nlp)
        contact_info = extract_contact_info(text, nlp)
        skills = extract_skills(text, sections.get('skills', ''), nlp)
        projects = extract_projects(text, sections.get('projects', ''), nlp)
        keywords = extract_keywords(text, nlp)
        action_verbs = detect_action_verbs(text, nlp)
        return {'sections': sections, 'contact_info': contact_info,
            'skills': skills, 'projects': projects, 'keywords': keywords,
            'action_verbs': action_verbs}
