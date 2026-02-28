"""
ATS Resume Scorer - Single Page Application
All views handled in one file to maintain session state
"""

import streamlit as st
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure page
st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Authentication
try:
    from streamlit_google_auth import Authenticate
    
    # Initialize authenticator
    # In production (Streamlit Cloud), credentials come from secrets
    # In local dev, they come from google_credentials.json
    try:
        authenticator = Authenticate(
            secret_credentials_path='google_credentials.json',
            cookie_name='ats_resume_scorer_cookie',
            cookie_key='ats_resume_scorer_secret_key',
            redirect_uri='http://localhost:8501',
        )
    except FileNotFoundError:
        # Production: use secrets instead of file
        import json
        import tempfile
        
        # Create credentials from secrets
        google_oauth = st.secrets.get("google_oauth", {})
        credentials = {
            "web": {
                "client_id": google_oauth.get("client_id"),
                "client_secret": google_oauth.get("client_secret"),
                "redirect_uris": [google_oauth.get("redirect_uri", "http://localhost:8501")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials, f)
            temp_creds_path = f.name
        
        authenticator = Authenticate(
            secret_credentials_path=temp_creds_path,
            cookie_name='ats_resume_scorer_cookie',
            cookie_key='ats_resume_scorer_secret_key',
            redirect_uri=google_oauth.get("redirect_uri", "http://localhost:8501"),
        )
    
    # Check authentication
    authenticator.check_authentification()
    
    # If not authenticated, show login and stop
    if not st.session_state.get('connected'):
        # Show a welcome message before login
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎯 ATS Resume Scorer</h1>
            <p style="font-size: 1.3rem; color: #666; margin-bottom: 2rem;">
                Optimize your resume for Applicant Tracking Systems
            </p>
            <p style="font-size: 1.1rem; color: #888;">
                Please sign in with your Google account to continue
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        authenticator.login()
        st.stop()
    
    # User is authenticated - get user info
    user_info = st.session_state.get('user_info', {})
    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')
    
    AUTH_ENABLED = True
    
except ImportError:
    # If streamlit-google-auth is not available, run without authentication
    st.warning("⚠️ Authentication module not available. Running in open mode.")
    AUTH_ENABLED = False
    email = None
    name = None
    picture = None

# Load custom CSS
def load_css():
    try:
        css_path = Path(__file__).parent / 'assets' / 'styles.css'
        with open(css_path, 'r') as f:
            return f'<style>{f.read()}</style>'
    except FileNotFoundError:
        return ''

st.markdown(load_css(), unsafe_allow_html=True)

# Initialize session state for view management
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'landing'

# Sidebar navigation
with st.sidebar:
    st.markdown("## Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = 'landing'
        st.rerun()
    
    if st.button("🎯 ATS Scorer", use_container_width=True):
        st.session_state.current_view = 'scorer'
        st.rerun()
    
    if st.button("📊 History", use_container_width=True):
        st.session_state.current_view = 'history'
        st.rerun()
    
    if st.button("📚 Resources", use_container_width=True):
        st.session_state.current_view = 'resources'
        st.rerun()
    
    # User info and logout (if authenticated)
    if AUTH_ENABLED and st.session_state.get('connected'):
        st.markdown("---")
        st.markdown("### 👤 Account")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if picture:
                st.image(picture, width=50)
            else:
                st.markdown("👤")
        
        with col2:
            st.markdown(f"**{name or 'User'}**")
            st.caption(email or '')
        
        if st.button("🚪 Logout", use_container_width=True):
            authenticator.logout()

# Main content area - render based on current view
if st.session_state.current_view == 'landing':
    # Import and render landing page
    from app.views import landing
    landing.render()

elif st.session_state.current_view == 'scorer':
    # Import and render scorer page
    from app.views import scorer
    scorer.render()

elif st.session_state.current_view == 'history':
    # Import and render history page
    from app.views import history
    history.render()

elif st.session_state.current_view == 'resources':
    # Import and render resources page
    from app.views import resources
    resources.render()
