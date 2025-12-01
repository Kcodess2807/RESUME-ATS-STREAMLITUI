"""
ATS Resume Scorer - Main Analysis Page

This page provides the main resume analysis functionality.
It requires authentication and displays the analysis interface.

Requirements: 2.1, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 15.1, 15.2, 15.3, 15.4, 15.5
"""

import streamlit as st
from utils.auth import require_authentication, display_user_info, logout_button
from utils.progress_indicator import (
    initialize_progress,
    update_progress,
    display_progress_bar,
    complete_progress,
    get_stage_names
)
from utils.file_parser import (
    parse_resume_file,
    FileParsingError,
    FileValidationError,
    MAX_FILE_SIZE_BYTES
)
from utils.text_processor import (
    load_spacy_model,
    process_resume_text,
    extract_jd_keywords
)
from utils.skill_validator import (
    load_embedder,
    validate_skills_with_projects,
    generate_validation_feedback
)
from utils.experience_analyzer import (
    analyze_experience_section,
    get_default_experience_results
)
from utils.location_detector import (
    detect_location_info,
    generate_location_feedback
)
from utils.scorer import (
    calculate_overall_score,
    generate_strengths,
    generate_critical_issues,
    generate_improvements
)
from utils.jd_comparator import compare_resume_with_jd
from utils.results_dashboard import (
    display_results_dashboard,
    get_score_color,
    generate_recommendations
)
from utils.report_generator import (
    generate_pdf_report,
    generate_action_items_checklist,
    generate_summary_text
)
from utils.error_handler import (
    log_error,
    log_warning,
    log_info,
    ErrorCategory,
    get_user_friendly_message,
    get_error_suggestions,
    get_default_grammar_results,
    get_default_location_results,
    get_default_skill_validation_results,
    get_default_jd_comparison_results,
    AnalysisResult,
    format_error_for_display
)
from utils.database import save_analysis_to_db


def save_to_history(results: dict, filename: str):
    """Save analysis results to database (with session fallback)."""
    save_analysis_to_db(results, filename)


