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

# Google Authentication using streamlit-oauth
from streamlit_oauth import OAuth2Component
import jwt
import os

GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "http://localhost:8501")

oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/auth",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/revoke",
)

# Check if user is authenticated
if "token" not in st.session_state:
    # Show welcome message
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
    
    # Show login button
    result = oauth2.authorize_button(
        "Login with Google",
        REDIRECT_URI,
        "openid email profile",
    )
    
    if result and "token" in result:
        st.session_state.token = result["token"]
        st.rerun()
    
    st.stop()

# User is authenticated - decode token to get user info
token = st.session_state.token
user_info = jwt.decode(
    token["id_token"],
    options={"verify_signature": False}
)

email = user_info.get("email")
name = user_info.get("name")
picture = user_info.get("picture")

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
    
    # User info and logout
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
        # Clear token and rerun
        if "token" in st.session_state:
            del st.session_state.token
        st.rerun()

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
