"""
Authentication Module for ATS Resume Scorer
Supports Supabase Google OAuth (PKCE flow) and Guest Login.
"""

import streamlit as st
from typing import Optional
from datetime import datetime
import logging
import os
import json
import tempfile
import secrets
import base64
import hashlib
from pathlib import Path
from urllib.parse import urlencode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not available")

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── PKCE Storage ────────────────────────────────────────────────────────────
_PKCE_STORE_DIR = Path(tempfile.gettempdir()) / "streamlit_pkce"


def _generate_code_verifier() -> str:
    """Generate a PKCE code_verifier (random string)."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    return verifier.rstrip('=')


def _generate_code_challenge(verifier: str) -> str:
    """Generate a PKCE code_challenge from a code_verifier using SHA256."""
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64.urlsafe_b64encode(digest).decode('utf-8')
    return challenge.rstrip('=')


def _save_code_verifier(code_verifier: str):
    """Save the PKCE code_verifier to a temp file."""
    _PKCE_STORE_DIR.mkdir(exist_ok=True)
    store_file = _PKCE_STORE_DIR / "latest_verifier.json"
    data = {
        "code_verifier": code_verifier,
        "timestamp": datetime.now().isoformat()
    }
    store_file.write_text(json.dumps(data))
    logger.info(f"Saved code_verifier to {store_file}")


def _load_code_verifier() -> Optional[str]:
    """Load the PKCE code_verifier from the temp file."""
    store_file = _PKCE_STORE_DIR / "latest_verifier.json"
    if store_file.exists():
        try:
            data = json.loads(store_file.read_text())
            verifier = data.get("code_verifier")
            logger.info(f"Loaded code_verifier from {store_file}")
            return verifier
        except Exception as e:
            logger.error(f"Failed to read code_verifier: {e}")
    else:
        logger.warning(f"Code verifier file not found at {store_file}")
    return None


def _delete_code_verifier():
    """Delete the PKCE code_verifier file after successful exchange."""
    store_file = _PKCE_STORE_DIR / "latest_verifier.json"
    try:
        store_file.unlink(missing_ok=True)
        logger.info(f"Deleted code_verifier file")
    except Exception as e:
        logger.error(f"Failed to delete code_verifier: {e}")


# ── Supabase Client ─────────────────────────────────────────────────────────

def get_supabase_client() -> Optional[any]:
    """Get Supabase client for authentication."""
    if not SUPABASE_AVAILABLE:
        return None

    try:
        url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

        if url and key:
            return create_client(url, key)
    except Exception as e:
        logger.error(f"Supabase client creation error: {e}")

    return None


def _get_redirect_url() -> str:
    """Get the OAuth redirect URL for the app."""
    return os.getenv("SUPABASE_REDIRECT_URL", "http://localhost:8501")


# ── Session Management ──────────────────────────────────────────────────────

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'authenticated': False,
        'user_name': None,
        'user_email': None,
        'user_picture': None,
        'auth_method': None,
        'session_start': None,
        'supabase_user': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _set_user_session(user):
    """Populate session state from a Supabase user object."""
    st.session_state.authenticated = True
    st.session_state.user_email = user.email
    st.session_state.user_name = (
        user.user_metadata.get('full_name')
        or user.user_metadata.get('name')
        or user.email.split('@')[0]
    )
    st.session_state.user_picture = user.user_metadata.get('avatar_url')
    st.session_state.auth_method = "google"
    st.session_state.session_start = datetime.now()
    st.session_state.supabase_user = user
    logger.info(f"User session set for: {user.email}")


# ── OAuth Flow ──────────────────────────────────────────────────────────────

def _generate_oauth_url() -> Optional[str]:
    """
    Generate the OAuth URL with custom PKCE parameters.
    
    We generate our own code_verifier and code_challenge to ensure they match.
    """
    try:
        supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        redirect_url = _get_redirect_url()
        
        if not supabase_url:
            logger.error("SUPABASE_URL not configured")
            return None
        
        # Generate PKCE parameters
        code_verifier = _generate_code_verifier()
        code_challenge = _generate_code_challenge(code_verifier)
        
        logger.info(f"Generated code_verifier: {code_verifier[:20]}...")
        logger.info(f"Generated code_challenge: {code_challenge[:20]}...")
        
        # Save verifier for later exchange
        _save_code_verifier(code_verifier)
        
        # Build OAuth URL
        params = {
            "provider": "google",
            "redirect_to": redirect_url,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        oauth_url = f"{supabase_url}/auth/v1/authorize?{urlencode(params)}"
        logger.info("OAuth URL generated successfully")
        
        return oauth_url

    except Exception as e:
        logger.error(f"Error generating OAuth URL: {e}", exc_info=True)
        return None


def check_supabase_session():
    """
    Check for OAuth callback and handle code exchange.
    
    Returns True if user is authenticated.
    """
    client = get_supabase_client()
    if not client:
        return False

    try:
        query_params = st.query_params
        
        # Log query params for debugging
        if query_params:
            logger.info(f"Query params: {list(query_params.keys())}")
        
        # ━━━ Handle PKCE callback ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if 'code' in query_params:
            auth_code = query_params.get('code')
            logger.info(f"OAuth code found: {auth_code[:20]}...")

            # Load the saved code_verifier
            code_verifier = _load_code_verifier()
            
            if not code_verifier:
                logger.error("No code_verifier found!")
                st.error(
                    "Authentication session expired. "
                    "Please try signing in again or use Guest mode."
                )
                st.query_params.clear()
                return False

            try:
                logger.info(f"Exchanging code with verifier (length={len(code_verifier)})")
                
                # Exchange code for session
                response = client.auth.exchange_code_for_session({
                    "auth_code": auth_code,
                    "code_verifier": code_verifier,
                })

                if response and hasattr(response, 'user') and response.user:
                    _set_user_session(response.user)
                    logger.info(f"✅ Login successful: {response.user.email}")
                    
                    # Clean up
                    _delete_code_verifier()
                    st.query_params.clear()
                    st.rerun()
                    return True
                else:
                    logger.error("No user in exchange response")
                    st.error("Authentication failed. Please try again or use Guest mode.")
                    st.query_params.clear()

            except Exception as e:
                logger.error(f"Code exchange failed: {e}", exc_info=True)
                st.error(f"Authentication error: {str(e)}")
                st.query_params.clear()
                return False

        # ━━━ Check for existing session ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            session = client.auth.get_session()
            if session and hasattr(session, 'user') and session.user:
                if not st.session_state.get('authenticated'):
                    _set_user_session(session.user)
                    logger.info(f"Existing session found: {session.user.email}")
                return True
        except Exception as e:
            logger.debug(f"No existing session: {e}")

    except Exception as e:
        logger.error(f"Session check error: {e}", exc_info=True)

    return False


# ── Login Functions ─────────────────────────────────────────────────────────

def login_with_google():
    """Display Google OAuth login button."""
    client = get_supabase_client()

    if not client:
        st.error("Supabase is not configured. Please check your credentials.")
        return

    try:
        oauth_url = _generate_oauth_url()

        if oauth_url:
            st.link_button(
                "🔑 Continue with Google",
                oauth_url,
                use_container_width=True,
                type="primary"
            )
        else:
            st.error("Failed to generate OAuth URL")

    except Exception as e:
        logger.error(f"Google OAuth error: {e}", exc_info=True)
        st.error(f"Authentication error: {str(e)}")


def login_as_guest():
    """Log in as Guest user."""
    logger.info("Guest login initiated")
    st.session_state.authenticated = True
    st.session_state.user_name = "Guest User"
    st.session_state.user_email = "guest@example.com"
    st.session_state.auth_method = "guest"
    st.session_state.session_start = datetime.now()
    logger.info("Guest login successful")


def logout():
    """Clear authentication and sign out."""
    if st.session_state.get('auth_method') == 'google':
        client = get_supabase_client()
        if client:
            try:
                client.auth.sign_out()
                logger.info("Signed out from Supabase")
            except Exception as e:
                logger.error(f"Supabase logout error: {e}")

    # Clear session state
    keys_to_clear = [
        'authenticated', 'user_name', 'user_email', 'user_picture',
        'auth_method', 'session_start', 'supabase_user'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            if key == 'authenticated':
                st.session_state[key] = False
            else:
                st.session_state[key] = None
    
    logger.info("User logged out")


# ── Authentication Guards ───────────────────────────────────────────────────

def is_authenticated() -> bool:
    """Check if user is currently logged in."""
    init_session_state()
    return st.session_state.authenticated


def require_authentication(redirect_message: str = "Please log in to access this page."):
    """Block page access if user is not authenticated."""
    init_session_state()

    # Check for OAuth callback or existing session
    if not st.session_state.authenticated:
        check_supabase_session()

    # If authenticated, allow access
    if st.session_state.authenticated:
        logger.info(f"User authenticated: {st.session_state.user_name}")
        return

    # Not authenticated - show login UI
    logger.info("User not authenticated - showing login UI")
    st.warning(redirect_message)

    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🎯 ATS Resume Scorer</h2>
        <p style="color: #666;">Sign in to analyze your resume</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Google Login
        st.markdown("### 🔐 Sign in with Google")
        
        client = get_supabase_client()
        if client:
            login_with_google()
        else:
            st.error("⚠️ Supabase is not configured. Check SUPABASE_URL and SUPABASE_KEY.")

        st.markdown("---")

        # Guest Login
        st.markdown("### 🚀 Quick Access")
        st.caption("Start analyzing your resume without signing in")
        if st.button("👤 Continue as Guest", use_container_width=True):
            login_as_guest()
            st.rerun()

    st.stop()


# ── UI Components ───────────────────────────────────────────────────────────

def display_user_info(location: str = 'sidebar'):
    """Display logged-in user's profile information."""
    init_session_state()

    if not st.session_state.authenticated:
        return

    name = st.session_state.user_name or "User"
    email = st.session_state.user_email or ""
    picture = st.session_state.user_picture
    auth_method = st.session_state.auth_method or ""

    duration_str = ""
    if st.session_state.session_start:
        duration = datetime.now() - st.session_state.session_start
        mins = int(duration.total_seconds() // 60)
        duration_str = f"{mins}m"

    st.markdown("### 👤 User Profile")

    if picture:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(picture, width=50)
        with col2:
            st.markdown(f"**{name}**")
            if email:
                st.caption(email)
    else:
        st.markdown(f"**{name}**")
        if email:
            st.caption(email)

    if auth_method == "google":
        st.caption("🔐 Google Account")
    elif auth_method == "guest":
        st.caption("🏷️ Guest Mode")

    if duration_str:
        st.caption(f"⏱️ Session: {duration_str}")


def logout_button(location: str = 'sidebar'):
    """Render a logout button."""
    init_session_state()

    if not st.session_state.authenticated:
        return

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()


# ── Legacy Compatibility ────────────────────────────────────────────────────

def get_auth_manager():
    """Legacy function - returns None."""
    return None


class AuthenticationManager:
    """Legacy class for backward compatibility."""

    def __init__(self, *args, **kwargs):
        pass

    def is_authenticated(self):
        return is_authenticated()

    def require_authentication(self, msg=""):
        require_authentication(msg)

    def display_user_info(self, location='sidebar'):
        display_user_info(location)

    def logout(self, location='sidebar'):
        logout_button(location)
