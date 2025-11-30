"""
Authentication Module for ATS Resume Scorer

Supports Google OAuth and Guest login.
Works with both local development and Streamlit Cloud.
"""

import streamlit as st
from typing import Optional
from datetime import datetime
import json
import os

# Try to import Google OAuth
try:
    from streamlit_google_auth import Authenticate
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False


def get_google_credentials():
    """Get Google OAuth credentials from secrets or local file."""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
            return {
                'client_id': st.secrets['google_oauth']['client_id'],
                'client_secret': st.secrets['google_oauth']['client_secret'],
                'redirect_uri': st.secrets['google_oauth'].get('redirect_uri', 'http://localhost:8501')
            }
    except Exception:
        pass
    
    # Fall back to local client_secret.json
    try:
        if os.path.exists('client_secret.json'):
            with open('client_secret.json', 'r') as f:
                creds = json.load(f)
                web = creds.get('web', {})
                return {
                    'client_id': web.get('client_id'),
                    'client_secret': web.get('client_secret'),
                    'redirect_uri': 'http://localhost:8501'
                }
    except Exception:
        pass
    
    return None


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'authenticated': False,
        'user_name': None,
        'user_email': None,
        'user_picture': None,
        'auth_method': None,
        'session_start': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_as_guest():
    """Log in as guest."""
    st.session_state.authenticated = True
    st.session_state.user_name = "Guest User"
    st.session_state.user_email = "guest@example.com"
    st.session_state.user_picture = None
    st.session_state.auth_method = "guest"
    st.session_state.session_start = datetime.now()


def login_with_google(user_info: dict):
    """Log in with Google user info."""
    st.session_state.authenticated = True
    st.session_state.user_name = user_info.get('name', 'Google User')
    st.session_state.user_email = user_info.get('email', '')
    st.session_state.user_picture = user_info.get('picture')
    st.session_state.auth_method = "google"
    st.session_state.session_start = datetime.now()


def logout():
    """Log out current user."""
    keys_to_clear = ['authenticated', 'user_name', 'user_email', 'user_picture', 
                     'auth_method', 'session_start', 'connected', 'user_info']
    for key in keys_to_clear:
        if key in st.session_state:
            if key == 'authenticated':
                st.session_state[key] = False
            else:
                st.session_state[key] = None


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    init_session_state()
    return st.session_state.authenticated


def require_authentication(redirect_message: str = "Please log in to access this page."):
    """Require authentication for the page."""
    init_session_state()
    
    # Already authenticated
    if st.session_state.authenticated:
        return
    
    # Check if Google auth completed
    if GOOGLE_AUTH_AVAILABLE and st.session_state.get('connected'):
        user_info = st.session_state.get('user_info', {})
        if user_info:
            login_with_google(user_info)
            st.rerun()
    
    # Show login UI
    st.warning(redirect_message)
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🎯 ATS Resume Scorer</h2>
        <p style="color: #666;">Sign in to analyze your resume</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Guest Login
        st.markdown("#### 🚀 Quick Start")
        if st.button("👤 Continue as Guest", use_container_width=True, type="primary"):
            login_as_guest()
            st.rerun()
        
        st.markdown("---")
        
        # Google Sign-In
        st.markdown("#### 🔐 Sign in with Google")
        
        if GOOGLE_AUTH_AVAILABLE:
            try:
                # Check if client_secret.json exists, if not try to create from secrets
                if not os.path.exists('client_secret.json'):
                    if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                        # Create temporary client_secret.json from secrets
                        secrets_dict = {
                            "web": {
                                "client_id": st.secrets['google_oauth']['client_id'],
                                "client_secret": st.secrets['google_oauth']['client_secret'],
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                "redirect_uris": [st.secrets['google_oauth'].get('redirect_uri', 'http://localhost:8501')]
                            }
                        }
                        with open('client_secret.json', 'w') as f:
                            json.dump(secrets_dict, f)
                
                redirect_uri = 'http://localhost:8501'
                if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
                    redirect_uri = st.secrets['google_oauth'].get('redirect_uri', 'http://localhost:8501')

                authenticator = Authenticate(
                    secret_credentials_path='client_secret.json',
                    cookie_name='ats_scorer_auth',
                    cookie_key='ats_scorer_key_2024',
                    redirect_uri=redirect_uri,
                )
                
                # Check authentication status
                authenticator.check_authentification()
                
                if st.session_state.get('connected'):
                    user_info = st.session_state.get('user_info', {})
                    if user_info:
                        login_with_google(user_info)
                        st.rerun()
                else:
                    # Show Google login button
                    authenticator.login()
                    
            except Exception as e:
                st.error(f"Google Sign-In error: {e}")
                st.info("Use Guest login instead")
        else:
            st.info("Google Sign-In not available. Use Guest login.")
    
    st.stop()


def display_user_info(location: str = 'sidebar'):
    """Display user info."""
    init_session_state()
    
    if not st.session_state.authenticated:
        return
    
    name = st.session_state.user_name or "User"
    email = st.session_state.user_email or ""
    picture = st.session_state.user_picture
    auth_method = st.session_state.auth_method or ""
    
    # Session duration
    duration_str = ""
    if st.session_state.session_start:
        duration = datetime.now() - st.session_state.session_start
        mins = int(duration.total_seconds() // 60)
        duration_str = f"{mins}m"
    
    st.markdown("### 👤 User Profile")
    
    if picture:
        st.image(picture, width=50)
    
    st.markdown(f"**{name}**")
    if email:
        st.caption(email)
    
    if auth_method == "guest":
        st.caption("🏷️ Guest Mode")
    elif auth_method == "google":
        st.caption("🔵 Google")
    
    if duration_str:
        st.caption(f"⏱️ Session: {duration_str}")


def logout_button(location: str = 'sidebar'):
    """Display logout button."""
    init_session_state()
    
    if not st.session_state.authenticated:
        return
    
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()


# Legacy compatibility
def get_auth_manager():
    return None


class AuthenticationManager:
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
