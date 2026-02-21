"""
Cache Manager Module for ATS Resume Scorer

This module provides centralized caching functionality for:
- Model caching using @st.cache_resource
- Result caching for identical resumes using @st.cache_data
- Hash-based cache key generation for resume content

Requirements: 14.4, 16.1, 16.2
"""

import streamlit as st
import hashlib
from typing import Dict, Any, Optional, Callable
from functools import wraps
import time


def generate_content_hash(content: str) -> str:
    """
    Generate a hash key for content-based caching.
    
    Args:
        content: Text content to hash
        
    Returns:
        SHA-256 hash string of the content
        
    Validates:
        - Requirements 16.1: Cache results for identical inputs
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def get_cache_key(resume_text: str, jd_text: Optional[str] = None) -> str:
    """
    Generate a unique cache key for a resume analysis.
    
    Args:
        resume_text: Resume text content
        jd_text: Optional job description text
        
    Returns:
        Combined hash key for caching
        
    Validates:
        - Requirements 16.1: Cache results for identical inputs
        - Requirements 16.2: Reuse cached results
    """
    resume_hash = generate_content_hash(resume_text)
    
    if jd_text:
        jd_hash = generate_content_hash(jd_text)
        return f"{resume_hash}_{jd_hash}"
    
    return resume_hash


@st.cache_data(ttl=3600, show_spinner=False)
def cached_text_processing(text_hash: str, text: str, _nlp) -> Dict[str, Any]:
    """
    Cache text processing results for identical resume content.
    
    Args:
        text_hash: Hash of the text content (for cache key)
        text: Resume text to process
        _nlp: spaCy model (underscore prefix excludes from hashing)
        
    Returns:
        Processed text data dictionary
        
    Validates:
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    from utils.text_processor import process_resume_text
    return process_resume_text(text, _nlp)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_skill_validation(
    skills_tuple: tuple,
    projects_hash: str,
    experience_hash: str,
    _embedder,
    threshold: float = 0.6
) -> Dict[str, Any]:
    """
    Cache skill validation results.
    
    Args:
        skills_tuple: Tuple of skills (hashable)
        projects_hash: Hash of projects data
        experience_hash: Hash of experience text
        _embedder: Sentence transformer model
        threshold: Similarity threshold
        
    Returns:
        Skill validation results dictionary
        
    Validates:
        - Requirements 16.1: Cache expensive computations
    """
    # This function is called with pre-computed hashes
    # The actual validation is done in the caller
    pass  # Placeholder - actual caching is done at call site


@st.cache_data(ttl=3600, show_spinner=False)
def cached_grammar_check(text_hash: str, text: str, _grammar_tool) -> Dict[str, Any]:
    """
    Cache grammar check results for identical text.
    
    Args:
        text_hash: Hash of the text content
        text: Text to check
        _grammar_tool: LanguageTool instance
        
    Returns:
        Grammar check results dictionary
        
    Validates:
        - Requirements 16.1: Cache expensive computations
    """
    from utils.grammar_checker import check_grammar_and_spelling
    return check_grammar_and_spelling(text, _grammar_tool)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_location_detection(text_hash: str, text: str, _nlp) -> Dict[str, Any]:
    """
    Cache location detection results for identical text.
    
    Args:
        text_hash: Hash of the text content
        text: Text to analyze
        _nlp: spaCy model
        
    Returns:
        Location detection results dictionary
        
    Validates:
        - Requirements 16.1: Cache expensive computations
    """
    from utils.location_detector import detect_location_info
    return detect_location_info(text, _nlp)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_jd_comparison(
    resume_hash: str,
    jd_hash: str,
    resume_text: str,
    resume_keywords: tuple,
    resume_skills: tuple,
    jd_text: str,
    jd_keywords: tuple,
    _embedder,
    _nlp
) -> Dict[str, Any]:
    """
    Cache JD comparison results.
    
    Args:
        resume_hash: Hash of resume text
        jd_hash: Hash of JD text
        resume_text: Resume text content
        resume_keywords: Tuple of resume keywords
        resume_skills: Tuple of resume skills
        jd_text: Job description text
        jd_keywords: Tuple of JD keywords
        _embedder: Sentence transformer model
        _nlp: spaCy model
        
    Returns:
        JD comparison results dictionary
        
    Validates:
        - Requirements 16.1: Cache expensive computations
    """
    from utils.jd_comparator import compare_resume_with_jd
    return compare_resume_with_jd(
        resume_text=resume_text,
        resume_keywords=list(resume_keywords),
        resume_skills=list(resume_skills),
        jd_text=jd_text,
        jd_keywords=list(jd_keywords),
        embedder=_embedder,
        nlp=_nlp
    )