# Configure page
st.set_page_config(
    page_title="ATS Scorer - Analysis",
    page_icon="🎯",
    layout="wide"
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

# Additional page-specific CSS for analysis page
st.markdown("""
<style>
    /* Analysis page specific styles */
    .analysis-header {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2);
    }
    
    .upload-section {
        background: #f8fafc;
        border: 2px dashed #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #4F46E5;
        background: #f0f4ff;
    }
    
    .results-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .results-card:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Score display enhancements */
    .score-display {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem;
        border-radius: 12px;
        animation: scaleIn 0.5s ease-out;
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Progress indicator enhancements */
    .progress-stage {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        background: #f0f4ff;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .progress-stage-icon {
        font-size: 1.5rem;
    }
    
    .progress-stage-text {
        font-weight: 500;
        color: #1e293b;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .analysis-header {
            padding: 1rem;
        }
        .upload-section {
            padding: 1.5rem;
        }
        .score-display {
            font-size: 2.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Require authentication for this page
# Requirements: 2.1 - Unauthenticated access protection
require_authentication("Please log in to access the ATS Resume Scorer.")

# Page Header
st.title("🎯 ATS Resume Scorer")
st.markdown("Upload your resume and optionally a job description for comprehensive analysis.")

# Display user info and logout in sidebar
# Requirements: 2.3 - Session information display
# Requirements: 2.4 - Logout functionality
with st.sidebar:
    st.markdown("## 👤 User Profile")
    display_user_info(location='sidebar')
    logout_button(location='sidebar')
    
    st.markdown("---")
    
    st.markdown("## 📊 Analysis Options")
    st.info("""
    **General ATS Score**: Upload resume only for overall ATS compatibility analysis.
    
    **JD Comparison**: Upload both resume and job description for targeted optimization.
    """)

# Main content area
st.markdown("---")

# Mode Selection
analysis_mode = st.radio(
    "Select Analysis Mode:",
    ["General ATS Score", "Job Description Comparison"],
    horizontal=True
)

st.markdown("---")

# File Upload Section
col1, col2 = st.columns(2)

def clear_previous_results():
    """Clear previous analysis results when a new file is uploaded."""
    if 'analysis_results' in st.session_state:
        del st.session_state['analysis_results']
    if 'analysis_complete' in st.session_state:
        del st.session_state['analysis_complete']
    if 'download_data' in st.session_state:
        del st.session_state['download_data']

with col1:
    st.markdown("### 📄 Upload Resume")
    resume_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'doc', 'docx'],
        help="Supported formats: PDF, DOC, DOCX (Max 5MB)",
        key="resume_upload",
        on_change=clear_previous_results
    )
    
    if resume_file:
        st.success(f"✅ Resume uploaded: {resume_file.name}")
        st.info(f"File size: {resume_file.size / 1024:.2f} KB")

jd_file = None
jd_text_input = None

with col2:
    if analysis_mode == "Job Description Comparison":
        st.markdown("### 📋 Upload Job Description")
        jd_input_method = st.radio(
            "Input method:",
            ["Upload File", "Paste Text"],
            horizontal=True,
            key="jd_input_method"
        )
        
        if jd_input_method == "Upload File":
            jd_file = st.file_uploader(
                "Choose job description file",
                type=['pdf', 'doc', 'docx', 'txt'],
                help="Supported formats: PDF, DOC, DOCX, TXT (Max 5MB)",
                key="jd_upload"
            )
            
            if jd_file:
                st.success(f"✅ Job Description uploaded: {jd_file.name}")
                st.info(f"File size: {jd_file.size / 1024:.2f} KB")
        else:
            jd_text_input = st.text_area(
                "Paste job description text:",
                height=200,
                placeholder="Paste the job description here...",
                key="jd_text"
            )
            if jd_text_input:
                st.success(f"✅ Job Description provided ({len(jd_text_input)} characters)")
    else:
        st.markdown("### 📋 Job Description")
        st.info("Job description comparison is not selected. Switch to 'Job Description Comparison' mode to enable this feature.")

st.markdown("---")


def run_analysis(resume_file, jd_file=None, jd_text=None, analysis_mode="General ATS Score"):
    """
    Run the complete resume analysis pipeline with comprehensive error handling.
    
    Args:
        resume_file: Uploaded resume file
        jd_file: Optional uploaded job description file
        jd_text: Optional job description text
        analysis_mode: Analysis mode selected
        
    Returns:
        Dictionary containing all analysis results
        
    Validates:
        - Requirements 15.1: Clear validation error messages
        - Requirements 15.2: Fallback extraction attempts
        - Requirements 15.3: Graceful degradation for component failures
        - Requirements 15.4: User-friendly error messages without stack traces
        - Requirements 15.5: Model load error guidance
    """
    results = {
        'success': False,
        'error': None,
        'error_suggestions': [],
        'warnings': [],
        'resume_text': None,
        'resume_metadata': None,
        'processed_data': None,
        'skill_validation': None,
        'grammar_results': None,
        'location_results': None,
        'scores': None,
        'jd_comparison': None,
        'component_status': {}
    }
    
    log_info(f"Starting analysis for file: {resume_file.name}", context="run_analysis")
    
    try:
        # Stage 1: File Validation
        # Requirements: 3.1, 3.2 - File type and size validation
        update_progress("File Validation")
        
        # Read file data
        try:
            file_data = resume_file.read()
            resume_file.seek(0)  # Reset file pointer
        except Exception as e:
            log_error(e, context="file_read", category=ErrorCategory.FILE_UPLOAD)
            raise FileValidationError("Could not read the uploaded file. Please try uploading again.")
        
        # Validate and extract text
        # Requirements: 3.3, 3.4 - Text extraction from PDF/DOCX
        # Requirements: 3.5, 15.1, 15.2 - Error handling with fallback
        resume_text, resume_metadata = parse_resume_file(file_data, resume_file.name)
        results['resume_text'] = resume_text
        results['resume_metadata'] = resume_metadata
        results['component_status']['file_parsing'] = 'success'
        
        # Stage 2: Text Extraction (already done, update progress)
        update_progress("Text Extraction")
        
        # Load models (cached)
        # Requirements: 14.1, 14.2, 14.3, 14.4 - Local model loading and caching
        try:
            nlp = load_spacy_model()
            results['component_status']['nlp_model'] = 'success'
        except Exception as e:
            log_error(e, context="load_spacy_model", category=ErrorCategory.MODEL_LOADING)
            raise  # NLP model is critical, cannot continue without it
        
        try:
            embedder = load_embedder()
            results['component_status']['embedder_model'] = 'success'
        except Exception as e:
            log_error(e, context="load_embedder", category=ErrorCategory.MODEL_LOADING)
            raise  # Embedder is critical for skill validation
        
        # Stage 3: NLP Processing
        # Requirements: 5.1-5.6 - Section and information extraction
        update_progress("NLP Processing")
        try:
            processed_data = process_resume_text(resume_text, nlp)
            results['processed_data'] = processed_data
            results['component_status']['nlp_processing'] = 'success'
        except Exception as e:
            log_error(e, context="process_resume_text", category=ErrorCategory.NLP_PROCESSING)
            raise  # NLP processing is critical
        
        # Stage 4: Skill Validation
        # Requirements: 6.1-6.6 - Skill validation against projects
        update_progress("Skill Validation")
        try:
            skill_validation = validate_skills_with_projects(
                skills=processed_data['skills'],
                projects=processed_data['projects'],
                experience=processed_data['sections'].get('experience', ''),
                embedder=embedder
            )
            results['skill_validation'] = skill_validation
            results['component_status']['skill_validation'] = 'success'
        except Exception as e:
            # Requirements: 15.3 - Graceful degradation
            log_error(e, context="skill_validation", category=ErrorCategory.SKILL_VALIDATION)
            results['warnings'].append("Skill validation encountered an issue. Using default values.")
            skill_validation = get_default_skill_validation_results()
            results['skill_validation'] = skill_validation
            results['component_status']['skill_validation'] = 'degraded'
        
        # Stage 5: Experience Analysis (replaced grammar check)
        update_progress("Experience Analysis")
        try:
            experience_results = analyze_experience_section(
                experience_text=processed_data['sections'].get('experience', ''),
                action_verbs=processed_data['action_verbs'],
                full_text=resume_text
            )
            results['experience_results'] = experience_results
            results['component_status']['experience_analysis'] = 'success'
        except Exception as e:
            log_error(e, context="experience_analysis", category=ErrorCategory.NLP_PROCESSING)
            results['warnings'].append("Experience analysis encountered an issue. Using default values.")
            experience_results = get_default_experience_results()
            results['experience_results'] = experience_results
            results['component_status']['experience_analysis'] = 'degraded'
        
        # Use default grammar results (grammar check disabled)
        grammar_results = get_default_grammar_results()
        results['grammar_results'] = grammar_results
        
        # Stage 6: Location Detection
        # Requirements: 8.1-8.6 - Location privacy detection
        update_progress("Location Detection")
        try:
            location_results = detect_location_info(resume_text, nlp)
            results['component_status']['location_detection'] = 'success'
        except Exception as e:
            # Requirements: 15.3 - Graceful degradation
            log_error(e, context="location_detection", category=ErrorCategory.LOCATION_DETECTION)
            results['warnings'].append("Location detection encountered an issue. Using default values.")
            location_results = get_default_location_results()
            results['component_status']['location_detection'] = 'degraded'
        results['location_results'] = location_results
        
        # Process JD if provided
        jd_keywords = None
        jd_comparison = None
        
        if analysis_mode == "Job Description Comparison":
            jd_text_content = None
            
            if jd_file:
                # Extract text from JD file
                try:
                    jd_data = jd_file.read()
                    jd_file.seek(0)
                    
                    # Handle TXT files differently
                    if jd_file.name.lower().endswith('.txt'):
                        jd_text_content = jd_data.decode('utf-8', errors='ignore')
                    else:
                        jd_text_content, _ = parse_resume_file(jd_data, jd_file.name)
                except Exception as e:
                    log_warning(f"Could not parse JD file: {str(e)}", context="jd_parsing")
                    results['warnings'].append(f"Could not parse job description file. Skipping JD comparison.")
            elif jd_text:
                jd_text_content = jd_text
            
            if jd_text_content:
                try:
                    # Extract JD keywords
                    jd_keywords = extract_jd_keywords(jd_text_content, nlp)
                    
                    # Compare resume with JD
                    # Requirements: 10.1-10.5 - JD comparison
                    jd_comparison = compare_resume_with_jd(
                        resume_text=resume_text,
                        resume_keywords=processed_data['keywords'],
                        resume_skills=processed_data['skills'],
                        jd_text=jd_text_content,
                        jd_keywords=jd_keywords,
                        embedder=embedder,
                        nlp=nlp
                    )
                    results['jd_comparison'] = jd_comparison
                    results['component_status']['jd_comparison'] = 'success'
                except Exception as e:
                    log_error(e, context="jd_comparison", category=ErrorCategory.JD_COMPARISON)
                    results['warnings'].append("Job description comparison encountered an issue.")
                    jd_comparison = get_default_jd_comparison_results()
                    results['jd_comparison'] = jd_comparison
                    results['component_status']['jd_comparison'] = 'degraded'
        
        # Stage 7: Score Calculation
        # Requirements: 9.1-9.7 - Score calculation
        update_progress("Score Calculation")
        try:
            scores = calculate_overall_score(
                text=resume_text,
                sections=processed_data['sections'],
                skills=processed_data['skills'],
                keywords=processed_data['keywords'],
                action_verbs=processed_data['action_verbs'],
                skill_validation_results=skill_validation,
                grammar_results=grammar_results,
                location_results=location_results,
                jd_keywords=jd_keywords
            )
            results['scores'] = scores
            results['component_status']['scoring'] = 'success'
        except Exception as e:
            log_error(e, context="score_calculation", category=ErrorCategory.SCORING)
            raise  # Scoring is critical
        
        # Stage 8: Generating Results
        update_progress("Generating Results")
        
        # Generate feedback (with error handling for each)
        try:
            results['strengths'] = generate_strengths(scores, skill_validation, grammar_results)
        except Exception as e:
            log_warning(f"Could not generate strengths: {str(e)}", context="generate_strengths")
            results['strengths'] = ["Analysis complete. See detailed results below."]
        
        try:
            results['critical_issues'] = generate_critical_issues(scores, grammar_results, location_results)
        except Exception as e:
            log_warning(f"Could not generate critical issues: {str(e)}", context="generate_critical_issues")
            results['critical_issues'] = []
        
        try:
            results['improvements'] = generate_improvements(scores, skill_validation)
        except Exception as e:
            log_warning(f"Could not generate improvements: {str(e)}", context="generate_improvements")
            results['improvements'] = []
        
        try:
            results['skill_feedback'] = generate_validation_feedback(skill_validation)
        except Exception as e:
            log_warning(f"Could not generate skill feedback: {str(e)}", context="generate_skill_feedback")
            results['skill_feedback'] = []
        
        try:
            results['location_feedback'] = generate_location_feedback(location_results)
        except Exception as e:
            log_warning(f"Could not generate location feedback: {str(e)}", context="generate_location_feedback")
            results['location_feedback'] = []
        
        # Mark analysis as successful
        results['success'] = True
        log_info("Analysis completed successfully", context="run_analysis")
        
    except FileValidationError as e:
        log_error(e, context="file_validation", category=ErrorCategory.FILE_UPLOAD)
        results['error'] = str(e)
        results['error_suggestions'] = get_error_suggestions(e, ErrorCategory.FILE_UPLOAD)
    except FileParsingError as e:
        log_error(e, context="file_parsing", category=ErrorCategory.FILE_PARSING)
        results['error'] = str(e)
        results['error_suggestions'] = get_error_suggestions(e, ErrorCategory.FILE_PARSING)
    except Exception as e:
        log_error(e, context="unexpected_error", category=ErrorCategory.UNKNOWN)
        results['error'] = get_user_friendly_message(e, ErrorCategory.UNKNOWN)
        results['error_suggestions'] = get_error_suggestions(e, ErrorCategory.UNKNOWN)
    
    return results


def display_results(results):
    """
    Display analysis results in the UI using the results dashboard module.
    
    Requirements: 11.1, 11.2
    
    Args:
        results: Complete analysis results dictionary
    """
    # Use the new comprehensive results dashboard
    display_results_dashboard(results)
    
    st.markdown("---")
    
    # Detailed Analysis Sections (kept for backward compatibility and additional details)
    st.markdown("### 🔍 Detailed Analysis")
    
    with st.expander("🎯 Skill Validation Details", expanded=False):
        skill_validation = results['skill_validation']
        
        # Validated skills
        # Requirements: 11.3 - Display validated skills with project names
        if skill_validation['validated_skills']:
            st.markdown("**✅ Validated Skills:**")
            for skill_info in skill_validation['validated_skills']:
                projects = ", ".join(skill_info['projects'][:3])
                similarity = skill_info.get('similarity', 0) * 100
                st.markdown(f"- **{skill_info['skill']}** ({similarity:.0f}% match) - demonstrated in: {projects}")
        
        # Unvalidated skills
        # Requirements: 11.4 - Display unvalidated skills with warnings
        if skill_validation['unvalidated_skills']:
            st.markdown("**⚠️ Unvalidated Skills:**")
            for skill in skill_validation['unvalidated_skills']:
                st.markdown(f"- ❌ {skill} - not found in projects or experience")
        
        # Feedback
        st.markdown("---")
        for feedback in results['skill_feedback']:
            st.markdown(feedback)
    
    with st.expander("�  Experience Section Analysis", expanded=False):
        experience_results = results.get('experience_results', {})
        metrics = experience_results.get('metrics', {})
        
        # Display experience score
        exp_score = experience_results.get('score', 0)
        max_score = experience_results.get('max_score', 20)
        st.markdown(f"**Experience Score:** {exp_score:.1f} / {max_score}")
        st.progress(exp_score / max_score)
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Job Entries", metrics.get('total_jobs', 0))
            st.metric("With Dates", metrics.get('jobs_with_dates', 0))
            st.metric("With Bullets", metrics.get('jobs_with_bullets', 0))
        with col2:
            st.metric("Quantified Achievements", metrics.get('quantified_achievements', 0))
            st.metric("Action Verbs Used", metrics.get('action_verbs_used', 0))
            st.metric("Jobs with Metrics", metrics.get('jobs_with_metrics', 0))
        
        # Strengths
        if experience_results.get('strengths'):
            st.markdown("**Strengths:**")
            for strength in experience_results['strengths']:
                st.markdown(f"- {strength}")
        
        # Improvements
        if experience_results.get('improvements'):
            st.markdown("**Areas for Improvement:**")
            for improvement in experience_results['improvements']:
                st.markdown(f"- {improvement}")
        
        # Feedback
        st.markdown("---")
        for feedback in experience_results.get('feedback', []):
            st.markdown(feedback)
    
    with st.expander("📍 Privacy & Location Details", expanded=False):
        location_results = results['location_results']
        
        # Requirements: 11.6 - Display privacy alert
        risk_colors = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢',
            'none': '✅'
        }
        risk_icon = risk_colors.get(location_results['privacy_risk'], '⚪')
        st.markdown(f"**Privacy Risk Level:** {risk_icon} {location_results['privacy_risk'].upper()}")
        
        if location_results['detected_locations']:
            st.markdown("**Detected Locations:**")
            for loc in location_results['detected_locations'][:5]:
                st.markdown(f"- {loc['text']} ({loc['type']}) in {loc['section']}")
        
        # Recommendations
        st.markdown("---")
        for feedback in results['location_feedback']:
            st.markdown(feedback)
    
    # JD Comparison (if available)
    # Requirements: 11.7 - Display JD comparison results
    if results['jd_comparison']:
        with st.expander("🎯 Job Description Match Analysis", expanded=True):
            jd_comp = results['jd_comparison']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Match Percentage", f"{jd_comp['match_percentage']:.0f}%")
                st.progress(jd_comp['match_percentage'] / 100.0)
                
                st.metric("Semantic Similarity", f"{jd_comp['semantic_similarity']*100:.0f}%")
                st.progress(jd_comp['semantic_similarity'])
            
            with col2:
                st.markdown("**✅ Matched Keywords:**")
                if jd_comp['matched_keywords']:
                    st.markdown(", ".join(jd_comp['matched_keywords'][:15]))
                else:
                    st.markdown("*No matching keywords found*")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**❌ Missing Keywords:**")
                if jd_comp['missing_keywords']:
                    for kw in jd_comp['missing_keywords'][:10]:
                        st.markdown(f"- {kw}")
                else:
                    st.markdown("*All key terms are present!*")
            
            with col2:
                st.markdown("**📊 Skills Gap:**")
                if jd_comp['skills_gap']:
                    for skill in jd_comp['skills_gap'][:10]:
                        st.markdown(f"- {skill}")
                else:
                    st.markdown("*No significant skills gap detected*")
    
    st.markdown("---")
    
    # Export Options
    # Requirements: 13.1, 13.2, 13.3, 13.4 - Report generation and download
    st.markdown("### 📥 Export Results")
    
    scores = results['scores']
    overall_score = scores['overall_score']
    
    # Pre-generate all download data to avoid regeneration on rerun
    # Store in session state if not already there
    if 'download_data' not in st.session_state:
        st.session_state['download_data'] = {}
    
    # Generate PDF bytes
    try:
        if 'pdf_bytes' not in st.session_state['download_data']:
            st.session_state['download_data']['pdf_bytes'] = generate_pdf_report(results)
        pdf_bytes = st.session_state['download_data']['pdf_bytes']
        pdf_available = True
    except Exception as e:
        pdf_available = False
        print(f"PDF generation error: {e}")
    
    # Generate summary text
    if 'summary_text' not in st.session_state['download_data']:
        st.session_state['download_data']['summary_text'] = generate_summary_text(results)
    summary_text = st.session_state['download_data']['summary_text']
    
    # Generate action checklist
    if 'action_checklist' not in st.session_state['download_data']:
        st.session_state['download_data']['action_checklist'] = generate_action_items_checklist(results)
    action_checklist = st.session_state['download_data']['action_checklist']
    
    # Generate quick actions
    if 'quick_actions' not in st.session_state['download_data']:
        action_items = []
        for error in results['grammar_results'].get('critical_errors', [])[:2]:
            action_items.append(("Critical", f"Fix: {error['message'][:100]}"))
        if results['location_results']['privacy_risk'] == 'high':
            action_items.append(("Critical", "Remove detailed location information from resume"))
        for skill in results['skill_validation'].get('unvalidated_skills', [])[:2]:
            action_items.append(("High", f"Add project evidence for skill: {skill}"))
        if results['jd_comparison']:
            for kw in results['jd_comparison'].get('missing_keywords', [])[:2]:
                action_items.append(("Medium", f"Consider adding keyword: {kw}"))
        
        action_text = "ATS Resume Quick Actions\n" + "=" * 25 + "\n\n"
        action_text += "\n".join([f"[{p}] {i}" for p, i in action_items])
        st.session_state['download_data']['quick_actions'] = action_text
    quick_actions_text = st.session_state['download_data']['quick_actions']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # PDF Report Download
        if pdf_available:
            st.download_button(
                "📑 Download PDF Report",
                data=pdf_bytes,
                file_name="ats_resume_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                key="download_pdf_report"
            )
        else:
            st.warning("PDF generation unavailable")
    
    with col2:
        # Summary text download
        st.download_button(
            "📄 Download Summary",
            data=summary_text,
            file_name="ats_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_summary"
        )
    
    with col3:
        # Action items checklist download
        st.download_button(
            "📋 Download Checklist",
            data=action_checklist,
            file_name="action_items_checklist.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_checklist"
        )
    
    with col4:
        # Quick action items
        st.download_button(
            "⚡ Quick Actions",
            data=quick_actions_text,
            file_name="quick_actions.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_quick_actions"
        )


# Check if we have previous results to display (for download button reruns)
has_previous_results = 'analysis_results' in st.session_state and st.session_state.get('analysis_complete')

# Analysis Button
if resume_file:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze Resume", use_container_width=True, type="primary"):
            # Clear any previous download data for fresh analysis
            if 'download_data' in st.session_state:
                del st.session_state['download_data']
            
            # Initialize progress tracking
            # Requirements: 4.1 - Progress initialization at zero percent
            initialize_progress()
            
            # Display progress bar
            # Requirements: 4.1, 4.2, 4.4 - Progress display with stage information
            progress_bar, status_text, percent_text = display_progress_bar()
            
            # Create a placeholder for dynamic updates
            progress_placeholder = st.empty()
            
            # Run analysis with progress updates
            with progress_placeholder.container():
                # Run the analysis
                results = run_analysis(
                    resume_file=resume_file,
                    jd_file=jd_file,
                    jd_text=jd_text_input,
                    analysis_mode=analysis_mode
                )
            
            # Mark as complete
            # Requirements: 4.3 - Progress completion at one hundred percent
            complete_progress()
            progress_bar.progress(1.0)
            percent_text.markdown(
                "<div style='text-align: center; color: #666;'>100%</div>",
                unsafe_allow_html=True
            )
            
            import time
            time.sleep(0.3)
            
            # Clear progress indicators
            status_text.empty()
            progress_bar.empty()
            percent_text.empty()
            progress_placeholder.empty()
            
            # Display results or error
            if results['success']:
                st.success("✅ Analysis complete!")
                # Store results in session state for persistence across reruns
                st.session_state['analysis_results'] = results
                st.session_state['analysis_complete'] = True
                
                # Save to analysis history
                save_to_history(results, resume_file.name)
                
                display_results(results)
            else:
                # Requirements: 15.4 - User-friendly error messages
                st.error(f"❌ {results['error']}")
                st.info("Please check your file and try again. If the problem persists, try converting your resume to a different format (PDF or DOCX).")
        
        # Display previous results if available (persists across reruns for downloads)
        elif has_previous_results:
            st.success("✅ Analysis results ready")
            display_results(st.session_state['analysis_results'])

# Display previous results even without file (edge case)
elif has_previous_results:
    st.success("✅ Analysis results (upload a new file to re-analyze)")
    display_results(st.session_state['analysis_results'])

else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload your resume to begin the analysis.")
    
    st.markdown("### 📝 Tips for Best Results")
    st.markdown("""
    - **File Format**: Use PDF or DOCX for best text extraction
    - **File Size**: Keep your resume under 5MB
    - **Content**: Include clear sections (Experience, Education, Skills, Projects)
    - **Skills**: List your skills and demonstrate them in project descriptions
    - **Job Description**: Upload a JD for targeted optimization recommendations
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>All analysis is performed locally on your machine. Your data never leaves your system.</p>
</div>
""", unsafe_allow_html=True)
