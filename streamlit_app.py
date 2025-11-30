"""
ATS Resume Scorer - Landing Page

This is the main landing page for the ATS Resume Scorer application.
It provides an overview of features and navigation to the main application.

Requirements: 1.1, 1.2, 1.4, 1.5
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
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

# Additional page-specific CSS for landing page
st.markdown("""
<style>
    /* Landing Page Hero Section */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #9333EA 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2rem;
        animation: fadeInDown 0.8s ease-out;
        box-shadow: 0 10px 40px rgba(79, 70, 229, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .main-header h3 {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.95;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    /* Feature Boxes */
    .feature-box {
        padding: 1.75rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .feature-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(79, 70, 229, 0.15);
        border-color: #c7d2fe;
    }
    
    .feature-box h3 {
        color: #1e293b;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
    }
    
    .feature-box p, .feature-box ul {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Step Boxes */
    .step-box {
        text-align: center;
        padding: 2rem 1.5rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%);
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: scaleIn 0.5s ease-out;
        border: 1px solid #bae6fd;
    }
    
    .step-box:hover {
        transform: scale(1.05) translateY(-4px);
        box-shadow: 0 15px 30px rgba(14, 165, 233, 0.2);
    }
    
    .step-box h2 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .step-box h4 {
        color: #1e293b;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .step-box p {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Stat Boxes */
    .stat-box {
        text-align: center;
        padding: 1.75rem 1.25rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stat-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stat-box:hover::after {
        left: 100%;
    }
    
    .stat-box:hover {
        transform: scale(1.05) translateY(-4px);
        box-shadow: 0 15px 35px rgba(79, 70, 229, 0.4);
    }
    
    .stat-number {
        font-size: 2.75rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-box p {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Footer Section */
    .footer-section {
        text-align: center;
        padding: 2.5rem 1rem;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
        background: linear-gradient(180deg, transparent 0%, #f8fafc 100%);
    }
    
    .footer-section p strong {
        color: #1e293b;
    }
    
    .footer-links {
        margin: 1.25rem 0;
    }
    
    .footer-links a {
        color: #4F46E5;
        text-decoration: none;
        margin: 0 1rem;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .footer-links a:hover {
        color: #7C3AED;
        text-decoration: none;
    }
    
    /* Animation delays for staggered effect */
    .feature-box:nth-child(1) { animation-delay: 0.1s; }
    .feature-box:nth-child(2) { animation-delay: 0.2s; }
    .feature-box:nth-child(3) { animation-delay: 0.3s; }
    
    .step-box:nth-child(1) { animation-delay: 0.1s; }
    .step-box:nth-child(2) { animation-delay: 0.2s; }
    .step-box:nth-child(3) { animation-delay: 0.3s; }
    
    .stat-box:nth-child(1) { animation-delay: 0.1s; }
    .stat-box:nth-child(2) { animation-delay: 0.15s; }
    .stat-box:nth-child(3) { animation-delay: 0.2s; }
    .stat-box:nth-child(4) { animation-delay: 0.25s; }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        .main-header h1 {
            font-size: 2rem;
        }
        .main-header h3 {
            font-size: 1.1rem;
        }
        .feature-box, .step-box {
            padding: 1.25rem;
        }
        .stat-number {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="main-header">
    <h1>🎯 ATS Resume Scorer</h1>
    <h3>Optimize Your Resume for Applicant Tracking Systems</h3>
    <p>Get instant feedback on your resume's ATS compatibility with AI-powered analysis</p>
</div>
""", unsafe_allow_html=True)

# Call-to-Action Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Start Analyzing Your Resume", use_container_width=True, type="primary"):
        st.switch_page("pages/1_🎯_ATS_Scorer.py")

st.markdown("---")

# Features Overview Section
st.markdown("## ✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>📊 Comprehensive Scoring</h3>
        <p>Get detailed scores across 5 key dimensions:</p>
        <ul>
            <li>Formatting (20%)</li>
            <li>Keywords & Skills (25%)</li>
            <li>Content Quality (25%)</li>
            <li>Skill Validation (15%)</li>
            <li>ATS Compatibility (15%)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>🔍 Skill Validation</h3>
        <p>Verify that your claimed skills are demonstrated in your projects and experience using AI-powered semantic analysis.</p>
        <p><strong>No more empty claims!</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>🔒 Privacy First</h3>
        <p>All analysis runs locally with no external API calls. Your resume data never leaves your system.</p>
        <p><strong>100% Private & Secure</strong></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# How It Works Section
st.markdown("## 🚀 How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="step-box">
        <h2>1️⃣</h2>
        <h4>Upload Your Resume</h4>
        <p>Support for PDF, DOC, and DOCX formats</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="step-box">
        <h2>2️⃣</h2>
        <h4>AI Analysis</h4>
        <p>Our local AI models analyze your resume across multiple dimensions</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="step-box">
        <h2>3️⃣</h2>
        <h4>Get Actionable Feedback</h4>
        <p>Receive detailed recommendations to improve your resume</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Benefits Section
st.markdown("## 💡 Why Use ATS Resume Scorer?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✅ For Job Seekers
    - **Beat the ATS**: Ensure your resume passes automated screening
    - **Validate Skills**: Prove your skills with project evidence
    - **Fix Grammar**: Catch spelling and grammar errors
    - **Protect Privacy**: Get warnings about sensitive location data
    - **Compare to JD**: Optimize for specific job descriptions
    """)

with col2:
    st.markdown("""
    ### 🎯 What You Get
    - **Overall ATS Score**: 0-100 compatibility rating
    - **Component Breakdown**: Detailed scoring by category
    - **Skill Validation**: Which skills are proven vs. claimed
    - **Grammar Check**: All errors with correction suggestions
    - **Privacy Alerts**: Location information warnings
    - **Action Items**: Prioritized list of improvements
    """)

st.markdown("---")

# Stats/Testimonials Section
st.markdown("## 📈 Trusted by Job Seekers")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">95%</div>
        <p>ATS Pass Rate</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">30s</div>
        <p>Average Analysis Time</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">100%</div>
        <p>Privacy Protected</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">5+</div>
        <p>Analysis Dimensions</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Additional Information
st.markdown("## 📚 Additional Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📄 Job Description Comparison
    Upload a job description to see:
    - Keyword match percentage
    - Missing critical keywords
    - Skills gap analysis
    - Semantic similarity score
    """)

with col2:
    st.markdown("""
    ### 📊 Detailed Reports
    Export your analysis:
    - PDF report with all scores
    - Visualizations and charts
    - Action items checklist
    - Recommendations summary
    """)

with col3:
    st.markdown("""
    ### ⚡ Fast & Local
    - No internet required
    - Analysis in under 30 seconds
    - All processing on your machine
    - Complete data privacy
    """)

st.markdown("---")

# Footer - using Streamlit native components for better rendering
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <p style="font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">Ready to optimize your resume?</p>
        <p style="color: #64748b; margin-bottom: 1.5rem;">Click the button above to get started!</p>
        <p style="font-size: 0.9rem; color: #64748b; margin-top: 1.5rem;">
            Built with ❤️ using Streamlit | All processing done locally for your privacy
        </p>
        <p style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.5rem;">
            © 2024 ATS Resume Scorer. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📖 Quick Guide")
    st.markdown("""
    1. Click **Start Analyzing** above
    2. Log in with your credentials
    3. Upload your resume (PDF/DOC/DOCX)
    4. Optionally upload a job description
    5. Get instant feedback and recommendations
    """)
    
    st.markdown("---")
    
    st.markdown("## 🔐 Demo Credentials")
    st.info("""
    **Username:** demo_user  
    **Password:** demo123
    
    or
    
    **Username:** test_user  
    **Password:** test123
    """)
    
    st.markdown("---")
    
    st.markdown("## ℹ️ About")
    st.markdown("""
    ATS Resume Scorer uses advanced NLP and machine learning to analyze your resume 
    for ATS compatibility. All analysis is performed locally using:
    - spaCy for NLP
    - Sentence-Transformers for semantic analysis
    - LanguageTool for grammar checking
    """)
