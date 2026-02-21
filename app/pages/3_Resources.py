"""
ATS Resume Scorer - Resources Page

This page provides resume writing tips and ATS optimization guidelines.

Requirements: 1.1
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Resources - ATS Resume Scorer",
    page_icon="📚",
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
    .resource-header {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #9333EA 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(79, 70, 229, 0.3);
    }
    
    .tip-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        margin: 1rem 0;
        border-left: 4px solid #4F46E5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .tip-box:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.15);
    }
    
    .guideline-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #ecfdf5 0%, #d1fae5 100%);
        margin: 1rem 0;
        border-left: 4px solid #10B981;
    }

    .warning-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #fffbeb 0%, #fef3c7 100%);
        margin: 1rem 0;
        border-left: 4px solid #F59E0B;
    }
    
    .checklist-item {
        padding: 0.875rem 1.25rem;
        margin: 0.5rem 0;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 8px;
        border-left: 3px solid #4F46E5;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="resource-header">
    <h1>📚 Resume Resources</h1>
    <p>Tips and guidelines to help you create an ATS-optimized resume</p>
</div>
""", unsafe_allow_html=True)

# Navigation tabs - only Writing Tips and ATS Guidelines
tab1, tab2 = st.tabs(["✍️ Writing Tips", "🎯 ATS Guidelines"])

