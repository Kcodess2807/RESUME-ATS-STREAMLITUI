"""
Database Module for ATS Resume Scorer

Handles persistent storage of resume analysis history using Supabase (PostgreSQL).
Falls back to in-memory session state if Supabase is not configured.

No authentication required - uses session-based user IDs.
"""

import streamlit as st
from datetime import datetime
import os
from typing import Optional, List, Dict, Any
import uuid

# Try to import Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Try to load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_supabase_client() -> Optional[Any]:
    """
    Create and return a Supabase database client if credentials are available.
    
    Returns:
        Supabase Client object if configured, None otherwise
    """
    if not SUPABASE_AVAILABLE:
        return None
    
    try:
        # Method 1: Environment variables
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        # Method 2: Streamlit secrets
        if not url or not key:
            url = st.secrets.get("supabase", {}).get("url")
            key = st.secrets.get("supabase", {}).get("key")
        
        if url and key:
            return create_client(url, key)
    except Exception as e:
        print(f"Supabase client creation error: {e}")
    
    return None


def get_user_id() -> str:
    """
    Generate a unique identifier for the current session.
    No authentication - just a session-based ID.
    
    Returns:
        String identifier for the current session
    """
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
    return st.session_state.session_id


def save_analysis_to_db(results: dict, filename: str) -> bool:
    """
    Save analysis result to database (or session state as fallback).
    
    Args:
        results: Full analysis results dictionary
        filename: Name of the uploaded resume file
        
    Returns:
        True if saved successfully
    """
    client = get_supabase_client()
    
    # No database → use session state
    if not client:
        return save_analysis_to_session(results, filename)
    
    try:
        user_id = get_user_id()
        scores = results.get('scores', {})
        jd_comp = results.get('jd_comparison')
        
        data = {
            'user_id': user_id,
            'filename': filename,
            'overall_score': scores.get('overall_score', 0),
            'formatting_score': scores.get('formatting_score', 0),
            'keywords_score': scores.get('keywords_score', 0),
            'content_score': scores.get('content_score', 0),
            'skill_validation_score': scores.get('skill_validation_score', 0),
            'ats_compatibility_score': scores.get('ats_compatibility_score', 0),
            'jd_match_percentage': jd_comp.get('match_percentage') if jd_comp else None,
            'created_at': datetime.now().isoformat(),
        }
        
        client.table('analysis_history').insert(data).execute()
        return True
        
    except Exception as e:
        print(f"Database save error: {e}")
        return save_analysis_to_session(results, filename)


def save_analysis_to_session(results: dict, filename: str) -> bool:
    """
    Save analysis results to session state (in-memory fallback).
    
    Args:
        results: Analysis results dict
        filename: Resume filename
        
    Returns:
        Always True
    """
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    scores = results.get('scores', {})
    jd_comp = results.get('jd_comparison')
    
    entry = {
        'filename': filename,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'overall_score': scores.get('overall_score', 0),
        'component_scores': {
            'formatting_score': scores.get('formatting_score', 0),
            'keywords_score': scores.get('keywords_score', 0),
            'content_score': scores.get('content_score', 0),
            'skill_validation_score': scores.get('skill_validation_score', 0),
            'ats_compatibility_score': scores.get('ats_compatibility_score', 0),
        },
        'jd_match': jd_comp.get('match_percentage') if jd_comp else None,
    }
    
    st.session_state.analysis_history.insert(0, entry)
    st.session_state.analysis_history = st.session_state.analysis_history[:20]
    return True


def get_user_history(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieve analysis history for the current session.
    
    Args:
        limit: Max number of history entries to return
        
    Returns:
        List of history entry dicts (newest first)
    """
    client = get_supabase_client()
    
    # No DB → return from session state
    if not client:
        return st.session_state.get('analysis_history', [])[:limit]
    
    try:
        user_id = get_user_id()
        
        response = client.table('analysis_history')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        history = []
        for row in response.data:
            history.append({
                'id': row.get('id'),
                'filename': row.get('filename'),
                'timestamp': row.get('created_at', '')[:16].replace('T', ' '),
                'overall_score': row.get('overall_score', 0),
                'component_scores': {
                    'formatting_score': row.get('formatting_score', 0),
                    'keywords_score': row.get('keywords_score', 0),
                    'content_score': row.get('content_score', 0),
                    'skill_validation_score': row.get('skill_validation_score', 0),
                    'ats_compatibility_score': row.get('ats_compatibility_score', 0),
                },
                'jd_match': row.get('jd_match_percentage'),
            })
        
        return history
        
    except Exception as e:
        print(f"Database fetch error: {e}")
        return st.session_state.get('analysis_history', [])[:limit]


def delete_history_entry(entry_id: int) -> bool:
    """
    Delete a specific history entry by its database ID.
    
    Args:
        entry_id: Database row ID of the entry to delete
        
    Returns:
        True if deleted successfully
    """
    client = get_supabase_client()
    
    if not client:
        return False
    
    try:
        user_id = get_user_id()
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
    Delete ALL history entries for the current session.
    
    Returns:
        True if cleared successfully
    """
    client = get_supabase_client()
    
    if not client:
        st.session_state.analysis_history = []
        return True
    
    try:
        user_id = get_user_id()
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
    
    Returns:
        True if Supabase client can be created
    """
    return get_supabase_client() is not None