def get_cached_analysis_results(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached analysis results from session state.
    
    Args:
        cache_key: Cache key for the analysis
        
    Returns:
        Cached results if available, None otherwise
        
    Validates:
        - Requirements 16.2: Reuse cached results
    """
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    
    return st.session_state.analysis_cache.get(cache_key)


def store_analysis_results(cache_key: str, results: Dict[str, Any]) -> None:
    """
    Store analysis results in session state cache.
    
    Args:
        cache_key: Cache key for the analysis
        results: Analysis results to cache
        
    Validates:
        - Requirements 16.1: Cache results for reuse
    """
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    
    # Limit cache size to prevent memory issues
    MAX_CACHE_SIZE = 10
    if len(st.session_state.analysis_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entry
        oldest_key = next(iter(st.session_state.analysis_cache))
        del st.session_state.analysis_cache[oldest_key]
    
    st.session_state.analysis_cache[cache_key] = {
        'results': results,
        'timestamp': time.time()
    }


def clear_analysis_cache() -> None:
    """
    Clear all cached analysis results from session state.
    """
    if 'analysis_cache' in st.session_state:
        st.session_state.analysis_cache = {}


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the current cache state.
    
    Returns:
        Dictionary with cache statistics
    """
    cache = st.session_state.get('analysis_cache', {})
    
    return {
        'cached_analyses': len(cache),
        'cache_keys': list(cache.keys())[:5],  # Show first 5 keys
        'oldest_entry': min(
            (entry['timestamp'] for entry in cache.values()),
            default=None
        ) if cache else None
    }


class LazyLoader:
    """
    Lazy loader for optional features and models.
    
    Delays loading of expensive resources until they are actually needed.
    
    Validates:
        - Requirements 14.4: Lazy loading for optional features
    """
    
    def __init__(self):
        self._loaded = {}
    
    def get_grammar_checker(self):
        """Lazily load grammar checker only when needed."""
        if 'grammar_checker' not in self._loaded:
            from utils.grammar_checker import load_grammar_checker
            self._loaded['grammar_checker'] = load_grammar_checker()
        return self._loaded['grammar_checker']
    
    def get_embedder(self):
        """Lazily load sentence transformer only when needed."""
        if 'embedder' not in self._loaded:
            from utils.skill_validator import load_embedder
            self._loaded['embedder'] = load_embedder()
        return self._loaded['embedder']
    
    def get_spacy_model(self):
        """Lazily load spaCy model only when needed."""
        if 'nlp' not in self._loaded:
            from utils.text_processor import load_spacy_model
            self._loaded['nlp'] = load_spacy_model()
        return self._loaded['nlp']
    
    def is_loaded(self, resource_name: str) -> bool:
        """Check if a resource has been loaded."""
        return resource_name in self._loaded
    
    def get_loaded_resources(self) -> list:
        """Get list of currently loaded resources."""
        return list(self._loaded.keys())


# Global lazy loader instance
_lazy_loader = None


def get_lazy_loader() -> LazyLoader:
    """
    Get the global lazy loader instance.
    
    Returns:
        LazyLoader instance
    """
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = LazyLoader()
    return _lazy_loader
