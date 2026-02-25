"""
Resume Text Processor Module
Orchestrates NLP analysis of raw resume text — sections, skills, keywords, projects.

📌 TEACHING NOTE — What does this file do?
    After parser.py extracts raw text from the resume file, THIS module
    turns that raw text into STRUCTURED DATA that the scoring engine can use.

    Input:  "John Smith\nSoftware Engineer\n\nSkills: Python, React, AWS..."
    Output: {
        'sections':     {'experience': '...', 'education': '...', ...},
        'contact_info': {'email': 'john@email.com', 'phone': '...'},
        'skills':       ['Python', 'React', 'AWS', ...],
        'projects':     [{'title': '...', 'technologies': [...]}],
        'keywords':     ['machine learning', 'docker', ...],
        'action_verbs': ['led', 'built', 'optimized', ...]
    }

📌 TEACHING NOTE — Two-file design:
    processor.py           ← YOU ARE HERE (orchestrator + caching)
    processor_extractors.py → individual extraction functions

    This split keeps the caching logic separate from the extraction logic.
    processor.py decides WHEN and HOW to cache.
    processor_extractors.py focuses purely on HOW to extract each thing.

📌 TEACHING NOTE — Why @st.cache_resource for the spaCy model?
    spaCy models are large (50MB+) and slow to load (~2-5 seconds).
    @st.cache_resource loads once and reuses across all users and sessions.
    @st.cache_data would serialize/copy the model on every call — very slow.
    For heavy shared objects (ML models, DB connections), always use cache_resource.
"""

import re
import streamlit as st
import spacy
from typing import Dict, List, Optional, Tuple
from collections import Counter
import string

# All extraction logic lives in the companion file
from app.core.processor_extractors import (
    extract_sections,
    extract_contact_info,
    extract_skills,
    extract_projects,
    extract_keywords,
    detect_action_verbs,
    extract_jd_keywords
)


@st.cache_resource
def load_spacy_model(model_name: str = 'en_core_web_md'):
    """
    Load and cache a spaCy NLP model — shared across all users.

    📌 TEACHING NOTE — @st.cache_resource:
        This decorator tells Streamlit: "run this function only ONCE,
        then store the result and return the same object on every future call."

        Unlike @st.cache_data (which stores serializable data like dicts/strings),
        @st.cache_resource stores live Python objects like ML models.

        Why does this matter? A spaCy model:
        - Takes 2-5 seconds to load
        - Uses ~200MB of RAM
        - Can safely be shared (it's read-only after loading)

        Without caching: every user reloads the model on every page load → slow.
        With cache_resource: model loads once, reused by everyone → fast.

    📌 TEACHING NOTE — Fallback model (en_core_web_sm):
        The function tries to load 'en_core_web_md' (medium model, better accuracy).
        If that fails (model not installed), it falls back to 'en_core_web_sm'
        (small model, less accurate but still functional) with a Streamlit warning.
        If THAT also fails, it raises an error with clear installation instructions.

        This "try best, fall back gracefully, error clearly" pattern ensures:
        - Best experience when dependencies are properly set up
        - Degraded-but-working experience when they're not
        - Clear actionable error when nothing works

    Args:
        model_name: spaCy model to load (default: 'en_core_web_md')

    Returns:
        Loaded spaCy Language object, shared across all users

    Raises:
        OSError: If neither the requested model nor the fallback can be loaded
    """
    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError:
        # Primary model not found — try the smaller fallback
        try:
            nlp = spacy.load('en_core_web_sm')
            st.warning(f'Could not load {model_name}, using en_core_web_sm instead')
            return nlp
        except OSError:
            # Neither model available — fail with clear instructions
            st.error(f'spaCy model not found. Please run: python -m spacy download {model_name}')
            raise


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_process_resume(text_hash: str, text: str, _nlp) -> Dict:
    """
    Cached internal function — runs the full NLP extraction pipeline.

    📌 TEACHING NOTE — Why separate this from process_resume_text()?
        @st.cache_data requires ALL arguments to be hashable (serializable).
        The nlp model object is NOT hashable (it's a complex C++ object).

        Solution: Use the underscore prefix trick:
            _nlp (with underscore) → Streamlit EXCLUDES this from the cache key
            Only text_hash and text are used as cache key components.

        So the cache key is effectively: (text_hash, text)
        Same text = same cache hit, regardless of which nlp object is passed.

    📌 TEACHING NOTE — text_hash AND text — why both?
        text_hash (SHA-256) is the CACHE KEY — fast to compare.
        text is the ACTUAL DATA — passed to the extraction functions.

        We don't use text as the key directly because:
        - Very long strings slow down cache key hashing
        - SHA-256 is a fast fixed-size (64 char) unique fingerprint

        We can't use ONLY the hash because the extraction functions need
        the actual text to work with. So both are passed.

    Args:
        text_hash: SHA-256 fingerprint of resume text (cache key component)
        text: Actual resume text (for processing)
        _nlp: spaCy model (excluded from cache key by _ prefix)

    Returns:
        Dict with sections, contact_info, skills, projects, keywords, action_verbs
    """
    # Run all extraction functions and combine results into one dict
    sections     = extract_sections(text, _nlp)
    contact_info = extract_contact_info(text, _nlp)
    skills       = extract_skills(text, sections.get('skills', ''), _nlp)
    projects     = extract_projects(text, sections.get('projects', ''), _nlp)
    keywords     = extract_keywords(text, _nlp)
    action_verbs = detect_action_verbs(text, _nlp)

    return {
        'sections':     sections,
        'contact_info': contact_info,
        'skills':       skills,
        'projects':     projects,
        'keywords':     keywords,
        'action_verbs': action_verbs
    }


