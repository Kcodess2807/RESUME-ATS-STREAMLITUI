"""
Authentication Module for ATS Resume Scorer

Uses Streamlit's native authentication (st.login) for Google OAuth
and custom session state for Guest login.
"""

import streamlit as st
from datetime import datetime

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'guest_authenticated': False,
        'guest_name': None,
        'session_start': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_as_guest():
    """Log in as guest."""
    st.session_state.guest_authenticated = True
    st.session_state.guest_name = "Guest User"
    st.session_state.session_start = datetime.now()


def logout():
    """Log out current user."""
    # Logout from Google
    if hasattr(st, 'logout'):
        st.logout()
    
    # Clear guest session
    st.session_state.guest_authenticated = False
    st.session_state.guest_name = None
    st.session_state.session_start = None


def is_authenticated() -> bool:
    """Check if user is authenticated (either via Google or Guest)."""
    init_session_state()
    # Check for Streamlit native auth (st.experimental_user)
    # Note: In some versions/environments, is_logged_in might not be directly available
    # or might be False locally.
    try:
        if hasattr(st, 'experimental_user') and st.experimental_user.get('email'):
            return True
    except Exception:
        pass
        
    return st.session_state.guest_authenticated


def require_authentication(redirect_message: str = "Please log in to access this page."):
    """Require authentication for the page."""
    init_session_state()
    
    # Check if already authenticated
    if is_authenticated():
        return
    
    # Show login UI
    st.warning(redirect_message)
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🎯 ATS Resume Scorer</h2>
        <p style="color: #666;">Sign in to analyze your resume</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if Google OAuth is properly configured
    google_oauth_configured = _is_google_oauth_configured()
    
    if google_oauth_configured:
        col1, col2 = st.columns(2)
        
        with col1:
            # Google Sign-In (Native)
            if st.button("🔐 Log in with Google", use_container_width=True, type="primary"):
                st.login()
                
        with col2:
            # Guest Login
            if st.button("👤 Continue as Guest", use_container_width=True):
                login_as_guest()
                st.rerun()
    else:
        # Only show guest login when OAuth is not configured
        st.info("💡 Google OAuth is not configured. You can continue as a guest.")
        if st.button("👤 Continue as Guest", use_container_width=True, type="primary"):
            login_as_guest()
            st.rerun()
    
    st.stop()


def _is_google_oauth_configured() -> bool:
    """Check if Google OAuth credentials are properly configured."""
    try:
        # Check Streamlit's native auth format: [auth.google]
        if hasattr(st, 'secrets') and 'auth' in st.secrets:
            auth_config = st.secrets.auth
            if 'google' in auth_config:
                client_id = auth_config.google.get('client_id', '')
                client_secret = auth_config.google.get('client_secret', '')
                
                # Check for placeholder values
                if client_id and client_secret:
                    if 'YOUR_' not in client_id and 'YOUR_' not in client_secret:
                        return True
        return False
    except Exception:
        return False


def display_user_info(location: str = 'sidebar'):
    """Display user info."""
    init_session_state()
    
    if not is_authenticated():
        return
    
    # Determine user details
    google_email = None
    try:
        if hasattr(st, 'experimental_user'):
            google_email = st.experimental_user.get('email')
    except Exception:
        pass

    if google_email:
        name = st.experimental_user.get('name', 'Google User')
        email = google_email
        auth_type = "Google"
        # Try to get avatar if available (not always present in experimental_user)
        picture = None 
    else:
        name = st.session_state.guest_name
        email = "guest@example.com"
        auth_type = "Guest"
        picture = None
    
    st.markdown("### 👤 User Profile")
    
    st.markdown(f"**{name}**")
    if email:
        st.caption(email)
    
    st.caption(f"🏷️ {auth_type} Mode")


def logout_button(location: str = 'sidebar'):
    """Display logout button."""
    if not is_authenticated():
        return
    
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()
