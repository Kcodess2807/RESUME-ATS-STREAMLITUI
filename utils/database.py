"""
Database Module for ATS Resume Scorer

Uses Supabase (PostgreSQL) for persistent storage of analysis history.
Falls back to session state if database is not configured.
"""

import streamlit as st
from datetime import datetime
import json
from typing import Optional, List, Dict, Any

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client() -> Optional[Any]:
    """Get Supabase client if configured."""
    if not SUPABASE_AVAILABLE:
        return None
    
    try:
        url = st.secrets.get("supabase", {}).get("url")
        key = st.secrets.get("supabase", {}).get("key")
        
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    
    return None


def get_user_id() -> str:
    """Get current user's identifier."""
    # Try Google auth first
    try:
        if hasattr(st, 'experimental_user') and st.experimental_user.get('email'):
            return st.experimental_user.get('email')
    except Exception:
        pass
    
    # Fall back to guest with session ID
    if st.session_state.get('guest_authenticated'):
        # Use a consistent guest ID per session
        if 'guest_session_id' not in st.session_state:
            import uuid
            st.session_state.guest_session_id = f"guest_{uuid.uuid4().hex[:8]}"
        return st.session_state.guest_session_id
    
    return "anonymous"


def save_analysis_to_db(results: dict, filename: str) -> bool:
    """
    Save analysis results to database.
    
    Args:
        results: Complete analysis results dictionary
        filename: Name of the analyzed file
        
    Returns:
        True if saved successfully, False otherwise
    """
    client = get_supabase_client()
    
    if not client:
        # Fall back to session state
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
        # Fall back to session state
        return save_analysis_to_session(results, filename)


def save_analysis_to_session(results: dict, filename: str) -> bool:
    """Save analysis to session state as fallback."""
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
    Get analysis history for current user.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of history entries
    """
    client = get_supabase_client()
    
    if not client:
        # Return session state history
        return st.session_state.get('analysis_history', [])[:limit]
    
    try:
        user_id = get_user_id()
        
        response = client.table('analysis_history')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        # Convert to expected format
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
    """Delete a specific history entry."""
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
    """Clear all history for current user."""
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
    """Check if database is properly configured."""
    return get_supabase_client() is not None
