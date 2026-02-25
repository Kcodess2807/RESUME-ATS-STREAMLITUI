"""
Database Module for ATS Resume Scorer

Handles persistent storage of resume analysis history using Supabase (PostgreSQL).
Falls back to in-memory session state if Supabase is not configured.

📌 TEACHING NOTE — What does this module do?
    Every time a user analyzes a resume, we want to SAVE the results so they
    can look at their history later. This module handles:
    - Connecting to the database (Supabase)
    - Saving analysis results
    - Fetching history for a user
    - Deleting entries
    
    📌 Key design decision — Dual storage strategy:
    ┌─────────────────────────────────────────────────────────┐
    │  Supabase configured?  YES → save to PostgreSQL database │
    │                         NO → save to session state (RAM) │
    └─────────────────────────────────────────────────────────┘
    
    This means the app works even without a database — perfect for
    local development or demo purposes. When deployed to production,
    Supabase credentials are added and history becomes persistent.

📌 TEACHING NOTE — What is Supabase?
    Supabase is an open-source Firebase alternative — it gives you a
    PostgreSQL database with a REST API on top. Instead of writing SQL
    queries directly, you use their Python client library:
    
        client.table('analysis_history').insert(data).execute()
    
    This is called an ORM-style API (Object Relational Mapping).
    The underlying data is still stored in PostgreSQL tables.
"""

import streamlit as st
from datetime import datetime
import json
import os
from typing import Optional, List, Dict, Any

# ============================================================
# 📌 TEACHING NOTE — Optional Imports at Module Level
#   Both supabase and dotenv are optional dependencies.
#   If not installed, the app degrades gracefully:
#   - No supabase → use session state instead
#   - No dotenv   → use system environment variables or st.secrets
#
#   This is the same "optional import" pattern used in auth.py.
#   Setting a flag variable (SUPABASE_AVAILABLE) lets the rest of
#   the code check availability without try/except everywhere.
# ============================================================

# Try to import Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False  # App will use session state as fallback

# Try to load .env file for local development
# In production (cloud), environment variables are set on the server
try:
    from dotenv import load_dotenv
    load_dotenv()  # Reads .env file and sets environment variables
except ImportError:
    pass  # No .env file support — use system env vars or st.secrets


def get_supabase_client() -> Optional[Any]:
    """
    Create and return a Supabase database client if credentials are available.
    
    📌 TEACHING NOTE — Two ways to provide credentials:
    
        1. Environment Variables (.env file or system):
               SUPABASE_URL=https://xxx.supabase.co
               SUPABASE_KEY=eyJhbGciOiJIUzI1N...
           os.getenv() reads these.
        
        2. Streamlit Secrets (st.secrets):
               In .streamlit/secrets.toml:
               [supabase]
               url = "https://xxx.supabase.co"
               key = "eyJhbGciOiJIUzI1N..."
           Used for Streamlit Cloud deployment.
        
        Priority: env vars first, then st.secrets.
        This lets local dev use .env and cloud deployment use st.secrets.
    
    📌 TEACHING NOTE — Why return Optional[Any] (can return None)?
        Not every deployment will have Supabase configured.
        Returning None signals "database not available" without crashing.
        Callers check: if not client: → use session state instead.
    
    Returns:
        Supabase Client object if configured, None otherwise
    """
    if not SUPABASE_AVAILABLE:
        return None  # supabase library not even installed
    
    try:
        # Method 1: Environment variables (preferred for local dev)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        # Method 2: Streamlit secrets (preferred for cloud deployment)
        if not url or not key:
            url = st.secrets.get("supabase", {}).get("url")
            key = st.secrets.get("supabase", {}).get("key")
        
        # Only create client if both URL and key are present
        if url and key:
            return create_client(url, key)
    except Exception as e:
        # Print to server logs (not shown to user)
        print(f"Supabase client creation error: {e}")
    
    return None  # Credentials missing or invalid


def get_user_id() -> str:
    """
    Determine a unique identifier for the current session.
    
    Since authentication is removed, we generate a stable session-scoped ID.
    
    Returns:
        String identifier for the current session
    """
    # Generate a stable session-scoped ID
    if 'session_id' not in st.session_state:
        import uuid
        # Generate unique session ID: "session_a1b2c3d4" (random 8 hex chars)
        st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
    return st.session_state.session_id


