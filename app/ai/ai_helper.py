"""
Model Loader Module
Handles initialization and caching of all AI models used in the application.

📚 TEACHING NOTE — Why a dedicated module for loading models?
    AI models (spaCy, SentenceTransformer, LanguageTool) are large and slow to load.
    Putting all loading logic in ONE place means:
    - Easy to update (change the model name in one place, not 10)
    - Consistent error handling and fallback across the whole app
    - Centralized caching — no model gets accidentally loaded twice
    
    This pattern is sometimes called a "Service Locator" or "Model Registry".

This module provides:
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
from app.utils.errors import ModelLoadError, ErrorCategory, log_error, log_warning, log_info

# ============================================================
# 📚 TEACHING NOTE — Module-level variables (global state)
# These two dictionaries are defined at the top of the file (module level),
# meaning they exist for the entire lifetime of the app.
# _model_load_times tracks HOW LONG each model took to load (for performance monitoring).
# _model_load_errors stores any error messages if a model fails (for debugging).
# The underscore prefix (_) is a Python convention meaning "intended for internal use only".
# ============================================================
_model_load_times: Dict[str, float] = {}   # e.g., {'spacy': 1.34, 'sentence_transformer': 2.1}
_model_load_errors: Dict[str, str] = {}    # e.g., {'spacy': 'Model not found. Run: python -m spacy download...'}


# ============================================================
# 📚 TEACHING NOTE — @st.cache_resource
# This decorator is KEY to performance. Without it, every Streamlit
# interaction (button click, slider move) would reload the entire model.
# With it, the model is loaded ONCE and reused for all users, all sessions.
#
# show_spinner=False — we manage our own loading messages (spinner)
# rather than showing Streamlit's default "Running..." spinner.
# ============================================================
@st.cache_resource(show_spinner=False)
def load_spacy_model(model_name: str='en_core_web_md'):
    """
    Load the spaCy NLP model with automatic fallback to a smaller model.
    
    📚 TEACHING NOTE — What does spaCy do?
        spaCy is a Natural Language Processing (NLP) library.
        It can: tokenize text, find named entities (person, org, location),
        identify parts of speech (noun, verb), and much more.
        
        'en_core_web_md' = English, trained on web data, medium size (~43MB)
        'en_core_web_sm' = English, small size (~12MB) — less accurate but lighter
        
    Fallback strategy:
        Try the preferred model first → if not installed, try the smaller one
        → if that also fails, show a helpful error with install commands.
    """
    import time
    start_time = time.time()
    
    try:
        nlp = spacy.load(model_name)
        # Record how long it took — useful for performance monitoring
        _model_load_times['spacy'] = time.time() - start_time
        log_info(
            f"spaCy model '{model_name}' loaded in {_model_load_times['spacy']:.2f}s",
            context='model_loader')
        return nlp
    
    except OSError as primary_error:
        # OSError means the model file wasn't found on disk
        log_warning(
            f"Primary spaCy model '{model_name}' not found, trying fallback",
            context='model_loader')
        
        try:
            # Fallback: try the smaller 'sm' model instead of 'md'
            nlp = spacy.load('en_core_web_sm')
            _model_load_times['spacy'] = time.time() - start_time
            log_info(
                f"spaCy fallback model 'en_core_web_sm' loaded in {_model_load_times['spacy']:.2f}s",
                context='model_loader')
            return nlp
        
        except OSError as fallback_error:
            # Both models failed — tell the user exactly how to fix it
            error_msg = f"""spaCy model not found. Please run one of the following commands:
                python -m spacy download {model_name}
                python -m spacy download en_core_web_sm

                If the issue persists, try:
                pip install spacy --upgrade
                pip install {model_name}"""
            
            _model_load_errors['spacy'] = error_msg  # Save for get_model_status()
            log_error(fallback_error, context='load_spacy_model', category=ErrorCategory.MODEL_LOADING)
            st.error(error_msg)
            
            # Raise a custom error type — better than a generic exception
            # because callers can specifically catch ModelLoadError
            raise ModelLoadError(
                message=f'Failed to load spaCy model: {str(fallback_error)}',
                model_name=model_name,
                user_message='The language processing model could not be loaded. Please check the troubleshooting steps.',
                original_error=fallback_error
            )


@st.cache_resource(show_spinner=False)
def load_sentence_transformer(model_name: str='all-MiniLM-L6-v2'):
    """
    Load the SentenceTransformer model for semantic similarity calculation.
    
    📚 TEACHING NOTE — What is SentenceTransformer?
        It converts text into a list of numbers called a "vector" or "embedding".
        Similar sentences get similar vectors.
        This lets us mathematically compare "Python developer" and
        "built apps using Python" — without exact word matching!
        
        'all-MiniLM-L6-v2' is a popular lightweight model:
        - Fast to run
        - ~80MB download (only on first use)
        - Good accuracy for skill matching use case
        
    📚 TEACHING NOTE — First-time vs cached runs:
        First time: downloads model from internet (~80MB) → slow
        Every run after: loads from local disk cache → fast
        That's why the error message says "Ensure you have internet access for first-time download"
    """
    import time
    start_time = time.time()
    
    try:
        embedder = SentenceTransformer(model_name)
        _model_load_times['sentence_transformer'] = time.time() - start_time
        log_info(
            f"Sentence-Transformers model '{model_name}' loaded in {_model_load_times['sentence_transformer']:.2f}s",
            context='model_loader')
        return embedder
    
    except Exception as e:
        # More general 'Exception' here because SentenceTransformer can fail
        # for many reasons: network issues, disk space, PyTorch problems, etc.
        error_msg = f"""Failed to load Sentence-Transformers model '{model_name}'.