def process_resume_text(
    text: str,
    nlp: Optional[spacy.Language] = None,
    use_cache: bool = True
) -> Dict:
    """
    Public entry point — process raw resume text into structured data.

    📌 TEACHING NOTE — Three-layer pattern (consistent throughout this codebase):
        Layer 1 (this function): public API, handles optional model loading and cache decision
        Layer 2 (_cached_process_resume): @st.cache_data wrapper
        Layer 3 (processor_extractors.py): pure extraction logic

        This pattern appears in detector.py, comparator.py, and validator.py too.
        It cleanly separates concerns:
        - Public interface (this)
        - Cache mechanics (_cached_*)
        - Business logic (extractors)

    📌 TEACHING NOTE — use_cache=False path (uncached):
        When use_cache=False, the function runs all extractions directly
        WITHOUT going through the cache layer. This is important for:
        - Unit tests (you want fresh results, not cached ones)
        - Debugging (you want to see what actually happens now)
        - Forced refresh (user clicks "re-analyze" button)

        Notice: when not caching, the exact same extraction calls are made —
        just calling the extractor functions directly, not through _cached_process_resume().
        This means there's slight code duplication. A refactor could extract
        the common logic into a _run_extraction(text, nlp) helper.
        ⚠️ This is a minor DRY violation worth flagging for students.

    📌 TEACHING NOTE — Optional nlp parameter with lazy loading:
        nlp: Optional[spacy.Language] = None
        If the caller doesn't provide an nlp model, we load one automatically.
        This makes the function convenient to call without managing model state,
        but still allows callers who already have a model to pass it in (avoiding
        the overhead of loading it again).

    Args:
        text: Raw resume text (from parser.py)
        nlp: Optional pre-loaded spaCy model
        use_cache: Whether to use Streamlit caching (default True)

    Returns:
        Dict with sections, contact_info, skills, projects, keywords, action_verbs
    """
    # Auto-load the model if one wasn't provided
    if nlp is None:
        nlp = load_spacy_model()

    if use_cache:
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_process_resume(text_hash, text, nlp)
    else:
        # Run directly without caching — same logic as _cached_process_resume()
        # ⚠️ DRY violation: this duplicates the logic from _cached_process_resume()
        sections     = extract_sections(text, nlp)
        contact_info = extract_contact_info(text, nlp)
        skills       = extract_skills(text, sections.get('skills', ''), nlp)
        projects     = extract_projects(text, sections.get('projects', ''), nlp)
        keywords     = extract_keywords(text, nlp)
        action_verbs = detect_action_verbs(text, nlp)
        return {
            'sections':     sections,
            'contact_info': contact_info,
            'skills':       skills,
            'projects':     projects,
            'keywords':     keywords,
            'action_verbs': action_verbs
        }