def save_analysis_to_db(results: dict, filename: str) -> bool:
    """
    Save a complete analysis result to the database (or session state as fallback).
    
    📌 TEACHING NOTE — Data Flattening for Database Storage:
        Our results dict is deeply nested:
        {
          'scores': {
            'overall_score': 82,
            'formatting_score': 75,
            ...
          },
          'jd_comparison': {
            'match_percentage': 68,
            ...
          }
        }
        
        Databases store flat rows (each column has one value).
        We "flatten" the nested dict by extracting individual scores
        into separate columns. This makes querying and sorting easy:
        
        SELECT * FROM analysis_history ORDER BY overall_score DESC
        
        If we stored the whole dict as JSON, we couldn't easily query
        individual scores without parsing JSON every time.
    
    📌 TEACHING NOTE — Fallback pattern:
        If the database call fails (network error, wrong credentials, etc.),
        we don't crash the app. Instead we fall back to session state.
        The user still gets their result saved — just not permanently.
    
    Args:
        results: Full analysis results dictionary
        filename: Name of the uploaded resume file
        
    Returns:
        True if saved successfully (either to DB or session), False if both fail
    """
    client = get_supabase_client()
    
    # No database → use session state immediately
    if not client:
        return save_analysis_to_session(results, filename)
    
    try:
        user_id = get_user_id()
        scores  = results.get('scores', {})
        jd_comp = results.get('jd_comparison')  # Can be None if no JD provided
        
        # Build the flat data row for the database table
        data = {
            'user_id':                user_id,
            'filename':               filename,
            'overall_score':          scores.get('overall_score', 0),
            'formatting_score':       scores.get('formatting_score', 0),
            'keywords_score':         scores.get('keywords_score', 0),
            'content_score':          scores.get('content_score', 0),
            'skill_validation_score': scores.get('skill_validation_score', 0),
            'ats_compatibility_score':scores.get('ats_compatibility_score', 0),
            # Conditional: jd_match_percentage is None if no job description was given
            'jd_match_percentage':    jd_comp.get('match_percentage') if jd_comp else None,
            'created_at':             datetime.now().isoformat(),  # "2024-01-15T14:30:00"
        }
        
        # Supabase ORM-style insert — equivalent to:
        # INSERT INTO analysis_history (...) VALUES (...)
        client.table('analysis_history').insert(data).execute()
        return True
        
    except Exception as e:
        print(f"Database save error: {e}")
        # Graceful fallback — at least save to session
        return save_analysis_to_session(results, filename)


def save_analysis_to_session(results: dict, filename: str) -> bool:
    """
    Save analysis results to session state (in-memory, non-persistent).
    
    📌 TEACHING NOTE — Session State as a Temporary Database:
        st.session_state is essentially a dictionary that lives in RAM
        for the duration of the user's browser session.
        
        Pros: No setup required, instant reads/writes, always available
        Cons: Lost when tab closes, not shared between devices, limited to ~50MB
        
        We cap history at 20 entries (.analysis_history[:20]) to prevent
        session state from growing unboundedly.
    
    📌 TEACHING NOTE — .insert(0, entry) vs .append(entry):
        .append(entry) adds to the END of the list (oldest → newest order)
        .insert(0, entry) adds to the START (newest → oldest order)
        
        We use insert(0) so the most recent analysis appears first in
        the history list — better UX for showing "latest results."
    
    Args:
        results: Analysis results dict
        filename: Resume filename
        
    Returns:
        Always True (session save can't fail)
    """
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    scores  = results.get('scores', {})
    jd_comp = results.get('jd_comparison')
    
    # Build history entry — slightly different format from DB (keeps component_scores nested)
    entry = {
        'filename':  filename,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),  # Human-readable format
        'overall_score': scores.get('overall_score', 0),
        'component_scores': {
            'formatting_score':        scores.get('formatting_score', 0),
            'keywords_score':          scores.get('keywords_score', 0),
            'content_score':           scores.get('content_score', 0),
            'skill_validation_score':  scores.get('skill_validation_score', 0),
            'ats_compatibility_score': scores.get('ats_compatibility_score', 0),
        },
        'jd_match': jd_comp.get('match_percentage') if jd_comp else None,
    }
    
    # Add new entry at the front (most recent first)
    st.session_state.analysis_history.insert(0, entry)
    
    # Keep only the 20 most recent entries (slice prevents unbounded growth)
    st.session_state.analysis_history = st.session_state.analysis_history[:20]
    return True


