"""
Model Loader Module
Handles initialization and caching of all AI models used in the application.

This module provides centralized model loading with:
- @st.cache_resource for persistent model caching
- Lazy loading support for optional features
- Fallback mechanisms for model loading failures
- Comprehensive error handling with troubleshooting guidance

Requirements: 14.1, 14.2, 14.3, 14.4, 15.5, 16.1
"""

import streamlit as st
import spacy
from sentence_transformers import SentenceTransformer
import nltk
import os
from typing import Optional, Dict, Any

# Try to import language_tool_python, but make it optional
try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False

from utils.error_handler import (
    ModelLoadError,
    ErrorCategory,
    log_error,
    log_warning,
    log_info
)


# Track model loading status for diagnostics
_model_load_times: Dict[str, float] = {}
_model_load_errors: Dict[str, str] = {}


@st.cache_resource(show_spinner=False)
def load_spacy_model(model_name: str = "en_core_web_sm"):
    """
    Load and cache spaCy language model.
    
    Uses @st.cache_resource to ensure the model is loaded only once
    and reused across all sessions and reruns.
    
    Args:
        model_name: Name of the spaCy model to load
        
    Returns:
        Loaded spaCy Language object
        
    Raises:
        OSError: If model is not installed
        
    Validates:
        - Requirements 14.1: Load spaCy model from local storage
        - Requirements 14.4: Cache models in memory for reuse
        - Requirements 15.5: Provide troubleshooting steps on failure
    """
    import time
    start_time = time.time()
    
    try:
        nlp = spacy.load(model_name)
        _model_load_times['spacy'] = time.time() - start_time
        log_info(f"spaCy model '{model_name}' loaded in {_model_load_times['spacy']:.2f}s", context="model_loader")
        return nlp
    except OSError as primary_error:
        log_warning(f"Primary spaCy model '{model_name}' not found, trying fallback", context="model_loader")
        
        # Try smaller model as fallback
        try:
            nlp = spacy.load("en_core_web_sm")
            _model_load_times['spacy'] = time.time() - start_time
            log_info(f"spaCy fallback model 'en_core_web_sm' loaded in {_model_load_times['spacy']:.2f}s", context="model_loader")
            return nlp
        except OSError as fallback_error:
            error_msg = (
                f"spaCy model not found. Please run one of the following commands:\n"
                f"  python -m spacy download {model_name}\n"
                f"  python -m spacy download en_core_web_sm\n\n"
                f"If the issue persists, try:\n"
                f"  pip install spacy --upgrade\n"
                f"  pip install {model_name}"
            )
            _model_load_errors['spacy'] = error_msg
            log_error(fallback_error, context="load_spacy_model", category=ErrorCategory.MODEL_LOADING)
            st.error(error_msg)
            raise ModelLoadError(
                message=f"Failed to load spaCy model: {str(fallback_error)}",
                model_name=model_name,
                user_message="The language processing model could not be loaded. Please check the troubleshooting steps.",
                original_error=fallback_error
            )


@st.cache_resource(show_spinner=False)
def load_sentence_transformer(model_name: str = "all-MiniLM-L6-v2"):
    """
    Load and cache Sentence-Transformers model for embeddings.
    
    Uses @st.cache_resource to ensure the model is loaded only once
    and reused across all sessions and reruns.
    
    Args:
        model_name: Name of the Sentence-Transformers model
        
    Returns:
        Loaded SentenceTransformer object
        
    Validates:
        - Requirements 14.2: Load Sentence-Transformers model from local storage
        - Requirements 14.4: Cache models in memory for reuse
        - Requirements 15.5: Provide troubleshooting steps on failure
    """
    import time
    start_time = time.time()
    
    try:
        embedder = SentenceTransformer(model_name)
        _model_load_times['sentence_transformer'] = time.time() - start_time
        log_info(f"Sentence-Transformers model '{model_name}' loaded in {_model_load_times['sentence_transformer']:.2f}s", context="model_loader")
        return embedder
    except Exception as e:
        error_msg = (
            f"Failed to load Sentence-Transformers model '{model_name}'.\n\n"
            f"Troubleshooting steps:\n"
            f"  1. pip install sentence-transformers --upgrade\n"
            f"  2. Ensure you have internet access for first-time model download\n"
            f"  3. Check disk space for model cache (~100MB)\n"
            f"  4. Try: pip install torch --upgrade"
        )
        _model_load_errors['sentence_transformer'] = error_msg
        log_error(e, context="load_sentence_transformer", category=ErrorCategory.MODEL_LOADING)
        st.error(error_msg)
        raise ModelLoadError(
            message=f"Failed to load Sentence-Transformers model: {str(e)}",
            model_name=model_name,
            user_message="The embedding model could not be loaded. Please check the troubleshooting steps.",
            original_error=e
        )


