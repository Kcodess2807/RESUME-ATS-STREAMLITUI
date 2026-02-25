"""
Cache Manager Module for ATS Resume Scorer

📌 TEACHING NOTE — Why a dedicated Cache Manager?
    Caching is done in many places across the app (grammar check, skill validation,
    JD comparison, text processing...). Without a central manager, each feature
    would implement its own caching — inconsistently and with duplicated logic.
    
    This module provides ONE place for all caching decisions:
    - How to generate cache keys (content hashing)
    - How to store/retrieve results from session state
    - How to limit cache size (prevent memory issues)
    - Lazy loading of heavy AI models

    Think of this as the app's "memory management department."
    
    Two types of caching used here:
    1. @st.cache_data    → Streamlit manages it (tied to function inputs)
    2. session_state     → We manage it manually (tied to user's session)
"""

import streamlit as st
import hashlib
from typing import Dict, Any, Optional, Callable
from functools import wraps
import time


def generate_content_hash(content: str) -> str:
    """
    Generate a unique fingerprint (hash) for any text content.
    
    📌 TEACHING NOTE — What is Hashing?
        A hash function converts any input into a fixed-length string.
        Properties of a good hash (like SHA-256):
        
        1. Same input   → Always same output
           "Hello"      → "185f8db32..."  (always)
        
        2. Different input → Different output (almost certainly)
           "Hello"      → "185f8db32..."
           "Hello!"     → "334d016f75..."  (completely different!)
        
        3. One-way: you can't reverse "185f8db32..." back to "Hello"
        
        Why SHA-256 instead of Python's built-in hash()?
        - hash() changes every program run (for security reasons)
        - SHA-256 is stable — same input gives same hash across runs,
          servers, and time. Critical for reliable cache keys.
    
    📌 Real-world use: This is how Git tracks file changes —
        each commit is a SHA hash of the code.
    
    Args:
        content: Any text string
        
    Returns:
        64-character hexadecimal SHA-256 hash string
    """
    # .encode('utf-8') converts string to bytes (hashlib works on bytes)
    # .hexdigest() returns hash as readable hex string (not binary)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def get_cache_key(resume_text: str, jd_text: Optional[str] = None) -> str:
    """
    Generate a unique cache key for a specific resume analysis.
    
    📌 TEACHING NOTE — Composite Cache Keys:
        When results depend on MULTIPLE inputs, the cache key must
        include ALL of them. If we only hashed the resume:
        
        Resume A + Job Description 1 → same key as Resume A + Job Description 2 ❌
        
        By combining both hashes with "_", we get a unique key for
        each unique (resume, job_description) combination.
        
        Example:
        resume_hash = "abc123..."
        jd_hash     = "def456..."
        cache_key   = "abc123..._def456..."
        
        This means:
        - Same resume, different JD    → different cache key (correct!)
        - Different resume, same JD    → different cache key (correct!)
        - Same resume, no JD           → just the resume hash (correct!)
    
    Args:
        resume_text: Full resume text content
        jd_text: Optional job description text
        
    Returns:
        Cache key string (either resume hash or resume_jd combined hash)
    """
    resume_hash = generate_content_hash(resume_text)
    
    if jd_text:
        # Analysis with JD → key includes both
        jd_hash = generate_content_hash(jd_text)
        return f"{resume_hash}_{jd_hash}"
    
    # Analysis without JD → key is just resume hash
    return resume_hash


# ============================================================
# 📌 TEACHING NOTE — The Underscore (_nlp, _embedder, _grammar_tool) Convention
#
#   @st.cache_data caches based on function arguments.
#   But it can ONLY hash simple types: strings, numbers, tuples, etc.
#   It CANNOT hash complex Python objects like AI models.
#
#   Solution: prefix the argument name with _ (underscore).
#   Streamlit sees _ and says "skip this one when building the cache key."
#
#   So the cache key for cached_text_processing() is built from:
#       text_hash + text    (both are strings → hashable ✅)
#   NOT from _nlp           (a complex object → skipped ✅)
#
#   This pattern appears in ALL the cached functions below.
# ============================================================