def get_user_history(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieve analysis history for the current user.
    
    📌 TEACHING NOTE — Supabase Query Chaining:
        The Supabase Python client uses method chaining (fluent interface):
        
        client.table('analysis_history')  → target the table
            .select('*')                   → SELECT all columns
            .eq('user_id', user_id)        → WHERE user_id = ?
            .order('created_at', desc=True)→ ORDER BY created_at DESC
            .limit(limit)                  → LIMIT 20
            .execute()                     → run the query
        
        This is equivalent to the SQL:
        SELECT * FROM analysis_history
        WHERE user_id = 'rahul@gmail.com'
        ORDER BY created_at DESC
        LIMIT 20;
    
    📌 TEACHING NOTE — Data normalization after DB fetch:
        The DB returns raw row dicts from Supabase.
        We convert them to a consistent format using a loop — the same
        format that save_analysis_to_session() uses.
        
        This means the rest of the app only needs to handle ONE format,
        regardless of whether data came from DB or session state.
        This is called "normalizing" the data interface.
    
    Args:
        limit: Max number of history entries to return (default 20)
        
    Returns:
        List of history entry dicts (newest first)
    """
    client = get_supabase_client()
    
    # No DB → return from session state
    if not client:
        return st.session_state.get('analysis_history', [])[:limit]
    
    try:
        user_id = get_user_id()
        
        # Query database with filtering, sorting, and limiting
        response = client.table('analysis_history')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        # Normalize DB rows into our standard history format
        history = []
        for row in response.data:
            history.append({
                'id':           row.get('id'),       # DB row ID (needed for deletion)
                'filename':     row.get('filename'),
                # Convert "2024-01-15T14:30:00" → "2024-01-15 14:30" (display-friendly)
                'timestamp':    row.get('created_at', '')[:16].replace('T', ' '),
                'overall_score': row.get('overall_score', 0),
                'component_scores': {
                    'formatting_score':        row.get('formatting_score', 0),
                    'keywords_score':          row.get('keywords_score', 0),
                    'content_score':           row.get('content_score', 0),
                    'skill_validation_score':  row.get('skill_validation_score', 0),
                    'ats_compatibility_score': row.get('ats_compatibility_score', 0),
                },
                'jd_match': row.get('jd_match_percentage'),
            })
        
        return history
        
    except Exception as e:
        print(f"Database fetch error: {e}")
        # Fallback to session state if DB query fails
        return st.session_state.get('analysis_history', [])[:limit]


def delete_history_entry(entry_id: int) -> bool:
    """
    Delete a specific history entry by its database ID.
    
    📌 TEACHING NOTE — Security: Always filter by BOTH id AND user_id
        Notice the query uses TWO conditions:
            .eq('id', entry_id)
            .eq('user_id', user_id)
        
        Why both? Imagine if we only filtered by id:
        A malicious user could guess other users' entry IDs and delete them!
        
        By requiring both the entry ID AND the user's own ID to match,
        users can ONLY delete their own entries — not anyone else's.
        This is called "ownership validation" — a basic security requirement.
    
    Args:
        entry_id: Database row ID of the entry to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    client = get_supabase_client()
    
    if not client:
        return False  # Can't delete from DB if there's no DB connection
    
    try:
        user_id = get_user_id()
        # DELETE FROM analysis_history WHERE id = ? AND user_id = ?
        client.table('analysis_history')\
            .delete()\
            .eq('id', entry_id)\
            .eq('user_id', user_id)\
            .execute()
        return True
    except Exception:
        return False


def clear_user_history() -> bool:
    """
    Delete ALL history entries for the current user.
    
    📌 TEACHING NOTE — Soft vs Hard Delete:
        This function does a HARD delete — data is permanently removed.
        Some apps implement "soft delete" instead:
        - Add a 'deleted_at' column to the table
        - Set deleted_at = now() instead of actually deleting
        - Filter out deleted entries in queries
        
        Soft delete is useful for:
        - Data recovery ("oops I didn't mean to delete that")
        - Audit logs / compliance requirements
        - Analytics on deleted data
        
        For this app, hard delete is fine — resume scores aren't critical data.
    
    📌 TEACHING NOTE — Dual behavior (DB vs session):
        If DB is available  → delete from database (persistent)
        If DB not available → clear session state list (temporary)
        
        Both paths return True on success, False on failure.
    
    Returns:
        True if cleared successfully, False on error
    """
    client = get_supabase_client()
    
    if not client:
        # No DB — just clear the session state list
        st.session_state.analysis_history = []
        return True
    
    try:
        user_id = get_user_id()
        # DELETE FROM analysis_history WHERE user_id = ?
        client.table('analysis_history')\
            .delete()\
            .eq('user_id', user_id)\
            .execute()
        return True
    except Exception:
        return False


def is_database_configured() -> bool:
    """
    Check if the database is properly set up and reachable.
    
    📌 TEACHING NOTE — Feature Flag via function:
        This function acts as a feature flag — the UI can call this to decide:
        - Show "History saved to cloud ☁️" (DB configured)
        - Show "History saved locally only 💾" (no DB)
        
        It's better practice to call this ONCE and cache the result
        rather than calling get_supabase_client() multiple times
        (each call attempts a connection, which is slow).
        
        ⚠️ Suggested improvement: cache this result in session_state
        so we don't create a new client object on every check.
    
    Returns:
        True if Supabase client can be created, False otherwise
    """
    return get_supabase_client() is not None