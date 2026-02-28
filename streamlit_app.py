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

# Google OAuth2 Authentication - Pure Python Implementation
import requests
import urllib.parse
import json

GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "http://localhost:8501")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def get_auth_url():
    """Generate Google OAuth2 authorization URL"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    return GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)

def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    return response.json()

def get_user_info(access_token):
    """Get user information from Google"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    return response.json()

# Authentication flow
if "user" not in st.session_state:
    query_params = st.query_params
    
    if "code" in query_params:
        # Handle OAuth callback
        code = query_params["code"]
        try:
            token_data = exchange_code_for_token(code)
            if "access_token" in token_data:
                user_info = get_user_info(token_data["access_token"])
                st.session_state.user = user_info
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Authentication failed. Please try again.")
                st.stop()
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.stop()
    else:
        # Show login page
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
        
        auth_url = get_auth_url()
        st.markdown(
            f'<a href="{auth_url}" target="_self">'
            '<button style="background-color:#4285F4;color:white;padding:12px 24px;'
            'border:none;border-radius:4px;cursor:pointer;font-size:16px;font-weight:500;">'
            '🔐 Login with Google</button></a>',
            unsafe_allow_html=True
        )
        st.stop()

# User is authenticated
user = st.session_state.user
email = user.get("email")
name = user.get("name")
picture = user.get("picture")

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
        # Clear user session and rerun
        if "user" in st.session_state:
            del st.session_state.user
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