@st.cache_data(ttl=3600, show_spinner=False)
def cached_text_processing(text_hash: str, text: str, _nlp) -> Dict[str, Any]:
    """
    Cache the result of processing resume text through spaCy.
    
    📌 TEACHING NOTE — Why cache text processing?
        spaCy processes text by running it through a neural network pipeline
        (tokenizer → tagger → parser → NER). This takes ~0.5-2 seconds.
        
        If a user submits the same resume twice (e.g., on page refresh),
        we shouldn't make them wait again. The cache key is text_hash —
        if the text is identical, we return the stored result instantly.
        
        ttl=3600 means "forget this cache entry after 1 hour."
        Why? To prevent stale data if the processing logic changes.
    
    Args:
        text_hash: SHA-256 hash of resume text (used as cache key)
        text: Actual resume text to process
        _nlp: spaCy model (excluded from cache key — prefixed with _)
        
    Returns:
        Processed text data dict (tokens, entities, keywords, etc.)
    """
    from app.core.processor import process_resume_text
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
    
    📌 TEACHING NOTE — Why tuple instead of list?
        Python lists are NOT hashable (they're mutable — you can change them).
        Python tuples ARE hashable (they're immutable — can't be changed).
        
        @st.cache_data needs hashable arguments to build the cache key.
        So we convert skills list → tuple before passing here.
        
        Example:
        ["Python", "React"]  → cannot be hashed ❌
        ("Python", "React")  → can be hashed ✅
    
    📌 TEACHING NOTE — ⚠️ Incomplete Implementation:
        This function currently just has `pass` — it does nothing and returns None.
        The actual caching for skill validation is handled differently in validator.py.
        
        This is dead code — either it should be completed or deleted.
        Leaving incomplete stubs like this is a common issue in growing codebases.
    
    Args:
        skills_tuple: Skills as a tuple (not list) for hashability
        projects_hash: SHA-256 hash of projects data
        experience_hash: SHA-256 hash of experience text
        _embedder: SentenceTransformer model (excluded from cache key)
        threshold: Similarity threshold (0.0 to 1.0)
    """
    # ⚠️ TODO: This is a stub — not implemented yet
    # Should call _compute_skill_validation() and return results
    pass


@st.cache_data(ttl=3600, show_spinner=False)
def cached_grammar_check(text_hash: str, text: str, _grammar_tool) -> Dict[str, Any]:
    """
    Cache grammar check results for identical resume text.
    
    📌 TEACHING NOTE — Why is grammar checking expensive?
        LanguageTool runs a local Java server that applies hundreds of
        grammar rules to each sentence. For a 500-word resume, this
        might check 3,000+ rule combinations.
        
        With caching: first check takes ~2 seconds, subsequent checks = instant.
        Without caching: every button click = another 2-second wait.
    
    Args:
        text_hash: Hash of text (cache key)
        text: Full text to grammar-check
        _grammar_tool: LanguageTool instance (excluded from cache key)
        
    Returns:
        Dict with critical_errors, moderate_errors, minor_errors, grammar_score
    """
    from app.ai.grammar import check_grammar_and_spelling
    return check_grammar_and_spelling(text, _grammar_tool)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_location_detection(text_hash: str, text: str, _nlp) -> Dict[str, Any]:
    """
    Cache location detection results for identical text.
    
    📌 TEACHING NOTE — What is location detection for a resume?
        The app checks whether the resume includes a location (city, country).
        ATS systems often filter candidates by location, so having a
        location on a resume matters for scoring.
        
        spaCy's Named Entity Recognition (NER) can find location mentions:
        "Bangalore, India" → entity type: GPE (Geopolitical Entity)
    
    Args:
        text_hash: Hash of text (cache key)
        text: Resume text to analyze
        _nlp: spaCy model (excluded from cache key)
        
    Returns:
        Dict with detected location info
    """
    from app.core.detector import detect_location_info
    return detect_location_info(text, _nlp)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_jd_comparison(
    resume_hash: str,
    jd_hash: str,
    resume_text: str,
    resume_keywords: tuple,   # tuple (not list) — must be hashable
    resume_skills: tuple,     # tuple (not list) — must be hashable
    jd_text: str,
    jd_keywords: tuple,       # tuple (not list) — must be hashable
    _embedder,                # excluded from cache key (not hashable)
    _nlp                      # excluded from cache key (not hashable)
) -> Dict[str, Any]:
    """
    Cache the result of comparing a resume against a job description.
    
    📌 TEACHING NOTE — This is the most expensive operation in the app.
        JD comparison involves:
        1. Keyword matching (which keywords from JD appear in resume?)
        2. Semantic similarity (using SentenceTransformer — AI-powered)
        3. Skill gap analysis (what skills does the JD want that are missing?)
        
        Caching this is essential — without it, every analysis takes 5-15 seconds.
        With caching: same (resume + JD) combination = instant results.
        
        The cache key is resume_hash + jd_hash (passed as separate args
        so Streamlit can hash them individually as strings).
    
    📌 TEACHING NOTE — list() conversion before passing to comparator:
        We receive tuples (for hashability), but the underlying function
        expects lists. So we convert back: list(resume_keywords).
        
        tuple → function call → list → internal processing
        This conversion dance is necessary because of Streamlit's caching limitations.
    
    Args:
        resume_hash: Hash of resume text (part of cache key)
        jd_hash: Hash of JD text (part of cache key)
        resume_text: Full resume content
        resume_keywords: Resume keywords as tuple
        resume_skills: Resume skills as tuple
        jd_text: Full job description content
        jd_keywords: JD keywords as tuple
        _embedder: SentenceTransformer (excluded from key)
        _nlp: spaCy model (excluded from key)
        
    Returns:
        Dict with match_percentage, matched_keywords, missing_keywords, suggestions
    """
    from app.core.comparator import compare_resume_with_jd
    return compare_resume_with_jd(
        resume_text=resume_text,
        resume_keywords=list(resume_keywords),  # Convert back from tuple to list
        resume_skills=list(resume_skills),
        jd_text=jd_text,
        jd_keywords=list(jd_keywords),
        embedder=_embedder,
        nlp=_nlp
    )


def get_cached_analysis_results(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Look up previously computed full analysis results from session state.
    
    📌 TEACHING NOTE — Two-level caching architecture:
        This app uses TWO layers of caching:
        
        Layer 1: @st.cache_data (above)
            → Caches individual operations (grammar, JD comparison, etc.)
            → Managed by Streamlit automatically
            → Shared across all users on the same server instance
        
        Layer 2: st.session_state (this function + store_analysis_results)
            → Caches the COMPLETE analysis result for a user
            → Managed by us manually
            → Private to each user's browser session
        
        Layer 2 is useful when the user navigates between pages —
        we don't want to re-run the full analysis just because they
        visited the History page and came back.
    
    Args:
        cache_key: Hash-based key from get_cache_key()
        
    Returns:
        Cached full analysis results dict, or None if not found
    """
    # Initialize the cache dict if it doesn't exist yet
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    
    # .get() returns None (not KeyError) if key doesn't exist
    return st.session_state.analysis_cache.get(cache_key)


def store_analysis_results(cache_key: str, results: Dict[str, Any]) -> None:
    """
    Save a complete analysis result to session state for quick retrieval.
    
    📌 TEACHING NOTE — Cache Size Management (Memory Safety):
        We limit the cache to 10 entries (MAX_CACHE_SIZE = 10).
        
        Why? Each full analysis result can be quite large (nested dicts
        with scores, errors, keywords, suggestions...). If we stored
        hundreds of these in memory, the browser tab could crash.
        
        Eviction policy: When cache is full, delete the OLDEST entry.
        This is a simple FIFO (First In, First Out) strategy.
        
        More sophisticated apps use LRU (Least Recently Used) — evicting
        the entry that was accessed LEAST recently, not just the oldest.
        LRU is better but more complex to implement.
    
    📌 TEACHING NOTE — Storing timestamp with results:
        We store the current time alongside results. This lets us:
        - Show the user "analyzed 5 minutes ago"
        - Build a proper LRU cache in the future (sort by last access time)
        - Debug stale cache issues
    
    Args:
        cache_key: Hash-based key to store under
        results: Full analysis results dict to cache
    """
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    
    # ── Enforce size limit before adding new entry ───────────────────────
    MAX_CACHE_SIZE = 10
    if len(st.session_state.analysis_cache) >= MAX_CACHE_SIZE:
        # next(iter(dict)) gets the FIRST key (oldest, since Python 3.7+
        # dicts maintain insertion order)
        oldest_key = next(iter(st.session_state.analysis_cache))
        del st.session_state.analysis_cache[oldest_key]
    
    # Store results with a timestamp for future use / debugging
    st.session_state.analysis_cache[cache_key] = {
        'results': results,
        'timestamp': time.time()  # Unix timestamp (seconds since 1970-01-01)
    }


def clear_analysis_cache() -> None:
    """
    Wipe all cached analysis results from the user's session.
    
    📌 TEACHING NOTE — When would you call this?
        - User uploads a new resume (old cache no longer relevant)
        - Debug button "Clear Cache" for developers
        - Memory is getting full
        
        Setting it to {} (empty dict) is faster than deleting entries one by one.
    """
    if 'analysis_cache' in st.session_state:
        st.session_state.analysis_cache = {}


def get_cache_stats() -> Dict[str, Any]:
    """
    Return a summary of current cache usage for monitoring/debugging.
    
    📌 TEACHING NOTE — Observability:
        In production apps, you need ways to understand what's happening
        inside the system. This function provides a "window" into the cache.
        
        Could be displayed on an admin dashboard:
        "Cache has 3 entries. Oldest from 2 minutes ago."
        
        The min() with a generator expression finds the smallest timestamp
        (= oldest entry) efficiently without building a list first.
        
        min((x for x in values), default=None) → None if no values exist
    
    Returns:
        Dict with count, key preview, and timestamp of oldest entry
    """
    cache = st.session_state.get('analysis_cache', {})
    
    return {
        'cached_analyses': len(cache),
        'cache_keys': list(cache.keys())[:5],  # Show only first 5 keys (preview)
        'oldest_entry': min(
            (entry['timestamp'] for entry in cache.values()),
            default=None  # Returns None instead of crashing if cache is empty
        ) if cache else None
    }


# ============================================================
# 📌 TEACHING NOTE — Lazy Loading Pattern
#
#   "Lazy loading" means: don't load a resource until it's actually needed.
#   Opposite of "eager loading" which loads everything at startup.
#
#   Why lazy loading?
#   - Faster app startup (don't load LanguageTool if user never checks grammar)
#   - Less memory used (models only load if that feature is used)
#   - Better for optional features
#
#   The LazyLoader class below implements this pattern using a dictionary
#   (_loaded) to track what's already been loaded. This is essentially
#   a manual cache for expensive objects.
#
#   The pattern for each loader method:
#       if not already loaded:
#           load it now, store it
#       return the stored version
# ============================================================

class LazyLoader:
    """
    Delays loading of expensive AI models until they are actually needed.
    
    📌 TEACHING NOTE — This is the "Lazy Initialization" design pattern.
        Instead of loading all three models at app startup, each model
        is loaded only when first requested. If a user never uses grammar
        checking, the LanguageTool Java server is never started.
    
    Usage:
        loader = get_lazy_loader()
        grammar = loader.get_grammar_checker()  # Loads only if not loaded yet
        embedder = loader.get_embedder()        # Loads only if not loaded yet
    """
    
    def __init__(self):
        # Dictionary to store already-loaded resources
        # Key = resource name, Value = loaded object
        self._loaded = {}
    
    def get_grammar_checker(self):
        """
        Load LanguageTool only when first called.
        Subsequent calls return the already-loaded instance instantly.
        """
        if 'grammar_checker' not in self._loaded:
            # First call — actually load it (slow, ~5 seconds)
            from app.ai.grammar import load_grammar_checker
            self._loaded['grammar_checker'] = load_grammar_checker()
        # All subsequent calls — return already-loaded instance (instant)
        return self._loaded['grammar_checker']
    
    def get_embedder(self):
        """Load SentenceTransformer model lazily."""
        if 'embedder' not in self._loaded:
            from app.ai.validator_utils import load_embedder
            self._loaded['embedder'] = load_embedder()
        return self._loaded['embedder']
    
    def get_spacy_model(self):
        """Load spaCy NLP model lazily."""
        if 'nlp' not in self._loaded:
            from app.core.processor import load_spacy_model
            self._loaded['nlp'] = load_spacy_model()
        return self._loaded['nlp']
    
    def is_loaded(self, resource_name: str) -> bool:
        """
        Check if a specific resource has already been loaded.
        Useful for displaying loading status in the UI.
        """
        return resource_name in self._loaded
    
    def get_loaded_resources(self) -> list:
        """Return names of all currently loaded resources (for debugging/status display)."""
        return list(self._loaded.keys())


# ============================================================
# 📌 TEACHING NOTE — Singleton Pattern
#
#   We only want ONE LazyLoader instance for the entire app.
#   Creating multiple instances would defeat the purpose —
#   each instance has its own _loaded dict, so models could load multiple times.
#
#   The Singleton Pattern ensures only one instance exists:
#       _lazy_loader = None   (module-level variable, starts as None)
#       
#       def get_lazy_loader():
#           global _lazy_loader
#           if _lazy_loader is None:
#               _lazy_loader = LazyLoader()   # Create ONCE
#           return _lazy_loader               # Always return same instance
#
#   After first call, _lazy_loader is set and the if-check is skipped.
#   Every caller gets the same object back.
# ============================================================

# Module-level holder for the single LazyLoader instance
_lazy_loader = None


def get_lazy_loader() -> LazyLoader:
    """
    Get (or create) the single global LazyLoader instance.
    
    📌 TEACHING NOTE — global keyword:
        Normally, assigning to a variable inside a function creates a
        LOCAL variable. The 'global' keyword tells Python:
        "I want to modify the MODULE-LEVEL _lazy_loader, not create a local one."
        
        Without 'global _lazy_loader', the assignment would create a new
        local variable that disappears when the function exits —
        and _lazy_loader would always remain None.
    
    Returns:
        The single shared LazyLoader instance
    """
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = LazyLoader()  # Created once, reused forever
    return _lazy_loader