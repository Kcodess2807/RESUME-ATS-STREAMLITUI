"""
ATS Resume Scorer - History Page

This page displays the user's analysis history and allows comparison
between different analyses.

Requirements: 2.3
"""

import streamlit as st
from datetime import datetime
from utils.auth import require_authentication, display_user_info, logout_button

# Configure page
st.set_page_config(
    page_title="History - ATS Resume Scorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS from file
def load_css():
    """Load custom CSS styles from the assets folder."""
    try:
        with open('assets/styles.css', 'r') as f:
            return f'<style>{f.read()}</style>'
    except FileNotFoundError:
        return ''

st.markdown(load_css(), unsafe_allow_html=True)

# Additional page-specific CSS
st.markdown("""
<style>
    /* History page header */
    .history-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(79, 70, 229, 0.3);
        animation: fadeInDown 0.6s ease-out;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* History card */
    .history-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.5s ease-out;
    }
    
    .history-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 25px rgba(0,0,0,0.1);
        border-color: #c7d2fe;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Score badge */
    .score-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        font-size: 1.25rem;
        font-weight: 700;
        color: white;
    }
    
    .score-badge-excellent {
        background: linear-gradient(135deg, #10B981, #34D399);
    }
    
    .score-badge-good {
        background: linear-gradient(135deg, #F59E0B, #FBBF24);
    }
    
    .score-badge-poor {
        background: linear-gradient(135deg, #EF4444, #F87171);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #64748b;
    }
    
    .empty-state-icon {
        font-size: 5rem;
        margin-bottom: 1.5rem;
        opacity: 0.5;
    }
    
    .empty-state h3 {
        color: #1e293b;
        margin-bottom: 0.75rem;
    }
    
    .empty-state p {
        max-width: 400px;
        margin: 0 auto 1.5rem;
    }
    
    /* Comparison section */
    .comparison-card {
        background: #f0f4ff;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #c7d2fe;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .history-header {
            padding: 1.5rem 1rem;
        }
        .history-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Require authentication
require_authentication("Please log in to view your analysis history.")

# Header
st.markdown("""
<div class="history-header">
    <h1>📊 Analysis History</h1>
    <p>Track your resume improvements over time</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 👤 User Profile")
    display_user_info(location='sidebar')
    logout_button(location='sidebar')
    
    st.markdown("---")
    
    st.markdown("## 📈 Quick Stats")
    
    # Get history from session state
    history = st.session_state.get('analysis_history', [])
    
    if history:
        st.metric("Total Analyses", len(history))
        scores = [h.get('overall_score', 0) for h in history]
        st.metric("Best Score", f"{max(scores):.0f}")
        st.metric("Average Score", f"{sum(scores)/len(scores):.0f}")
    else:
        st.info("No analyses yet")

# Initialize history in session state if not exists
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Main content
history = st.session_state.analysis_history

if not history:
    # Empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📋</div>
        <h3>No Analysis History Yet</h3>
        <p>Start by analyzing your resume to track your progress over time. 
        Each analysis will be saved here for comparison.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze Your First Resume", use_container_width=True, type="primary"):
            st.switch_page("pages/1_ATS_Scorer.py")
else:
    # Display history
    st.markdown("### 📜 Recent Analyses")
    
    # Sort by timestamp (most recent first)
    sorted_history = sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for i, analysis in enumerate(sorted_history):
        score = analysis.get('overall_score', 0)
        filename = analysis.get('filename', 'Unknown')
        timestamp = analysis.get('timestamp', 'Unknown date')
        
        # Determine score class
        if score >= 80:
            score_class = 'excellent'
            score_color = '#10B981'
        elif score >= 60:
            score_class = 'good'
            score_color = '#F59E0B'
        else:
            score_class = 'poor'
            score_color = '#EF4444'
        
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="score-badge score-badge-{score_class}">
                    {score:.0f}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{filename}**")
                st.caption(f"📅 {timestamp}")
                
                # Component scores
                components = analysis.get('component_scores', {})
                if components:
                    cols = st.columns(5)
                    labels = ['Format', 'Keywords', 'Content', 'Skills', 'ATS']
                    keys = ['formatting_score', 'keywords_score', 'content_score', 
                           'skill_validation_score', 'ats_compatibility_score']
                    for j, (col, label, key) in enumerate(zip(cols, labels, keys)):
                        with col:
                            val = components.get(key, 0)
                            st.caption(f"{label}: {val:.0f}")
            
            with col3:
                if st.button("📄 View", key=f"view_{i}"):
                    st.session_state.selected_analysis = analysis
                    st.rerun()
            
            st.markdown("---")
    
    # Comparison section
    st.markdown("### 📊 Compare Analyses")
    
    if len(history) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_options = [f"{h.get('filename', 'Unknown')} ({h.get('timestamp', 'Unknown')})" 
                              for h in sorted_history]
            selected1 = st.selectbox("First Analysis", analysis_options, key="compare1")
        
        with col2:
            selected2 = st.selectbox("Second Analysis", analysis_options, index=1 if len(analysis_options) > 1 else 0, key="compare2")
        
        if st.button("🔍 Compare", use_container_width=True):
            idx1 = analysis_options.index(selected1)
            idx2 = analysis_options.index(selected2)
            
            a1 = sorted_history[idx1]
            a2 = sorted_history[idx2]
            
            st.markdown("#### Comparison Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**{a1.get('filename', 'Analysis 1')}**")
                st.metric("Overall Score", f"{a1.get('overall_score', 0):.0f}")
            
            with col2:
                diff = a2.get('overall_score', 0) - a1.get('overall_score', 0)
                st.markdown("**Difference**")
                st.metric("Score Change", f"{diff:+.0f}", delta=f"{diff:+.0f}")
            
            with col3:
                st.markdown(f"**{a2.get('filename', 'Analysis 2')}**")
                st.metric("Overall Score", f"{a2.get('overall_score', 0):.0f}")
    else:
        st.info("Analyze at least 2 resumes to compare them.")

# View selected analysis details
if 'selected_analysis' in st.session_state and st.session_state.selected_analysis:
    st.markdown("---")
    st.markdown("### 📋 Analysis Details")
    
    analysis = st.session_state.selected_analysis
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**File:** {analysis.get('filename', 'Unknown')}")
        st.markdown(f"**Date:** {analysis.get('timestamp', 'Unknown')}")
    
    with col2:
        if st.button("✖️ Close Details"):
            st.session_state.selected_analysis = None
            st.rerun()
    
    # Display scores
    st.markdown("#### Score Breakdown")
    
    components = analysis.get('component_scores', {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("📝 Formatting", components.get('formatting_score', 0), 20),
        ("🔑 Keywords", components.get('keywords_score', 0), 25),
        ("📄 Content", components.get('content_score', 0), 25),
        ("✅ Skills", components.get('skill_validation_score', 0), 15),
        ("🤖 ATS", components.get('ats_compatibility_score', 0), 15),
    ]
    
    for col, (label, score, max_score) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.metric(label, f"{score:.0f}/{max_score}")
            st.progress(score / max_score)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p>Your analysis history is stored locally in your session.</p>
</div>
""", unsafe_allow_html=True)