@st.cache_resource(show_spinner=False)
def load_language_tool(language: str = "en-US"):
    """
    Load and cache LanguageTool for grammar checking.
    
    Uses @st.cache_resource to ensure the tool is loaded only once
    and reused across all sessions and reruns.
    
    Args:
        language: Language code for grammar checking
        
    Returns:
        Loaded LanguageTool object, or None if not available
        
    Validates:
        - Requirements 14.3: Initialize LanguageTool locally
        - Requirements 14.4: Cache models in memory for reuse
        - Requirements 15.5: Provide troubleshooting steps on failure
    """
    import time
    start_time = time.time()
    
    if not LANGUAGE_TOOL_AVAILABLE:
        log_warning("LanguageTool not available (language-tool-python not installed)", context="model_loader")
        return None
    
    try:
        tool = language_tool_python.LanguageTool(language)
        _model_load_times['language_tool'] = time.time() - start_time
        log_info(f"LanguageTool for '{language}' loaded in {_model_load_times['language_tool']:.2f}s", context="model_loader")
        return tool
    except Exception as e:
        # Log warning but don't crash - grammar checking is optional
        log_warning(f"LanguageTool unavailable: {str(e)}", context="model_loader")
        _model_load_errors['language_tool'] = f"Grammar checking unavailable (requires Java): {str(e)}"
        return None


@st.cache_data(show_spinner=False)
def ensure_nltk_data():
    """
    Ensure required NLTK data packages are downloaded.
    Downloads packages if not already present.
    
    Uses @st.cache_data to run only once per session.
    
    Returns:
        bool: True if all packages are available
    """
    required_packages = [
        ('punkt', 'tokenizers/punkt'),
        ('stopwords', 'corpora/stopwords'),
        ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger'),
        ('wordnet', 'corpora/wordnet')
    ]
    
    all_available = True
    
    for package, path in required_packages:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except Exception as e:
                all_available = False
    
    return all_available


def initialize_all_models(show_progress: bool = True):
    """
    Initialize all models at application startup.
    
    This function should be called once when the app starts.
    Models are cached by @st.cache_resource, so subsequent calls
    return cached instances.
    
    Args:
        show_progress: Whether to show loading spinner
        
    Returns:
        dict: Dictionary containing all loaded models
        
    Validates:
        - Requirements 14.1, 14.2, 14.3: Load all models from local storage
        - Requirements 14.4: Cache models in memory
        - Requirements 16.1: Cache for reuse in subsequent analyses
    """
    if show_progress:
        with st.spinner("Loading AI models... This may take a moment on first run."):
            return _load_all_models()
    else:
        return _load_all_models()


def _load_all_models() -> Dict[str, Any]:
    """Internal function to load all models."""
    # Ensure NLTK data is available
    ensure_nltk_data()
    
    # Load all models (cached by @st.cache_resource)
    models = {
        'nlp': load_spacy_model(),
        'embedder': load_sentence_transformer(),
        'grammar_tool': load_language_tool()
    }
    
    return models


def get_models() -> Dict[str, Any]:
    """
    Get all models, initializing them if necessary.
    
    Uses session state to track initialization status.
    
    Returns:
        dict: Dictionary containing all loaded models
        
    Validates:
        - Requirements 14.4: Cache models in memory for reuse
        - Requirements 16.1: Reuse cached models
    """
    if 'models_initialized' not in st.session_state:
        st.session_state.models = initialize_all_models()
        st.session_state.models_initialized = True
    
    return st.session_state.models


def get_model_load_times() -> Dict[str, float]:
    """
    Get model loading times for performance monitoring.
    
    Returns:
        dict: Dictionary mapping model names to load times in seconds
    """
    return _model_load_times.copy()


def preload_models_async():
    """
    Preload models in the background for faster first analysis.
    
    This function can be called early in the application lifecycle
    to start loading models before they are needed.
    
    Validates:
        - Requirements 14.4: Lazy loading for optional features
    """
    # Models are loaded lazily by @st.cache_resource
    # This function triggers the loading
    try:
        load_spacy_model()
        load_sentence_transformer()
        # Grammar tool is optional, load lazily
    except Exception:
        pass  # Errors will be handled when models are actually used


def is_model_loaded(model_name: str) -> bool:
    """
    Check if a specific model has been loaded.
    
    Args:
        model_name: Name of the model ('nlp', 'embedder', 'grammar_tool')
        
    Returns:
        bool: True if model is loaded
    """
    return model_name in _model_load_times


def get_model_status() -> Dict[str, Any]:
    """
    Get status information about all models.
    
    Returns:
        dict: Status information for each model
        
    Validates:
        - Requirements 15.5: Provide model status for troubleshooting
    """
    return {
        'spacy': {
            'loaded': 'spacy' in _model_load_times,
            'load_time': _model_load_times.get('spacy', None),
            'error': _model_load_errors.get('spacy', None)
        },
        'sentence_transformer': {
            'loaded': 'sentence_transformer' in _model_load_times,
            'load_time': _model_load_times.get('sentence_transformer', None),
            'error': _model_load_errors.get('sentence_transformer', None)
        },
        'language_tool': {
            'loaded': 'language_tool' in _model_load_times,
            'load_time': _model_load_times.get('language_tool', None),
            'error': _model_load_errors.get('language_tool', None)
        }
    }


def get_model_load_errors() -> Dict[str, str]:
    """
    Get any model loading errors that occurred.
    
    Returns:
        dict: Dictionary mapping model names to error messages
    """
    return _model_load_errors.copy()


def clear_model_errors() -> None:
    """Clear stored model loading errors."""
    _model_load_errors.clear()
