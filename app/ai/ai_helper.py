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
import language_tool_python
import nltk
import os
from typing import Optional, Dict, Any
from utils.error_handler import ModelLoadError, ErrorCategory, log_error, log_warning, log_info
_model_load_times: Dict[str, float] = {}
_model_load_errors: Dict[str, str] = {}


@st.cache_resource(show_spinner=False)
def load_spacy_model(model_name: str='en_core_web_md'):
    import time
    start_time = time.time()
    try:
        nlp = spacy.load(model_name)
        _model_load_times['spacy'] = time.time() - start_time
        log_info(
            f"spaCy model '{model_name}' loaded in {_model_load_times['spacy']:.2f}s"
            , context='model_loader')
        return nlp
    except OSError as primary_error:
        log_warning(
            f"Primary spaCy model '{model_name}' not found, trying fallback",
            context='model_loader')
        try:
            nlp = spacy.load('en_core_web_sm')
            _model_load_times['spacy'] = time.time() - start_time
            log_info(
                f"spaCy fallback model 'en_core_web_sm' loaded in {_model_load_times['spacy']:.2f}s"
                , context='model_loader')
            return nlp
        except OSError as fallback_error:
            error_msg = f"""spaCy model not found. Please run one of the following commands:
  python -m spacy download {model_name}
  python -m spacy download en_core_web_sm

If the issue persists, try:
  pip install spacy --upgrade
  pip install {model_name}"""
            _model_load_errors['spacy'] = error_msg
            log_error(fallback_error, context='load_spacy_model', category=
                ErrorCategory.MODEL_LOADING)
            st.error(error_msg)
            raise ModelLoadError(message=
                f'Failed to load spaCy model: {str(fallback_error)}',
                model_name=model_name, user_message=
                'The language processing model could not be loaded. Please check the troubleshooting steps.'
                , original_error=fallback_error)


@st.cache_resource(show_spinner=False)
def load_sentence_transformer(model_name: str='all-MiniLM-L6-v2'):
    import time
    start_time = time.time()
    try:
        embedder = SentenceTransformer(model_name)
        _model_load_times['sentence_transformer'] = time.time() - start_time
        log_info(
            f"Sentence-Transformers model '{model_name}' loaded in {_model_load_times['sentence_transformer']:.2f}s"
            , context='model_loader')
        return embedder
    except Exception as e:
        error_msg = f"""Failed to load Sentence-Transformers model '{model_name}'.

Troubleshooting steps:
  1. pip install sentence-transformers --upgrade
  2. Ensure you have internet access for first-time model download
  3. Check disk space for model cache (~100MB)
  4. Try: pip install torch --upgrade"""
        _model_load_errors['sentence_transformer'] = error_msg
        log_error(e, context='load_sentence_transformer', category=
            ErrorCategory.MODEL_LOADING)
        st.error(error_msg)
        raise ModelLoadError(message=
            f'Failed to load Sentence-Transformers model: {str(e)}',
            model_name=model_name, user_message=
            'The embedding model could not be loaded. Please check the troubleshooting steps.'
            , original_error=e)


@st.cache_resource(show_spinner=False)
def load_language_tool(language: str='en-US'):
    import time
    start_time = time.time()
    try:
        tool = language_tool_python.LanguageTool(language)
        _model_load_times['language_tool'] = time.time() - start_time
        log_info(
            f"LanguageTool for '{language}' loaded in {_model_load_times['language_tool']:.2f}s"
            , context='model_loader')
        return tool
    except Exception as e:
        error_msg = f"""Failed to load LanguageTool for '{language}'.

Troubleshooting steps:
  1. pip install language-tool-python --upgrade
  2. Ensure Java is installed (required by LanguageTool)
  3. Check if port 8081 is available
  4. Try restarting the application"""
        _model_load_errors['language_tool'] = error_msg
        log_error(e, context='load_language_tool', category=ErrorCategory.
            MODEL_LOADING)
        st.error(error_msg)
        raise ModelLoadError(message=
            f'Failed to load LanguageTool: {str(e)}', model_name=
            'LanguageTool', user_message=
            'The grammar checking tool could not be loaded. Please check the troubleshooting steps.'
            , original_error=e)


@st.cache_data(show_spinner=False)
def ensure_nltk_data():
    required_packages = [('punkt', 'tokenizers/punkt'), ('stopwords',
        'corpora/stopwords'), ('averaged_perceptron_tagger',
        'taggers/averaged_perceptron_tagger'), ('wordnet', 'corpora/wordnet')]
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


def initialize_all_models(show_progress: bool=True):
    if show_progress:
        with st.spinner(
            'Loading AI models... This may take a moment on first run.'):
            return _load_all_models()
    else:
        return _load_all_models()


def _load_all_models() ->Dict[str, Any]:
    ensure_nltk_data()
    models = {'nlp': load_spacy_model(), 'embedder':
        load_sentence_transformer(), 'grammar_tool': load_language_tool()}
    return models


def get_models() ->Dict[str, Any]:
    if 'models_initialized' not in st.session_state:
        st.session_state.models = initialize_all_models()
        st.session_state.models_initialized = True
    return st.session_state.models


def get_model_load_times() ->Dict[str, float]:
    return _model_load_times.copy()


def preload_models_async():
    try:
        load_spacy_model()
        load_sentence_transformer()
    except Exception:
        pass


def is_model_loaded(model_name: str) ->bool:
    return model_name in _model_load_times


def get_model_status() ->Dict[str, Any]:
    return {'spacy': {'loaded': 'spacy' in _model_load_times, 'load_time':
        _model_load_times.get('spacy', None), 'error': _model_load_errors.
        get('spacy', None)}, 'sentence_transformer': {'loaded': 
        'sentence_transformer' in _model_load_times, 'load_time':
        _model_load_times.get('sentence_transformer', None), 'error':
        _model_load_errors.get('sentence_transformer', None)},
        'language_tool': {'loaded': 'language_tool' in _model_load_times,
        'load_time': _model_load_times.get('language_tool', None), 'error':
        _model_load_errors.get('language_tool', None)}}


def get_model_load_errors() ->Dict[str, str]:
    return _model_load_errors.copy()


def clear_model_errors() ->None:
    _model_load_errors.clear()