Troubleshooting steps:
  1. pip install sentence-transformers --upgrade
  2. Ensure you have internet access for first-time model download
  3. Check disk space for model cache (~100MB)
  4. Try: pip install torch --upgrade"""
        
        _model_load_errors['sentence_transformer'] = error_msg
        log_error(e, context='load_sentence_transformer', category=ErrorCategory.MODEL_LOADING)
        st.error(error_msg)
        raise ModelLoadError(
            message=f'Failed to load Sentence-Transformers model: {str(e)}',
            model_name=model_name,
            user_message='The embedding model could not be loaded. Please check the troubleshooting steps.',
            original_error=e
        )


@st.cache_resource(show_spinner=False)
def load_language_tool(language: str='en-US'):
    """
    Load the LanguageTool grammar checker.
    
    📚 TEACHING NOTE — LanguageTool is Java-based!
        Unlike spaCy and SentenceTransformer (pure Python),
        LanguageTool is a Java application that the Python library wraps.
        This means:
        1. Java must be installed on the machine (requirement)
        2. It starts a small local server on port 8081
        3. Python communicates with it via HTTP requests
        
        That's why the error message mentions Java and port 8081.
        This is an example of a "language bridge" — Python calling Java code.
    """
    import time
    start_time = time.time()
    
    try:
        tool = language_tool_python.LanguageTool(language)
        _model_load_times['language_tool'] = time.time() - start_time
        log_info(
            f"LanguageTool for '{language}' loaded in {_model_load_times['language_tool']:.2f}s",
            context='model_loader')
        return tool
    
    except Exception as e:
        error_msg = f"""Failed to load LanguageTool for '{language}'.

        Troubleshooting steps:
        1. pip install language-tool-python --upgrade
        2. Ensure Java is installed (required by LanguageTool)
        3. Check if port 8081 is available
  4. Try restarting the application"""
        
        _model_load_errors['language_tool'] = error_msg
        log_error(e, context='load_language_tool', category=ErrorCategory.MODEL_LOADING)
        st.error(error_msg)
        raise ModelLoadError(
            message=f'Failed to load LanguageTool: {str(e)}',
            model_name='LanguageTool',
            user_message='The grammar checking tool could not be loaded. Please check the troubleshooting steps.',
            original_error=e
        )


# ============================================================
# 📚 TEACHING NOTE — @st.cache_data vs @st.cache_resource
# We use @st.cache_data here (not @st.cache_resource) because
# this function returns a simple boolean, not a large object/model.
# @st.cache_data is for lightweight data values.
# @st.cache_resource is for heavyweight objects like ML models.
# ============================================================
@st.cache_data(show_spinner=False)
def ensure_nltk_data():
    """
    Download required NLTK datasets if they're not already available.
    
    📚 TEACHING NOTE — What is NLTK?
        NLTK (Natural Language Toolkit) is another NLP library.
        Unlike spaCy which comes as one download, NLTK has many small
        separate datasets you download on demand.
        
        We need:
        - punkt: for splitting text into sentences/words (tokenization)
        - stopwords: common words like "the", "is", "at" (often filtered out)
        - averaged_perceptron_tagger: tags words as noun/verb/adjective etc.
        - wordnet: a dictionary of word relationships (synonyms, meanings)
        
    This function silently downloads anything missing → no user action needed.
    """
    required_packages = [
        ('punkt',                       'tokenizers/punkt'),                  # Sentence tokenizer
        ('stopwords',                   'corpora/stopwords'),                 # Common words to ignore
        ('averaged_perceptron_tagger',  'taggers/averaged_perceptron_tagger'), # Part-of-speech tagger
        ('wordnet',                     'corpora/wordnet')                    # Word meaning database
    ]
    
    all_available = True
    for package, path in required_packages:
        try:
            nltk.data.find(path)  # Check if already downloaded
        except LookupError:
            # Not found locally — download it quietly (quiet=True suppresses output)
            try:
                nltk.download(package, quiet=True)
            except Exception as e:
                all_available = False  # Mark that at least one package failed
    
    return all_available  # True if everything is ready, False if something failed


def initialize_all_models(show_progress: bool=True):
    """
    Load all three AI models together, optionally showing a loading spinner.
    
    📚 TEACHING NOTE — User Experience (UX) consideration:
        Loading models takes 5-15 seconds on first run.
        Without a spinner, the user thinks the app is frozen.
        show_progress=True shows "Loading AI models..." message → better UX.
        
        This is a simple but important lesson: always give feedback
        to users when the app is doing something slow.
    """
    if show_progress:
        with st.spinner('Loading AI models... This may take a moment on first run.'):
            return _load_all_models()
    else:
        return _load_all_models()  # No UI feedback — useful for background/test loading


def _load_all_models() -> Dict[str, Any]:
    """
    Internal function that actually loads all models and returns them as a dictionary.
    
    📚 TEACHING NOTE — Why return a dictionary?
        Returning {'nlp': ..., 'embedder': ..., 'grammar_tool': ...}
        lets callers access models by name: models['nlp']
        This is more readable and flexible than returning a tuple
        where you'd need to remember: models[0], models[1], models[2]
    """
    # First ensure NLTK data is available before loading other models
    ensure_nltk_data()
    
    # Load all three models — each is cached separately
    models = {
        'nlp':          load_spacy_model(),           # For NLP parsing
        'embedder':     load_sentence_transformer(),  # For semantic similarity
        'grammar_tool': load_language_tool()          # For grammar checking
    }
    return models


def get_models() -> Dict[str, Any]:
    """
    Get all models, loading them on first call and caching in session state.
    
    📚 TEACHING NOTE — st.session_state (Streamlit-specific concept):
        In Streamlit, every user interaction reruns the script from top to bottom.
        session_state is like a "memory" that persists between these reruns.
        
        'models_initialized' flag acts as a guard:
        - First call: flag doesn't exist → load models → set flag = True
        - Every subsequent call: flag exists → just return cached models
        
        Without this guard, we'd call initialize_all_models() on EVERY click!
    """
    if 'models_initialized' not in st.session_state:
        # First time this user's session touches models — load them all
        st.session_state.models = initialize_all_models()
        st.session_state.models_initialized = True  # Set the guard flag
    
    return st.session_state.models  # Return from session memory


def get_model_load_times() -> Dict[str, float]:
    """
    Return a copy of the model load times dictionary (for monitoring/debugging).
    
    📚 TEACHING NOTE — Why return a .copy()?
        Returning the original dictionary would let callers accidentally modify it.
        _model_load_times['spacy'] = 999  ← this would corrupt our data!
        Returning a copy protects the internal state.
        This is the principle of "defensive copying" or "encapsulation".
    """
    return _model_load_times.copy()


def preload_models_async():
    """
    Attempt to preload models in the background.
    
    📚 TEACHING NOTE — ⚠️ Known Issue / Improvement Needed:
        Despite the name, this function is NOT truly async (asynchronous).
        It runs synchronously — meaning it blocks until models are loaded.
        
        A real async implementation would use Python's asyncio or threading:
            import threading
            thread = threading.Thread(target=load_spacy_model)
            thread.start()
        
        This is a good example to discuss with students: naming a function
        "async" doesn't make it async — the implementation must actually be
        non-blocking. This would be a bug if called expecting async behavior.
    """
    try:
        load_spacy_model()
        load_sentence_transformer()
    except Exception:
        pass  # Silently ignore errors — this is a "best effort" preload


def is_model_loaded(model_name: str) -> bool:
    """
    Check if a specific model has been successfully loaded.
    
    📚 TEACHING NOTE:
        We use _model_load_times as our "registry" of loaded models.
        If a model loaded successfully, its name is in _model_load_times.
        If it failed (or hasn't been loaded yet), it won't be in the dict.
        This is a clever way to track state without a separate boolean flag.
    """
    return model_name in _model_load_times


def get_model_status() -> Dict[str, Any]:
    """
    Return a full status report for all models — useful for a health check page.
    
    📚 TEACHING NOTE — Health Check / Monitoring pattern:
        In production apps, you often have a "status" or "health" endpoint
        that tells you: "Is the system working? What's loaded? Any errors?"
        This function serves that purpose for the AI models.
        
        The .get() method safely reads from a dictionary:
        dict.get('key', default) → returns default if key doesn't exist
        (avoids KeyError exceptions)
    """
    return {
        'spacy': {
            'loaded':    'spacy' in _model_load_times,            # True/False
            'load_time': _model_load_times.get('spacy', None),    # Seconds, or None if not loaded
            'error':     _model_load_errors.get('spacy', None)    # Error message, or None if OK
        },
        'sentence_transformer': {
            'loaded':    'sentence_transformer' in _model_load_times,
            'load_time': _model_load_times.get('sentence_transformer', None),
            'error':     _model_load_errors.get('sentence_transformer', None)
        },
        'language_tool': {
            'loaded':    'language_tool' in _model_load_times,
            'load_time': _model_load_times.get('language_tool', None),
            'error':     _model_load_errors.get('language_tool', None)
        }
    }


def get_model_load_errors() -> Dict[str, str]:
    """Return a copy of any model loading errors (for debugging/display)."""
    return _model_load_errors.copy()  # Copy to protect internal state


def clear_model_errors() -> None:
    """
    Clear all recorded model errors — useful for retry attempts.
    
    📚 TEACHING NOTE:
        .clear() empties the dictionary in-place (without creating a new one).
        This is different from: _model_load_errors = {}
        (which creates a new dictionary and breaks the reference)
        
        Use case: If a model failed to load, the user fixes the issue,
        and clicks "Retry" — we clear old errors and try again.
    """
    _model_load_errors.clear()