# Tab 1: Resume Writing Tips
with tab1:
    st.markdown("## ✍️ Resume Writing Best Practices")
    
    st.markdown("""
    <div class="tip-box">
        <h4>📝 1. Start with a Strong Summary</h4>
        <p>Your professional summary should be 2-3 sentences that highlight your key qualifications, 
        years of experience, and what value you bring to employers. Make it specific to your target role.</p>
        <p><strong>Example:</strong> "Results-driven software engineer with 5+ years of experience 
        developing scalable web applications. Proficient in Python, JavaScript, and cloud technologies. 
        Proven track record of reducing system latency by 40% and improving user engagement."</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
        <h4>💪 2. Use Strong Action Verbs</h4>
        <p>Begin each bullet point with a powerful action verb to demonstrate your impact and achievements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Leadership:**
        - Directed
        - Managed
        - Led
        - Supervised
        - Coordinated
        """)
    with col2:
        st.markdown("""
        **Achievement:**
        - Achieved
        - Delivered
        - Exceeded
        - Improved
        - Increased
        """)
    with col3:
        st.markdown("""
        **Technical:**
        - Developed
        - Implemented
        - Engineered
        - Designed
        - Optimized
        """)
    
    st.markdown("""
    <div class="tip-box">
        <h4>📊 3. Quantify Your Achievements</h4>
        <p>Numbers make your accomplishments concrete and memorable. Include metrics wherever possible.</p>
        <ul>
            <li>❌ "Improved sales performance"</li>
            <li>✅ "Increased sales by 35% over 6 months, generating $500K in new revenue"</li>
        </ul>
        <ul>
            <li>❌ "Managed a team"</li>
            <li>✅ "Led a cross-functional team of 12 engineers across 3 time zones"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
        <h4>🎯 4. Tailor Your Resume for Each Job</h4>
        <p>Customize your resume for each application by:</p>
        <ul>
            <li>Matching keywords from the job description</li>
            <li>Highlighting relevant experience first</li>
            <li>Adjusting your summary to align with the role</li>
            <li>Reordering skills based on job requirements</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
        <h4>✅ 5. Proofread Thoroughly</h4>
        <p>Grammar and spelling errors can disqualify you immediately. Always:</p>
        <ul>
            <li>Use spell-check tools (like our built-in grammar checker!)</li>
            <li>Read your resume out loud</li>
            <li>Have someone else review it</li>
            <li>Check for consistent formatting and tense</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
        <h4>📏 6. Keep It Concise</h4>
        <p>Recruiters spend an average of 6-7 seconds on initial resume screening.</p>
        <ul>
            <li><strong>Entry-level:</strong> 1 page maximum</li>
            <li><strong>Mid-career:</strong> 1-2 pages</li>
            <li><strong>Senior/Executive:</strong> 2 pages maximum</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Tab 2: ATS Optimization Guidelines
with tab2:
    st.markdown("## 🎯 ATS Optimization Guidelines")
    
    st.info("""
    **What is an ATS?** An Applicant Tracking System (ATS) is software used by employers to 
    collect, sort, scan, and rank job applications. Over 90% of Fortune 500 companies use ATS 
    to filter resumes before a human ever sees them.
    """)
    
    st.markdown("### ✅ Do's")
    
    st.markdown("""
    <div class="guideline-box">
        <h4>📄 Use Standard Section Headers</h4>
        <p>ATS systems look for specific section names. Use these standard headers:</p>
        <ul>
            <li><strong>Summary</strong> or <strong>Professional Summary</strong></li>
            <li><strong>Experience</strong> or <strong>Work Experience</strong></li>
            <li><strong>Education</strong></li>
            <li><strong>Skills</strong> or <strong>Technical Skills</strong></li>
            <li><strong>Projects</strong></li>
            <li><strong>Certifications</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guideline-box">
        <h4>🔤 Use Standard Fonts</h4>
        <p>Stick to ATS-friendly fonts that are easy to parse:</p>
        <ul>
            <li>Arial</li>
            <li>Calibri</li>
            <li>Times New Roman</li>
            <li>Helvetica</li>
            <li>Georgia</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guideline-box">
        <h4>📝 Use Simple Formatting</h4>
        <ul>
            <li>Use standard bullet points (•, -, or *)</li>
            <li>Avoid tables, text boxes, and columns</li>
            <li>Use consistent date formats (MM/YYYY or Month YYYY)</li>
            <li>Keep margins between 0.5" and 1"</li>
            <li>Use 10-12pt font size for body text</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guideline-box">
        <h4>🔑 Include Relevant Keywords</h4>
        <ul>
            <li>Mirror exact phrases from the job description</li>
            <li>Include both spelled-out terms and acronyms (e.g., "Search Engine Optimization (SEO)")</li>
            <li>Use industry-standard terminology</li>
            <li>Include hard skills and technical competencies</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ❌ Don'ts")
    
    st.markdown("""
    <div class="warning-box">
        <h4>🚫 Avoid These Common Mistakes</h4>
        <ul>
            <li><strong>Headers and Footers:</strong> ATS often can't read content in headers/footers</li>
            <li><strong>Images and Graphics:</strong> ATS cannot parse images, logos, or icons</li>
            <li><strong>Fancy Formatting:</strong> Avoid text boxes, shapes, and complex layouts</li>
            <li><strong>Non-standard File Types:</strong> Stick to .docx or .pdf formats</li>
            <li><strong>Creative Section Names:</strong> "My Journey" instead of "Experience"</li>
            <li><strong>Embedded Tables:</strong> Use simple lists instead</li>
            <li><strong>Special Characters:</strong> Avoid symbols that may not parse correctly</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 ATS Optimization Checklist")
    
    checklist_items = [
        "File is in .docx or .pdf format",
        "Using standard section headers",
        "No images, graphics, or logos",
        "No tables or text boxes",
        "Using ATS-friendly fonts",
        "Contact info is in the main body (not header/footer)",
        "Keywords from job description are included",
        "Dates are in consistent format",
        "No special characters or symbols",
        "File size is under 5MB"
    ]
    
    for item in checklist_items:
        st.markdown(f"""
        <div class="checklist-item">
            ☐ {item}
        </div>
        """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📖 Quick Navigation")
    st.markdown("""
    - Writing Tips
    - ATS Guidelines
    """)
    
    st.markdown("---")
    
    st.markdown("## 🎯 Ready to Score?")
    if st.button("📊 Analyze Your Resume", use_container_width=True, type="primary"):
        st.switch_page("pages/1_🎯_ATS_Scorer.py")
    
    st.markdown("---")
    
    st.markdown("## 📈 Key Stats")
    st.metric("ATS Usage", "90%+", help="Percentage of Fortune 500 companies using ATS")
    st.metric("Avg. Review Time", "6-7 sec", help="Time recruiters spend on initial resume scan")
    st.metric("Keyword Match", "70%+", help="Recommended keyword match rate for ATS success")
    
    st.markdown("---")
    
    st.markdown("## 💡 Pro Tip")
    st.info("""
    Use our **ATS Scorer** to check your resume against a specific job description. 
    It will show you exactly which keywords you're missing!
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p>Built with ❤️ using Streamlit | All processing done locally for your privacy</p>
</div>
""", unsafe_allow_html=True)