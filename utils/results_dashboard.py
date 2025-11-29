"""
Results Dashboard Module for ATS Resume Scorer

This module provides functions to display comprehensive analysis results
with expandable sections, color-coded scores, and actionable recommendations.

Requirements: 11.1, 11.2
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple


def get_score_color(score: float) -> Tuple[str, str]:
    """
    Get color based on score value.
    
    Requirements: 11.1 - Score color coding (red < 60, yellow 60-79, green ≥ 80)
    
    Args:
        score: Overall score (0-100)
        
    Returns:
        Tuple of (text_color, background_color)
    """
    if score >= 80:
        return "#2e7d32", "#e8f5e9"  # Green
    elif score >= 60:
        return "#f57c00", "#fff3e0"  # Yellow/Orange
    else:
        return "#c62828", "#ffebee"  # Red


def get_score_emoji(score: float) -> str:
    """Get emoji based on score value."""
    if score >= 90:
        return "🌟"
    elif score >= 80:
        return "✅"
    elif score >= 70:
        return "👍"
    elif score >= 60:
        return "⚠️"
    elif score >= 50:
        return "❌"
    else:
        return "🔴"


def display_overall_score(scores: Dict) -> None:
    """
    Display the overall score with color coding.
    
    Requirements: 11.1 - Overall score display with color coding
    
    Args:
        scores: Dictionary containing score results
    """
    overall_score = scores['overall_score']
    text_color, bg_color = get_score_color(overall_score)
    emoji = get_score_emoji(overall_score)
    
    st.markdown("## 📊 Analysis Results")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background-color: {bg_color}; 
                    border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="color: {text_color}; font-size: 4.5rem; margin: 0; font-weight: bold;">
                {emoji} {overall_score:.0f}
            </h1>
            <h3 style="color: {text_color}; margin: 0.5rem 0;">Overall ATS Score</h3>
            <p style="color: #666; margin-top: 0.5rem;">{scores['overall_interpretation']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display penalties and bonuses if any
    if scores.get('penalties') or scores.get('bonuses'):
        with col2:
            st.markdown("")
            if scores.get('bonuses'):
                bonus_text = ", ".join([f"+{v:.0f} ({k.replace('_', ' ')})" 
                                       for k, v in scores['bonuses'].items()])
                st.success(f"🎁 Bonuses applied: {bonus_text}")
            if scores.get('penalties'):
                penalty_text = ", ".join([f"-{v:.0f} ({k.replace('_', ' ')})" 
                                         for k, v in scores['penalties'].items()])
                st.warning(f"⚠️ Penalties applied: {penalty_text}")


def display_score_breakdown(scores: Dict) -> None:
    """
    Display score breakdown with progress bars for all 5 components.
    
    Requirements: 11.2 - Component score display with progress bars
    
    Args:
        scores: Dictionary containing score results
    """
    st.markdown("### 📈 Score Breakdown")
    
    # Component definitions with max scores
    components = [
        ("Formatting", "formatting_score", 20, "📝"),
        ("Keywords & Skills", "keywords_score", 25, "🔑"),
        ("Content Quality", "content_score", 25, "📄"),
        ("Skill Validation", "skill_validation_score", 15, "✅"),
        ("ATS Compatibility", "ats_compatibility_score", 15, "🤖"),
    ]
    
    col1, col2 = st.columns(2)
    
    for i, (name, key, max_score, icon) in enumerate(components):
        score = scores[key]
        percentage = score / max_score
        message = scores['component_messages'].get(key.replace('_score', ''), '')
        
        # Determine color based on percentage
        if percentage >= 0.8:
            color = "green"
        elif percentage >= 0.6:
            color = "orange"
        else:
            color = "red"
        
        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"**{icon} {name}**")
            
            # Custom progress bar with color
            progress_html = f"""
            <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px; margin-bottom: 5px;">
                <div style="background-color: {color}; width: {percentage*100}%; height: 100%; 
                            border-radius: 10px; transition: width 0.5s ease-in-out;"></div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
            st.markdown(f"**{score:.0f}/{max_score}** - {message}")
            st.markdown("")




def display_strengths_section(strengths: List[str], scores: Dict, 
                              skill_validation: Dict, grammar_results: Dict) -> None:
    """
    Display strengths section with expandable details.
    
    Args:
        strengths: List of strength messages
        scores: Score results dictionary
        skill_validation: Skill validation results
        grammar_results: Grammar check results
    """
    st.markdown("### 💪 Strengths")
    
    if not strengths:
        st.info("Keep improving your resume to unlock strengths!")
        return
    
    # Main strengths display
    for strength in strengths:
        st.markdown(f"- {strength}")
    
    # Expandable details
    with st.expander("📋 View Detailed Strength Analysis", expanded=False):
        st.markdown("#### Detailed Breakdown")
        
        # Formatting details
        if scores['formatting_score'] >= 16:
            st.markdown("**📝 Formatting Excellence:**")
            st.markdown("""
            - Clear section headers detected
            - Good use of bullet points
            - Well-organized structure
            - Appropriate content length
            """)
        
        # Keywords details
        if scores['keywords_score'] >= 20:
            st.markdown("**🔑 Keyword Optimization:**")
            st.markdown("""
            - Strong presence of relevant keywords
            - Good variety of technical skills
            - Industry-appropriate terminology
            """)
        
        # Content details
        if scores['content_score'] >= 20:
            st.markdown("**📄 Content Quality:**")
            st.markdown("""
            - Effective use of action verbs
            - Quantifiable achievements present
            - Professional language throughout
            """)
        
        # Skill validation details
        if scores['skill_validation_score'] >= 12:
            validated = skill_validation.get('validated_skills', [])
            st.markdown(f"**✅ Skill Validation ({len(validated)} skills validated):**")
            for skill_info in validated[:5]:
                projects = ", ".join(skill_info.get('projects', [])[:2])
                st.markdown(f"- **{skill_info['skill']}**: demonstrated in {projects}")
        
        # Grammar details
        if grammar_results.get('total_errors', 0) == 0:
            st.markdown("**✨ Grammar & Spelling:**")
            st.markdown("- No errors detected - excellent proofreading!")


def display_critical_issues_section(critical_issues: List[str], scores: Dict,
                                    grammar_results: Dict, location_results: Dict) -> None:
    """
    Display critical issues section with expandable details.
    
    Args:
        critical_issues: List of critical issue messages
        scores: Score results dictionary
        grammar_results: Grammar check results
        location_results: Location detection results
    """
    if not critical_issues:
        st.success("### ✅ No Critical Issues Found!")
        st.markdown("Your resume doesn't have any critical issues that need immediate attention.")
        return
    
    st.markdown("### 🚨 Critical Issues")
    st.error("These issues should be addressed immediately for better ATS performance.")
    
    # Main issues display
    for issue in critical_issues:
        st.markdown(f"- {issue}")
    
    # Expandable details
    with st.expander("🔍 View Detailed Issue Analysis", expanded=False):
        st.markdown("#### Issue Details & Solutions")
        
        # Grammar critical errors
        critical_errors = grammar_results.get('critical_errors', [])
        if critical_errors:
            st.markdown("**🔴 Critical Grammar/Spelling Errors:**")
            for i, error in enumerate(critical_errors[:5], 1):
                st.markdown(f"**Error {i}:** {error.get('message', 'Unknown error')}")
                if error.get('context'):
                    st.markdown(f"- Context: *\"{error['context']}\"*")
                if error.get('suggestions'):
                    st.markdown(f"- Suggestion: **{error['suggestions'][0]}**")
                st.markdown("")
        
        # Location privacy issues
        if location_results.get('privacy_risk') == 'high':
            st.markdown("**📍 Location Privacy Issues:**")
            detected = location_results.get('detected_locations', [])
            for loc in detected[:5]:
                st.markdown(f"- Found: **{loc['text']}** ({loc['type']}) in {loc['section']}")
            st.markdown("""
            **Why this matters:**
            - Full addresses can lead to discrimination
            - City/State in header is sufficient
            - Detailed location info is unnecessary for most jobs
            """)
        
        # Low formatting score
        if scores['formatting_score'] < 10:
            st.markdown("**📝 Formatting Issues:**")
            st.markdown("""
            - Missing or unclear section headers
            - Insufficient use of bullet points
            - Poor content organization
            
            **Solution:** Add clear sections (Experience, Education, Skills) with bullet points.
            """)
        
        # Low keywords score
        if scores['keywords_score'] < 12:
            st.markdown("**🔑 Keyword Deficiency:**")
            st.markdown("""
            - Insufficient industry keywords
            - Missing technical skills
            - Limited skill variety
            
            **Solution:** Add relevant keywords from job descriptions in your field.
            """)
        
        # Low skill validation
        if scores['skill_validation_score'] < 7:
            unvalidated = len(skill_validation.get('unvalidated_skills', []) if 'skill_validation' in dir() else [])
            st.markdown("**✅ Skill Validation Issues:**")
            st.markdown("""
            - Listed skills lack supporting evidence
            - Projects don't demonstrate claimed skills
            
            **Solution:** Add project descriptions that showcase your skills, or remove unsubstantiated skills.
            """)


def display_improvements_section(improvements: List[str], scores: Dict,
                                 skill_validation: Dict) -> None:
    """
    Display areas for improvement section with expandable details.
    
    Args:
        improvements: List of improvement suggestions
        scores: Score results dictionary
        skill_validation: Skill validation results
    """
    if not improvements:
        st.success("### 🎉 Excellent Work!")
        st.markdown("Your resume is well-optimized. Focus on maintaining this quality.")
        return
    
    st.markdown("### 📈 Areas for Improvement")
    st.warning("Address these areas to boost your ATS score.")
    
    # Main improvements display
    for improvement in improvements:
        st.markdown(f"- {improvement}")
    
    # Expandable details
    with st.expander("💡 View Improvement Strategies", expanded=False):
        st.markdown("#### Detailed Improvement Guide")
        
        # Formatting improvements
        if 12 <= scores['formatting_score'] < 16:
            st.markdown("**📝 Formatting Improvements:**")
            st.markdown("""
            1. **Add more bullet points** - Aim for 3-5 bullets per job
            2. **Use consistent formatting** - Same font, spacing throughout
            3. **Add section headers** - Make sections clearly identifiable
            4. **Optimize length** - 1-2 pages is ideal
            """)
        
        # Keywords improvements
        if 14 <= scores['keywords_score'] < 20:
            st.markdown("**🔑 Keyword Optimization:**")
            st.markdown("""
            1. **Research job descriptions** - Extract common keywords
            2. **Add technical skills** - Include tools, technologies, methodologies
            3. **Use industry terminology** - Match language used in your field
            4. **Include certifications** - Add relevant credentials
            """)
        
        # Content improvements
        if 14 <= scores['content_score'] < 20:
            st.markdown("**📄 Content Enhancement:**")
            st.markdown("""
            1. **Start bullets with action verbs** - Led, Developed, Implemented, etc.
            2. **Add quantifiable results** - Numbers, percentages, metrics
            3. **Show impact** - "Increased sales by 25%" vs "Improved sales"
            4. **Be specific** - Avoid vague descriptions
            """)
        
        # Skill validation improvements
        if 7 <= scores['skill_validation_score'] < 12:
            unvalidated = skill_validation.get('unvalidated_skills', [])
            st.markdown("**✅ Skill Validation:**")
            st.markdown("Skills that need project evidence:")
            for skill in unvalidated[:5]:
                st.markdown(f"- **{skill}**: Add a project or experience that demonstrates this skill")
        
        # ATS compatibility improvements
        if 9 <= scores['ats_compatibility_score'] < 13:
            st.markdown("**🤖 ATS Compatibility:**")
            st.markdown("""
            1. **Use standard section names** - Experience, Education, Skills
            2. **Avoid tables and columns** - Use simple formatting
            3. **Remove graphics** - ATS can't read images
            4. **Use standard fonts** - Arial, Calibri, Times New Roman
            """)


def display_skill_validation_section(skill_validation: Dict, scores: Dict) -> None:
    """
    Display skill validation analysis section with validated/unvalidated skills.
    
    Requirements: 11.3 - Display validated skills with associated project names
    Requirements: 11.4 - Display unvalidated skills with warning indicators
    
    Args:
        skill_validation: Skill validation results dictionary containing:
            - validated_skills: List of dicts with skill, projects, similarity
            - unvalidated_skills: List of unvalidated skill names
            - validation_percentage: Float 0.0-1.0
            - skill_project_mapping: Dict mapping skills to projects
        scores: Score results dictionary
    """
    st.markdown("### ✅ Skill Validation Analysis")
    
    validated_skills = skill_validation.get('validated_skills', [])
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    validation_percentage = skill_validation.get('validation_percentage', 0.0)
    skill_project_mapping = skill_validation.get('skill_project_mapping', {})
    
    total_skills = len(validated_skills) + len(unvalidated_skills)
    
    # Display validation summary
    if total_skills == 0:
        st.info("No skills detected in your resume. Add a Skills section to get validation feedback.")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Skills",
            value=total_skills
        )
    
    with col2:
        st.metric(
            label="Validated",
            value=len(validated_skills),
            delta=f"{validation_percentage*100:.0f}%"
        )
    
    with col3:
        st.metric(
            label="Unvalidated",
            value=len(unvalidated_skills),
            delta=f"-{len(unvalidated_skills)}" if unvalidated_skills else None,
            delta_color="inverse"
        )
    
    # Validation status indicator
    if validation_percentage >= 0.8:
        st.success(f"🌟 Excellent! {validation_percentage*100:.0f}% of your skills are validated by projects/experience.")
    elif validation_percentage >= 0.6:
        st.info(f"👍 Good! {validation_percentage*100:.0f}% of your skills are validated. Consider adding more project evidence.")
    elif validation_percentage >= 0.4:
        st.warning(f"⚠️ {validation_percentage*100:.0f}% of your skills are validated. Many skills lack supporting evidence.")
    else:
        st.error(f"❌ Only {validation_percentage*100:.0f}% of your skills are validated. Add projects demonstrating your skills.")
    
    # Display validated skills with project names
    # Requirements: 11.3 - Display validated skills with associated project names
    if validated_skills:
        with st.expander(f"✅ Validated Skills ({len(validated_skills)})", expanded=True):
            for skill_info in validated_skills:
                skill_name = skill_info.get('skill', 'Unknown')
                projects = skill_info.get('projects', [])
                similarity = skill_info.get('similarity', 0.0)
                
                # Determine confidence level based on similarity
                if similarity >= 0.9:
                    confidence_icon = "🟢"
                    confidence_text = "High confidence"
                elif similarity >= 0.7:
                    confidence_icon = "🟡"
                    confidence_text = "Medium confidence"
                else:
                    confidence_icon = "🟠"
                    confidence_text = "Low confidence"
                
                # Display skill with projects
                projects_text = ", ".join(projects) if projects else "No specific project"
                st.markdown(f"""
                **{confidence_icon} {skill_name}**
                - Demonstrated in: *{projects_text}*
                - Match confidence: {confidence_text} ({similarity*100:.0f}%)
                """)
    
    # Display unvalidated skills with warning indicators
    # Requirements: 11.4 - Display unvalidated skills with warning indicators
    if unvalidated_skills:
        with st.expander(f"⚠️ Unvalidated Skills ({len(unvalidated_skills)})", expanded=True):
            st.warning("These skills are listed but not demonstrated in your projects or experience.")
            
            for skill in unvalidated_skills:
                st.markdown(f"""
                **⚠️ {skill}**
                - Status: Not found in projects or experience
                - Action: Add a project demonstrating this skill or remove it
                """)
            
            st.markdown("---")
            st.markdown("""
            **💡 Tips to validate your skills:**
            1. Add project descriptions that mention these skills
            2. Include specific examples in your experience section
            3. Remove skills you cannot demonstrate with evidence
            """)
    
    # Display skill-project matrix visualization
    display_skill_project_matrix(skill_validation)
    
    # Display validation feedback messages
    display_validation_feedback(skill_validation)


def display_skill_project_matrix(skill_validation: Dict) -> None:
    """
    Display a skill-project matrix visualization showing which projects demonstrate which skills.
    
    Requirements: 11.3, 11.4 - Skill validation display
    
    Args:
        skill_validation: Skill validation results dictionary
    """
    validated_skills = skill_validation.get('validated_skills', [])
    skill_project_mapping = skill_validation.get('skill_project_mapping', {})
    
    if not validated_skills:
        return
    
    # Collect all unique projects
    all_projects = set()
    for skill_info in validated_skills:
        all_projects.update(skill_info.get('projects', []))
    
    if not all_projects:
        return
    
    with st.expander("📊 Skill-Project Matrix", expanded=False):
        st.markdown("This matrix shows which projects demonstrate each skill:")
        
        # Create matrix header
        projects_list = sorted(list(all_projects))
        
        # Build matrix data
        matrix_data = []
        for skill_info in validated_skills:
            skill_name = skill_info.get('skill', 'Unknown')
            skill_projects = set(skill_info.get('projects', []))
            
            row = {'Skill': skill_name}
            for project in projects_list:
                row[project] = "✅" if project in skill_projects else "—"
            matrix_data.append(row)
        
        # Display as a simple table using markdown
        if matrix_data:
            # Create header row
            header = "| Skill | " + " | ".join(projects_list) + " |"
            separator = "|" + "---|" * (len(projects_list) + 1)
            
            # Create data rows
            rows = []
            for row in matrix_data:
                row_str = f"| {row['Skill']} | " + " | ".join([row.get(p, "—") for p in projects_list]) + " |"
                rows.append(row_str)
            
            # Combine and display
            table_md = header + "\n" + separator + "\n" + "\n".join(rows)
            st.markdown(table_md)
        
        st.markdown("""
        **Legend:**
        - ✅ = Skill demonstrated in project
        - — = Skill not found in project
        """)


def display_validation_feedback(skill_validation: Dict) -> None:
    """
    Generate and display validation feedback messages.
    
    Requirements: 11.3, 11.4 - Skill validation display with feedback
    
    Args:
        skill_validation: Skill validation results dictionary
    """
    validated_skills = skill_validation.get('validated_skills', [])
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    validation_percentage = skill_validation.get('validation_percentage', 0.0)
    
    total_skills = len(validated_skills) + len(unvalidated_skills)
    
    if total_skills == 0:
        return
    
    with st.expander("💬 Validation Feedback", expanded=False):
        feedback_messages = []
        
        # Overall assessment
        if validation_percentage >= 0.8:
            feedback_messages.append(
                "🌟 **Excellent skill validation!** Your resume effectively demonstrates "
                "the skills you've listed through concrete projects and experience."
            )
        elif validation_percentage >= 0.6:
            feedback_messages.append(
                "👍 **Good skill validation.** Most of your skills are backed by evidence, "
                "but there's room for improvement."
            )
        elif validation_percentage >= 0.4:
            feedback_messages.append(
                "⚠️ **Moderate skill validation.** Consider adding more project details "
                "or removing skills that lack supporting evidence."
            )
        else:
            feedback_messages.append(
                "❌ **Low skill validation.** Many skills lack supporting evidence. "
                "Recruiters may question unsubstantiated claims."
            )
        
        # Specific feedback for validated skills
        if validated_skills:
            high_confidence = [s for s in validated_skills if s.get('similarity', 0) >= 0.8]
            if high_confidence:
                skills_text = ", ".join([s['skill'] for s in high_confidence[:3]])
                feedback_messages.append(
                    f"✅ **Strong matches:** {skills_text} are clearly demonstrated in your projects."
                )
        
        # Specific feedback for unvalidated skills
        if unvalidated_skills:
            if len(unvalidated_skills) <= 3:
                skills_text = ", ".join(unvalidated_skills)
                feedback_messages.append(
                    f"⚠️ **Action needed:** Add project evidence for: {skills_text}"
                )
            else:
                feedback_messages.append(
                    f"⚠️ **Action needed:** {len(unvalidated_skills)} skills need project evidence. "
                    "Consider adding relevant projects or removing unsubstantiated skills."
                )
        
        # Impact on score
        skill_score = skill_validation.get('validation_score', 0.0)
        max_score = 15.0
        potential_gain = max_score - skill_score
        
        if potential_gain > 3:
            feedback_messages.append(
                f"📈 **Score impact:** Validating all skills could add up to "
                f"**{potential_gain:.0f} points** to your overall score."
            )
        
        # Display all feedback
        for message in feedback_messages:
            st.markdown(message)
            st.markdown("")


def get_skill_validation_summary(skill_validation: Dict) -> Dict:
    """
    Get a summary of skill validation results for use in other components.
    
    Args:
        skill_validation: Skill validation results dictionary
        
    Returns:
        Dictionary with summary statistics
    """
    validated_skills = skill_validation.get('validated_skills', [])
    unvalidated_skills = skill_validation.get('unvalidated_skills', [])
    validation_percentage = skill_validation.get('validation_percentage', 0.0)
    
    total_skills = len(validated_skills) + len(unvalidated_skills)
    
    # Calculate confidence distribution
    high_confidence = len([s for s in validated_skills if s.get('similarity', 0) >= 0.8])
    medium_confidence = len([s for s in validated_skills if 0.6 <= s.get('similarity', 0) < 0.8])
    
    return {
        'total_skills': total_skills,
        'validated_count': len(validated_skills),
        'unvalidated_count': len(unvalidated_skills),
        'validation_percentage': validation_percentage,
        'high_confidence_count': high_confidence,
        'medium_confidence_count': medium_confidence,
        'has_issues': len(unvalidated_skills) > 0,
        'status': 'excellent' if validation_percentage >= 0.8 else 
                  'good' if validation_percentage >= 0.6 else
                  'moderate' if validation_percentage >= 0.4 else 'poor'
    }


def display_experience_section(experience_results: Dict) -> None:
    """
    Display experience section analysis in results dashboard.
    
    Args:
        experience_results: Experience analysis results dictionary containing:
            - score: Experience score (0-20)
            - max_score: Maximum possible score (20)
            - metrics: Dictionary of experience metrics
            - feedback: List of feedback messages
            - strengths: List of strengths
            - improvements: List of improvement suggestions
    """
    st.markdown("### 💼 Experience Section Analysis")
    
    if not experience_results:
        st.info("Experience analysis not available.")
        return
    
    score = experience_results.get('score', 0)
    max_score = experience_results.get('max_score', 20)
    metrics = experience_results.get('metrics', {})
    
    # Display score with progress bar
    score_pct = (score / max_score) * 100 if max_score > 0 else 0
    
    # Color based on score percentage
    if score_pct >= 80:
        score_color = "#2e7d32"  # Green
    elif score_pct >= 60:
        score_color = "#f57c00"  # Orange
    else:
        score_color = "#c62828"  # Red
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 12px; margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; font-weight: 700; color: {score_color};">{score:.1f} / {max_score}</div>
        <div style="color: #64748b; font-size: 0.9rem;">Experience Score</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(score_pct / 100)
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📋 Job Entries",
            value=metrics.get('total_jobs', 0),
            help="Number of job positions documented"
        )
        st.metric(
            label="📅 With Dates",
            value=metrics.get('jobs_with_dates', 0),
            help="Jobs that include date ranges"
        )
    
    with col2:
        st.metric(
            label="📊 Quantified Achievements",
            value=metrics.get('quantified_achievements', 0),
            help="Numbers, percentages, and metrics found"
        )
        st.metric(
            label="✅ With Bullets",
            value=metrics.get('jobs_with_bullets', 0),
            help="Jobs using bullet points"
        )
    
    with col3:
        st.metric(
            label="💪 Action Verbs",
            value=metrics.get('action_verbs_used', 0),
            help="Strong action verbs in experience"
        )
        st.metric(
            label="📈 With Metrics",
            value=metrics.get('jobs_with_metrics', 0),
            help="Jobs with quantifiable results"
        )
    
    # Status indicator
    if score >= 16:
        st.success("🌟 Excellent experience section! Well-documented with strong details and quantified achievements.")
    elif score >= 12:
        st.info("✅ Good experience section with room for improvement. Consider adding more metrics.")
    elif score >= 8:
        st.warning("⚠️ Experience section needs more detail. Add quantified achievements and action verbs.")
    else:
        st.error("❌ Experience section requires significant improvement. Add job details, dates, and bullet points.")
    
    # Strengths
    strengths = experience_results.get('strengths', [])
    if strengths:
        with st.expander("💪 Strengths", expanded=False):
            for strength in strengths:
                st.markdown(f"- {strength}")
    
    # Improvements
    improvements = experience_results.get('improvements', [])
    if improvements:
        with st.expander("📝 Areas for Improvement", expanded=True):
            for improvement in improvements:
                st.markdown(f"- {improvement}")


# Keep grammar function for backward compatibility but it won't be called
def display_grammar_check_section(grammar_results: Dict, sections: Optional[Dict] = None) -> None:
    """
    Display grammar and spelling analysis section in results dashboard.
    NOTE: This function is deprecated - grammar check has been replaced with experience analysis.
    """
    pass  # No longer used


def display_error_free_sections(grammar_results: Dict, sections: Dict) -> None:
    """
    Display summary of error-free sections in the resume.
    
    Requirements: 11.5 - Create summary metrics (error-free sections)
    
    Args:
        grammar_results: Grammar check results dictionary
        sections: Dictionary of resume sections
    """
    # Analyze which sections have errors based on error context
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors = grammar_results.get('minor_errors', [])
    
    all_errors = critical_errors + moderate_errors + minor_errors
    
    # Define standard sections to check
    standard_sections = ['summary', 'experience', 'education', 'skills', 'projects']
    
    # Track which sections have errors (simplified approach)
    sections_with_errors = set()
    sections_present = set()
    
    for section_name in standard_sections:
        section_content = sections.get(section_name, '')
        if section_content and len(section_content.strip()) > 0:
            sections_present.add(section_name)
            # Check if any error context appears in this section
            for error in all_errors:
                error_text = error.get('error_text', '')
                if error_text and error_text.lower() in section_content.lower():
                    sections_with_errors.add(section_name)
                    break
    
    error_free_sections = sections_present - sections_with_errors
    
    if sections_present:
        with st.expander("📊 Section Analysis", expanded=False):
            st.markdown("**Error distribution across resume sections:**")
            
            for section in standard_sections:
                if section in sections_present:
                    if section in error_free_sections:
                        st.markdown(f"- ✅ **{section.title()}**: Error-free")
                    else:
                        st.markdown(f"- ⚠️ **{section.title()}**: Contains errors")
                else:
                    st.markdown(f"- ➖ **{section.title()}**: Not detected")
            
            # Summary
            if error_free_sections:
                st.success(f"🎉 {len(error_free_sections)} of {len(sections_present)} sections are error-free!")
            else:
                st.warning("Consider reviewing all sections for grammar and spelling.")


def display_errors_by_severity(grammar_results: Dict) -> None:
    """
    Display all errors categorized by severity with correction suggestions.
    
    Requirements: 11.5 - Display all errors categorized by severity with correction suggestions
    
    Args:
        grammar_results: Grammar check results dictionary
    """
    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors = grammar_results.get('minor_errors', [])
    
    # Critical Errors Section
    if critical_errors:
        with st.expander(f"🔴 Critical Errors ({len(critical_errors)})", expanded=True):
            st.markdown("**These errors must be fixed immediately:**")
            st.markdown("*Critical errors include spelling mistakes, subject-verb agreement issues, and wrong word usage.*")
            st.markdown("---")
            
            for i, error in enumerate(critical_errors, 1):
                display_single_error(error, i, "critical")
    
    # Moderate Errors Section
    if moderate_errors:
        with st.expander(f"🟡 Moderate Errors ({len(moderate_errors)})", expanded=False):
            st.markdown("**These errors should be addressed:**")
            st.markdown("*Moderate errors include punctuation issues, capitalization errors, and missing articles.*")
            st.markdown("---")
            
            for i, error in enumerate(moderate_errors, 1):
                display_single_error(error, i, "moderate")
    
    # Minor Errors Section
    if minor_errors:
        with st.expander(f"🟢 Minor Issues ({len(minor_errors)})", expanded=False):
            st.markdown("**Optional improvements for polish:**")
            st.markdown("*Minor issues include style suggestions and formatting improvements.*")
            st.markdown("---")
            
            for i, error in enumerate(minor_errors, 1):
                display_single_error(error, i, "minor")


def display_single_error(error: Dict, index: int, severity: str) -> None:
    """
    Display a single error with its details, context, and suggestions.
    
    Requirements: 11.5 - Show correction suggestions for each error, display error locations and context
    
    Args:
        error: Error detail dictionary
        index: Error number for display
        severity: Error severity level (critical, moderate, minor)
    """
    # Determine icon based on severity
    severity_icons = {
        "critical": "🔴",
        "moderate": "🟡",
        "minor": "🟢"
    }
    icon = severity_icons.get(severity, "⚪")
    
    # Error message
    message = error.get('message', 'Unknown error')
    st.markdown(f"**{icon} Error {index}:** {message}")
    
    # Error text and context
    error_text = error.get('error_text', '')
    context = error.get('context', '')
    
    if error_text:
        st.markdown(f"**Found:** `{error_text}`")
    
    if context:
        # Highlight the error in context
        highlighted_context = context
        if error_text:
            highlighted_context = context.replace(
                error_text, 
                f"**[{error_text}]**"
            )
        st.markdown(f"**Context:** *\"{highlighted_context}\"*")
    
    # Correction suggestions
    suggestions = error.get('suggestions', [])
    if suggestions:
        if len(suggestions) == 1:
            st.markdown(f"**💡 Suggestion:** `{suggestions[0]}`")
        else:
            suggestions_text = ", ".join([f"`{s}`" for s in suggestions[:3]])
            st.markdown(f"**💡 Suggestions:** {suggestions_text}")
    
    # Rule ID for reference (optional, collapsed)
    rule_id = error.get('rule_id', '')
    if rule_id:
        st.caption(f"Rule: {rule_id}")
    
    st.markdown("---")


def display_grammar_penalty_info(grammar_results: Dict) -> None:
    """
    Display information about grammar penalty applied to the score.
    
    Requirements: 11.5 - Grammar check display section
    
    Args:
        grammar_results: Grammar check results dictionary
    """
    penalty = grammar_results.get('penalty_applied', 0)
    critical_count = len(grammar_results.get('critical_errors', []))
    moderate_count = len(grammar_results.get('moderate_errors', []))
    minor_count = len(grammar_results.get('minor_errors', []))
    
    with st.expander("📉 Score Impact", expanded=False):
        st.markdown("**How grammar errors affect your score:**")
        
        # Penalty breakdown
        st.markdown("""
        | Error Type | Count | Penalty per Error | Total |
        |------------|-------|-------------------|-------|
        | 🔴 Critical | {} | -5 points | -{:.1f} |
        | 🟡 Moderate | {} | -2 points | -{:.1f} |
        | 🟢 Minor | {} | -0.5 points | -{:.1f} |
        | **Total** | **{}** | | **-{:.1f}** |
        """.format(
            critical_count, critical_count * 5,
            moderate_count, moderate_count * 2,
            minor_count, minor_count * 0.5,
            critical_count + moderate_count + minor_count,
            min(penalty, 20)
        ))
        
        if penalty >= 20:
            st.warning("⚠️ Maximum penalty of 20 points has been applied.")
        
        st.markdown("""
        **Tips to improve:**
        - Fix all critical errors first (highest impact)
        - Use spell-check tools before uploading
        - Have someone proofread your resume
        - Pay attention to technical terms and proper nouns
        """)


def get_grammar_summary(grammar_results: Dict) -> Dict:
    """
    Get a summary of grammar check results for use in other components.
    
    Args:
        grammar_results: Grammar check results dictionary
        
    Returns:
        Dictionary with summary statistics
    """
    total_errors = grammar_results.get('total_errors', 0)
    critical_count = len(grammar_results.get('critical_errors', []))
    moderate_count = len(grammar_results.get('moderate_errors', []))
    minor_count = len(grammar_results.get('minor_errors', []))
    penalty = grammar_results.get('penalty_applied', 0)
    
    # Determine status
    if total_errors == 0:
        status = 'excellent'
    elif critical_count == 0 and moderate_count <= 2:
        status = 'good'
    elif critical_count <= 2:
        status = 'moderate'
    else:
        status = 'poor'
    
    return {
        'total_errors': total_errors,
        'critical_count': critical_count,
        'moderate_count': moderate_count,
        'minor_count': minor_count,
        'penalty_applied': penalty,
        'has_critical': critical_count > 0,
        'has_issues': total_errors > 0,
        'status': status
    }


def get_privacy_risk_color(risk_level: str) -> Tuple[str, str, str]:
    """
    Get color coding based on privacy risk level.
    
    Requirements: 11.6 - Display privacy alert with color coding based on risk level
    
    Args:
        risk_level: Privacy risk level ("high", "medium", "low", "none")
        
    Returns:
        Tuple of (text_color, background_color, border_color)
    """
    if risk_level == "high":
        return "#c62828", "#ffebee", "#ef5350"  # Red
    elif risk_level == "medium":
        return "#f57c00", "#fff3e0", "#ffb74d"  # Orange
    elif risk_level == "low":
        return "#1976d2", "#e3f2fd", "#64b5f6"  # Blue
    else:  # none
        return "#2e7d32", "#e8f5e9", "#81c784"  # Green


def get_privacy_status_info(risk_level: str) -> Tuple[str, str, str]:
    """
    Get privacy status information based on risk level.
    
    Requirements: 11.6 - Show privacy status (issue detected, warning, optimized)
    
    Args:
        risk_level: Privacy risk level
        
    Returns:
        Tuple of (status_text, status_icon, status_description)
    """
    if risk_level == "high":
        return (
            "Issue Detected",
            "🔴",
            "Your resume contains detailed location information that poses a privacy risk."
        )
    elif risk_level == "medium":
        return (
            "Warning",
            "🟡",
            "Your resume has some location mentions that could be simplified."
        )
    elif risk_level == "low":
        return (
            "Minor Concern",
            "🔵",
            "Your resume has minimal location information, but could be improved."
        )
    else:  # none
        return (
            "Optimized",
            "🟢",
            "Your resume is optimized for privacy with no sensitive location information."
        )


def display_privacy_check_section(location_results: Dict) -> None:
    """
    Display privacy and location check section in results dashboard.
    
    Requirements: 11.6 - Display privacy alert with detected locations and removal recommendations
    
    Args:
        location_results: Location detection results dictionary containing:
            - location_found: bool
            - detected_locations: List of location dictionaries
            - privacy_risk: "high" | "medium" | "low" | "none"
            - recommendations: List of recommendation strings
            - penalty_applied: float (0-5)
    """
    st.markdown("### 📍 Privacy & Location Check")
    
    location_found = location_results.get('location_found', False)
    detected_locations = location_results.get('detected_locations', [])
    privacy_risk = location_results.get('privacy_risk', 'none')
    recommendations = location_results.get('recommendations', [])
    penalty_applied = location_results.get('penalty_applied', 0)
    
    # Get color coding and status info
    text_color, bg_color, border_color = get_privacy_risk_color(privacy_risk)
    status_text, status_icon, status_description = get_privacy_status_info(privacy_risk)
    
    # Display privacy alert with color coding
    # Requirements: 11.6 - Display privacy alert with color coding based on risk level
    st.markdown(f"""
    <div style="padding: 1rem; background-color: {bg_color}; 
                border-left: 4px solid {border_color}; border-radius: 5px; margin-bottom: 1rem;">
        <h4 style="color: {text_color}; margin: 0 0 0.5rem 0;">
            {status_icon} Privacy Status: {status_text}
        </h4>
        <p style="color: #333; margin: 0;">{status_description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Locations Found",
            value=len(detected_locations),
            delta=f"-{penalty_applied:.1f} pts" if penalty_applied > 0 else None,
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="Risk Level",
            value=privacy_risk.title()
        )
    
    with col3:
        st.metric(
            label="Penalty Applied",
            value=f"{penalty_applied:.1f} pts"
        )
    
    # Show privacy status indicator
    # Requirements: 11.6 - Show privacy status (issue detected, warning, optimized)
    if privacy_risk == "none":
        st.success("✅ Excellent! Your resume is optimized for privacy. No sensitive location information detected.")
    elif privacy_risk == "low":
        st.info("🔵 Good! Your resume has minimal location information. Consider the suggestions below for further optimization.")
    elif privacy_risk == "medium":
        st.warning("⚠️ Your resume contains some location information that could be simplified for better privacy.")
    else:  # high
        st.error("🔴 Privacy Alert! Your resume contains detailed location information that should be removed.")
    
    # Display detected locations with section information
    # Requirements: 11.6 - Show detected locations with section information
    if detected_locations:
        display_detected_locations(detected_locations)
    
    # Display removal recommendations
    # Requirements: 11.6 - Display removal recommendations
    if recommendations:
        display_privacy_recommendations(recommendations)
    
    # Display penalty information if applicable
    if penalty_applied > 0:
        display_privacy_penalty_info(location_results)


def display_detected_locations(detected_locations: List[Dict]) -> None:
    """
    Display detected locations with section information.
    
    Requirements: 11.6 - Show detected locations with section information
    
    Args:
        detected_locations: List of detected location dictionaries
    """
    with st.expander(f"📍 Detected Locations ({len(detected_locations)})", expanded=True):
        st.markdown("**The following location information was found in your resume:**")
        st.markdown("---")
        
        # Group locations by type
        addresses = [loc for loc in detected_locations if loc.get('type') == 'address']
        zip_codes = [loc for loc in detected_locations if loc.get('type') == 'zip']
        cities = [loc for loc in detected_locations if loc.get('type') in ['gpe', 'loc', 'city', 'state']]
        
        # Display addresses (highest priority)
        if addresses:
            st.markdown("**🔴 Full Addresses (High Risk):**")
            for loc in addresses:
                section = loc.get('section', 'unknown').replace('_', ' ').title()
                st.markdown(f"""
                - **Found:** `{loc['text']}`
                - **Section:** {section}
                - **Risk:** High - Full addresses should be removed
                """)
                st.markdown("")
        
        # Display zip codes
        if zip_codes:
            st.markdown("**🔴 Zip Codes (High Risk):**")
            for loc in zip_codes:
                section = loc.get('section', 'unknown').replace('_', ' ').title()
                st.markdown(f"""
                - **Found:** `{loc['text']}`
                - **Section:** {section}
                - **Risk:** High - Zip codes reveal precise location
                """)
                st.markdown("")
        
        # Display cities/states
        if cities:
            st.markdown("**🟡 City/State Mentions:**")
            for loc in cities:
                section = loc.get('section', 'unknown').replace('_', ' ').title()
                risk_text = "Acceptable in contact header" if section == "Contact Header" else "Consider removing"
                st.markdown(f"""
                - **Found:** `{loc['text']}`
                - **Section:** {section}
                - **Note:** {risk_text}
                """)
                st.markdown("")
        
        # Summary table
        if len(detected_locations) > 3:
            st.markdown("---")
            st.markdown("**Summary Table:**")
            
            # Create table data
            table_data = []
            for loc in detected_locations:
                table_data.append({
                    'Location': loc.get('text', 'Unknown'),
                    'Type': loc.get('type', 'unknown').upper(),
                    'Section': loc.get('section', 'unknown').replace('_', ' ').title()
                })
            
            # Display as markdown table
            header = "| Location | Type | Section |"
            separator = "|----------|------|---------|"
            rows = [f"| {d['Location']} | {d['Type']} | {d['Section']} |" for d in table_data]
            
            st.markdown(header + "\n" + separator + "\n" + "\n".join(rows))


def display_privacy_recommendations(recommendations: List[str]) -> None:
    """
    Display removal recommendations for location privacy.
    
    Requirements: 11.6 - Display removal recommendations
    
    Args:
        recommendations: List of recommendation strings
    """
    with st.expander("💡 Privacy Recommendations", expanded=True):
        st.markdown("**Actions to improve your resume's privacy:**")
        st.markdown("---")
        
        for rec in recommendations:
            # Handle multi-line recommendations (indented items)
            if rec.startswith("  •"):
                st.markdown(f"    {rec}")
            elif rec.startswith("\n"):
                st.markdown(rec)
            else:
                st.markdown(rec)
        
        st.markdown("---")
        st.markdown("""
        **Why Privacy Matters:**
        - 🔒 Protects against location-based discrimination
        - 📍 City/State in header is sufficient for most applications
        - 🏠 Full addresses are unnecessary and pose security risks
        - 📧 Employers will request address details if needed
        """)


def display_privacy_penalty_info(location_results: Dict) -> None:
    """
    Display information about privacy penalty applied to the score.
    
    Requirements: 11.6 - Privacy check display section
    
    Args:
        location_results: Location detection results dictionary
    """
    penalty = location_results.get('penalty_applied', 0)
    privacy_risk = location_results.get('privacy_risk', 'none')
    detected_locations = location_results.get('detected_locations', [])
    
    with st.expander("📉 Score Impact", expanded=False):
        st.markdown("**How location privacy affects your ATS score:**")
        
        # Count location types
        has_address = any(loc.get('type') == 'address' for loc in detected_locations)
        has_zip = any(loc.get('type') == 'zip' for loc in detected_locations)
        
        # Penalty breakdown
        st.markdown("""
        | Issue | Penalty |
        |-------|---------|
        | Full street address | -4 to -5 points |
        | Zip code | -4 points |
        | Both address and zip | -5 points |
        | Multiple location mentions | -3 points |
        | Few location mentions | -2 points |
        """)
        
        st.markdown(f"**Your penalty:** -{penalty:.1f} points")
        
        if has_address and has_zip:
            st.warning("⚠️ Maximum penalty applied due to both address and zip code.")
        elif has_address:
            st.warning("⚠️ High penalty applied due to full street address.")
        elif has_zip:
            st.warning("⚠️ High penalty applied due to zip code.")
        
        st.markdown("""
        **How to remove the penalty:**
        1. Remove all street addresses from your resume
        2. Remove all zip codes
        3. Keep only "City, State" in your contact header
        4. Remove location details from experience/education sections
        """)


def get_privacy_summary(location_results: Dict) -> Dict:
    """
    Get a summary of privacy check results for use in other components.
    
    Args:
        location_results: Location detection results dictionary
        
    Returns:
        Dictionary with summary statistics
    """
    location_found = location_results.get('location_found', False)
    detected_locations = location_results.get('detected_locations', [])
    privacy_risk = location_results.get('privacy_risk', 'none')
    penalty = location_results.get('penalty_applied', 0)
    
    # Count by type
    address_count = len([loc for loc in detected_locations if loc.get('type') == 'address'])
    zip_count = len([loc for loc in detected_locations if loc.get('type') == 'zip'])
    city_count = len([loc for loc in detected_locations if loc.get('type') in ['gpe', 'loc', 'city', 'state']])
    
    # Determine status
    if privacy_risk == "none":
        status = 'optimized'
    elif privacy_risk == "low":
        status = 'good'
    elif privacy_risk == "medium":
        status = 'warning'
    else:
        status = 'issue_detected'
    
    return {
        'location_found': location_found,
        'total_locations': len(detected_locations),
        'address_count': address_count,
        'zip_count': zip_count,
        'city_count': city_count,
        'privacy_risk': privacy_risk,
        'penalty_applied': penalty,
        'has_high_risk': privacy_risk == 'high',
        'status': status
    }


def display_jd_comparison_section(jd_comparison: Dict) -> None:
    """
    Display job description comparison section with keyword analysis.
    
    Requirements: 11.7 - Display matched keywords, missing keywords, and skills gap analysis
    
    Args:
        jd_comparison: JD comparison results dictionary containing:
            - semantic_similarity: float (0.0-1.0)
            - matched_keywords: List of matched keywords
            - missing_keywords: List of missing keywords
            - skills_gap: List of skills in JD but not in resume
            - match_percentage: float (0-100)
    """
    st.markdown("### 🎯 Job Description Comparison")
    
    semantic_similarity = jd_comparison.get('semantic_similarity', 0.0)
    matched_keywords = jd_comparison.get('matched_keywords', [])
    missing_keywords = jd_comparison.get('missing_keywords', [])
    skills_gap = jd_comparison.get('skills_gap', [])
    match_percentage = jd_comparison.get('match_percentage', 0.0)
    
    # Display match percentage and semantic similarity
    # Requirements: 11.7 - Show match percentage and semantic similarity
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Color code match percentage
        if match_percentage >= 70:
            delta_color = "normal"
        elif match_percentage >= 50:
            delta_color = "off"
        else:
            delta_color = "inverse"
        
        st.metric(
            label="Match Score",
            value=f"{match_percentage:.0f}%",
            help="Overall match between your resume and the job description"
        )
    
    with col2:
        st.metric(
            label="Semantic Similarity",
            value=f"{semantic_similarity*100:.0f}%",
            help="How closely your resume content aligns with the JD"
        )
    
    with col3:
        st.metric(
            label="Matched Keywords",
            value=len(matched_keywords),
            delta=f"+{len(matched_keywords)}" if matched_keywords else None,
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Missing Keywords",
            value=len(missing_keywords),
            delta=f"-{len(missing_keywords)}" if missing_keywords else None,
            delta_color="inverse"
        )
    
    # Status indicator based on match percentage
    if match_percentage >= 80:
        st.success(f"🌟 Excellent match! Your resume is highly aligned with this job description ({match_percentage:.0f}% match).")
    elif match_percentage >= 60:
        st.info(f"👍 Good match! Your resume aligns well with this job description ({match_percentage:.0f}% match). Consider adding missing keywords.")
    elif match_percentage >= 40:
        st.warning(f"⚠️ Moderate match ({match_percentage:.0f}%). Your resume needs optimization for this position.")
    else:
        st.error(f"❌ Low match ({match_percentage:.0f}%). Significant improvements needed to align with this job description.")
    
    # Display matched keywords with visualization
    # Requirements: 11.7 - Display matched keywords with visualization
    if matched_keywords:
        display_matched_keywords(matched_keywords)
    
    # Display missing critical keywords with importance
    # Requirements: 11.7 - Display missing critical keywords with importance
    if missing_keywords:
        display_missing_keywords(missing_keywords)
    
    # Display skills gap analysis
    # Requirements: 11.7 - Display skills gap analysis
    if skills_gap:
        display_skills_gap(skills_gap)
    
    # Display match summary and recommendations
    display_jd_match_summary(jd_comparison)


def display_matched_keywords(matched_keywords: List[str]) -> None:
    """
    Display matched keywords with visualization.
    
    Requirements: 11.7 - Display matched keywords with visualization
    
    Args:
        matched_keywords: List of keywords found in both resume and JD
    """
    with st.expander(f"✅ Matched Keywords ({len(matched_keywords)})", expanded=True):
        st.markdown("**Keywords found in both your resume and the job description:**")
        st.markdown("*These keywords help your resume pass ATS screening for this position.*")
        st.markdown("---")
        
        # Display as tag-style visualization
        if matched_keywords:
            # Create a visual tag display using columns
            cols_per_row = 4
            rows = [matched_keywords[i:i+cols_per_row] for i in range(0, len(matched_keywords), cols_per_row)]
            
            for row in rows:
                cols = st.columns(cols_per_row)
                for i, keyword in enumerate(row):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background-color: #e8f5e9; padding: 8px 12px; 
                                    border-radius: 20px; text-align: center; margin: 4px 0;
                                    border: 1px solid #81c784;">
                            <span style="color: #2e7d32; font-weight: 500;">✓ {keyword}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.success(f"🎉 Great job! You have {len(matched_keywords)} matching keywords with the job description.")


def display_missing_keywords(missing_keywords: List[str]) -> None:
    """
    Display missing critical keywords with importance indicators.
    
    Requirements: 11.7 - Display missing critical keywords with importance
    
    Args:
        missing_keywords: List of keywords in JD but not in resume
    """
    with st.expander(f"⚠️ Missing Keywords ({len(missing_keywords)})", expanded=True):
        st.markdown("**Keywords from the job description not found in your resume:**")
        st.markdown("*Adding these keywords can significantly improve your match score.*")
        st.markdown("---")
        
        # Categorize by importance (first keywords are typically more important)
        critical_keywords = missing_keywords[:5]  # Top 5 are critical
        important_keywords = missing_keywords[5:10]  # Next 5 are important
        other_keywords = missing_keywords[10:]  # Rest are nice-to-have
        
        # Display critical missing keywords
        if critical_keywords:
            st.markdown("**🔴 Critical (High Priority):**")
            for keyword in critical_keywords:
                st.markdown(f"""
                <div style="background-color: #ffebee; padding: 8px 12px; 
                            border-radius: 5px; margin: 4px 0;
                            border-left: 4px solid #ef5350;">
                    <span style="color: #c62828;">❌ <strong>{keyword}</strong></span>
                    <span style="color: #666; font-size: 0.9em;"> - Add this keyword to improve match</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Display important missing keywords
        if important_keywords:
            st.markdown("")
            st.markdown("**🟡 Important (Medium Priority):**")
            for keyword in important_keywords:
                st.markdown(f"""
                <div style="background-color: #fff3e0; padding: 8px 12px; 
                            border-radius: 5px; margin: 4px 0;
                            border-left: 4px solid #ffb74d;">
                    <span style="color: #f57c00;">⚠️ <strong>{keyword}</strong></span>
                </div>
                """, unsafe_allow_html=True)
        
        # Display other missing keywords
        if other_keywords:
            st.markdown("")
            st.markdown("**🟢 Nice to Have (Lower Priority):**")
            keywords_text = ", ".join(other_keywords)
            st.markdown(f"*{keywords_text}*")
        
        st.markdown("---")
        st.markdown("""
        **💡 Tips for adding missing keywords:**
        1. Naturally incorporate keywords into your experience descriptions
        2. Add relevant keywords to your skills section
        3. Use keywords in project descriptions where applicable
        4. Don't keyword-stuff - ensure natural readability
        """)


def display_skills_gap(skills_gap: List[str]) -> None:
    """
    Display skills gap analysis between resume and job description.
    
    Requirements: 11.7 - Display skills gap analysis
    
    Args:
        skills_gap: List of skills mentioned in JD but not in resume
    """
    with st.expander(f"📊 Skills Gap Analysis ({len(skills_gap)})", expanded=False):
        st.markdown("**Skills mentioned in the job description but not evident in your resume:**")
        st.markdown("*These represent potential gaps between your profile and the job requirements.*")
        st.markdown("---")
        
        if not skills_gap:
            st.success("✅ No significant skills gap detected!")
            return
        
        # Group skills by type (simplified categorization)
        technical_indicators = ['python', 'java', 'sql', 'aws', 'api', 'database', 'cloud', 
                               'docker', 'kubernetes', 'react', 'node', 'machine learning',
                               'data', 'software', 'programming', 'development', 'system']
        
        technical_skills = []
        other_skills = []
        
        for skill in skills_gap:
            skill_lower = skill.lower()
            if any(indicator in skill_lower for indicator in technical_indicators):
                technical_skills.append(skill)
            else:
                other_skills.append(skill)
        
        # Display technical skills gap
        if technical_skills:
            st.markdown("**🔧 Technical Skills Gap:**")
            for skill in technical_skills[:10]:
                st.markdown(f"- **{skill}**")
        
        # Display other skills gap
        if other_skills:
            st.markdown("")
            st.markdown("**📋 Other Skills/Requirements Gap:**")
            for skill in other_skills[:10]:
                st.markdown(f"- {skill}")
        
        st.markdown("---")
        st.markdown("""
        **🎯 How to address skills gaps:**
        
        1. **If you have the skill:** Add it to your resume with evidence
        2. **If you're learning:** Mention relevant coursework or projects
        3. **If it's a stretch:** Consider if this role is the right fit
        4. **Transferable skills:** Highlight related experience that demonstrates capability
        """)


def display_jd_match_summary(jd_comparison: Dict) -> None:
    """
    Display a summary of JD match with actionable insights.
    
    Requirements: 11.7 - JD comparison display
    
    Args:
        jd_comparison: JD comparison results dictionary
    """
    match_percentage = jd_comparison.get('match_percentage', 0.0)
    semantic_similarity = jd_comparison.get('semantic_similarity', 0.0)
    matched_keywords = jd_comparison.get('matched_keywords', [])
    missing_keywords = jd_comparison.get('missing_keywords', [])
    skills_gap = jd_comparison.get('skills_gap', [])
    
    with st.expander("📈 Match Summary & Insights", expanded=False):
        st.markdown("**Your Resume vs. Job Description Analysis:**")
        st.markdown("---")
        
        # Visual match indicator
        match_bar_color = "#2e7d32" if match_percentage >= 70 else "#f57c00" if match_percentage >= 50 else "#c62828"
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span><strong>Overall Match</strong></span>
                <span><strong>{match_percentage:.0f}%</strong></span>
            </div>
            <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px;">
                <div style="background-color: {match_bar_color}; width: {match_percentage}%; 
                            height: 100%; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics table
        st.markdown("""
        | Metric | Value | Status |
        |--------|-------|--------|
        | Match Percentage | {:.0f}% | {} |
        | Semantic Similarity | {:.0f}% | {} |
        | Keywords Matched | {} | {} |
        | Keywords Missing | {} | {} |
        | Skills Gap | {} items | {} |
        """.format(
            match_percentage,
            "✅" if match_percentage >= 60 else "⚠️" if match_percentage >= 40 else "❌",
            semantic_similarity * 100,
            "✅" if semantic_similarity >= 0.6 else "⚠️" if semantic_similarity >= 0.4 else "❌",
            len(matched_keywords),
            "✅" if len(matched_keywords) >= 10 else "⚠️" if len(matched_keywords) >= 5 else "❌",
            len(missing_keywords),
            "✅" if len(missing_keywords) <= 3 else "⚠️" if len(missing_keywords) <= 7 else "❌",
            len(skills_gap),
            "✅" if len(skills_gap) <= 3 else "⚠️" if len(skills_gap) <= 7 else "❌"
        ))
        
        st.markdown("---")
        
        # Actionable recommendations based on match
        st.markdown("**🎯 Recommended Actions:**")
        
        if match_percentage < 40:
            st.markdown("""
            1. **Major revision needed** - Consider if this role aligns with your experience
            2. **Add critical keywords** - Focus on the top 5 missing keywords
            3. **Address skills gaps** - Highlight transferable skills or relevant projects
            4. **Tailor your summary** - Align your professional summary with the JD
            """)
        elif match_percentage < 60:
            st.markdown("""
            1. **Add missing keywords** - Incorporate top missing keywords naturally
            2. **Strengthen skills section** - Add skills mentioned in the JD
            3. **Quantify achievements** - Add metrics that align with JD requirements
            4. **Review experience bullets** - Ensure they reflect JD language
            """)
        elif match_percentage < 80:
            st.markdown("""
            1. **Fine-tune keywords** - Add remaining missing keywords where relevant
            2. **Optimize for ATS** - Ensure exact keyword matches where possible
            3. **Strengthen weak areas** - Focus on any skills gaps
            4. **Polish content** - Ensure professional presentation
            """)
        else:
            st.markdown("""
            1. **Excellent match!** - Your resume is well-aligned with this position
            2. **Final polish** - Review for any remaining optimization opportunities
            3. **Prepare for interview** - Focus on discussing matched skills
            4. **Customize cover letter** - Highlight your strong alignment
            """)


def get_jd_comparison_summary(jd_comparison: Dict) -> Dict:
    """
    Get a summary of JD comparison results for use in other components.
    
    Args:
        jd_comparison: JD comparison results dictionary
        
    Returns:
        Dictionary with summary statistics
    """
    match_percentage = jd_comparison.get('match_percentage', 0.0)
    semantic_similarity = jd_comparison.get('semantic_similarity', 0.0)
    matched_keywords = jd_comparison.get('matched_keywords', [])
    missing_keywords = jd_comparison.get('missing_keywords', [])
    skills_gap = jd_comparison.get('skills_gap', [])
    
    # Determine status
    if match_percentage >= 80:
        status = 'excellent'
    elif match_percentage >= 60:
        status = 'good'
    elif match_percentage >= 40:
        status = 'moderate'
    else:
        status = 'poor'
    
    return {
        'match_percentage': match_percentage,
        'semantic_similarity': semantic_similarity,
        'matched_count': len(matched_keywords),
        'missing_count': len(missing_keywords),
        'skills_gap_count': len(skills_gap),
        'critical_missing': missing_keywords[:5],
        'has_significant_gap': len(skills_gap) > 5,
        'status': status
    }


def generate_recommendations(scores: Dict, skill_validation: Dict, 
                            grammar_results: Dict, location_results: Dict,
                            jd_comparison: Optional[Dict] = None) -> List[Dict]:
    """
    Generate prioritized recommendations based on analysis results.
    
    Args:
        scores: Score results dictionary
        skill_validation: Skill validation results
        grammar_results: Grammar check results
        location_results: Location detection results
        jd_comparison: Optional JD comparison results
        
    Returns:
        List of recommendation dictionaries with priority, category, title, and description
    """
    recommendations = []
    
    # Critical priority recommendations
    
    # Grammar critical errors
    critical_errors = grammar_results.get('critical_errors', [])
    if critical_errors:
        recommendations.append({
            'priority': 'critical',
            'category': 'Grammar',
            'title': f'Fix {len(critical_errors)} critical grammar/spelling error(s)',
            'description': 'Critical errors can immediately disqualify your resume.',
            'impact': '+5-10 points',
            'details': [f"Fix: {e.get('message', '')[:80]}" for e in critical_errors[:3]]
        })
    
    # Location privacy
    if location_results.get('privacy_risk') == 'high':
        recommendations.append({
            'priority': 'critical',
            'category': 'Privacy',
            'title': 'Remove detailed location information',
            'description': 'Full addresses can lead to bias and are unnecessary.',
            'impact': '+3-5 points',
            'details': ['Remove street address', 'Keep only city and state in header']
        })
    
    # Very low formatting
    if scores['formatting_score'] < 10:
        recommendations.append({
            'priority': 'critical',
            'category': 'Formatting',
            'title': 'Restructure resume with clear sections',
            'description': 'Poor formatting prevents ATS from parsing your resume.',
            'impact': '+10-15 points',
            'details': ['Add Experience section', 'Add Education section', 'Add Skills section', 'Use bullet points']
        })
    
    # High priority recommendations
    
    # Unvalidated skills
    unvalidated = skill_validation.get('unvalidated_skills', [])
    if len(unvalidated) > 3:
        recommendations.append({
            'priority': 'high',
            'category': 'Skills',
            'title': f'Validate {len(unvalidated)} unsubstantiated skills',
            'description': 'Skills without evidence may be questioned by recruiters.',
            'impact': '+3-8 points',
            'details': [f"Add project for: {s}" for s in unvalidated[:4]]
        })
    
    # Moderate grammar errors
    moderate_errors = grammar_results.get('moderate_errors', [])
    if len(moderate_errors) > 2:
        recommendations.append({
            'priority': 'high',
            'category': 'Grammar',
            'title': f'Address {len(moderate_errors)} moderate grammar issues',
            'description': 'These errors affect readability and professionalism.',
            'impact': '+2-5 points',
            'details': [f"Fix: {e.get('message', '')[:60]}" for e in moderate_errors[:3]]
        })
    
    # Low keywords score
    if scores['keywords_score'] < 15:
        recommendations.append({
            'priority': 'high',
            'category': 'Keywords',
            'title': 'Add more relevant keywords and skills',
            'description': 'Keywords help ATS match your resume to job requirements.',
            'impact': '+5-10 points',
            'details': ['Add technical skills', 'Include industry terminology', 'List tools and technologies']
        })
    
    # Missing JD keywords
    if jd_comparison and jd_comparison.get('missing_keywords'):
        missing = jd_comparison['missing_keywords'][:5]
        recommendations.append({
            'priority': 'high',
            'category': 'Job Match',
            'title': f'Add {len(jd_comparison["missing_keywords"])} missing keywords from job description',
            'description': 'These keywords appear in the JD but not in your resume.',
            'impact': '+5-15 points',
            'details': [f"Add: {kw}" for kw in missing]
        })
    
    # Medium priority recommendations
    
    # Content improvements
    if 14 <= scores['content_score'] < 20:
        recommendations.append({
            'priority': 'medium',
            'category': 'Content',
            'title': 'Enhance content with action verbs and metrics',
            'description': 'Quantifiable achievements make your resume more compelling.',
            'impact': '+3-5 points',
            'details': ['Start bullets with action verbs', 'Add numbers and percentages', 'Show measurable impact']
        })
    
    # Formatting improvements
    if 12 <= scores['formatting_score'] < 16:
        recommendations.append({
            'priority': 'medium',
            'category': 'Formatting',
            'title': 'Improve resume structure and organization',
            'description': 'Better formatting improves both ATS parsing and readability.',
            'impact': '+2-4 points',
            'details': ['Add more bullet points', 'Ensure consistent formatting', 'Optimize section lengths']
        })
    
    # Minor grammar issues
    minor_errors = grammar_results.get('minor_errors', [])
    if len(minor_errors) > 3:
        recommendations.append({
            'priority': 'medium',
            'category': 'Grammar',
            'title': f'Polish {len(minor_errors)} minor language issues',
            'description': 'Minor improvements for a more polished presentation.',
            'impact': '+1-2 points',
            'details': ['Review punctuation', 'Check consistency', 'Improve word choice']
        })
    
    # Skills gap from JD
    if jd_comparison and jd_comparison.get('skills_gap'):
        gap = jd_comparison['skills_gap'][:4]
        recommendations.append({
            'priority': 'medium',
            'category': 'Skills Gap',
            'title': 'Address skills gap for target position',
            'description': 'These skills are required but not evident in your resume.',
            'impact': '+3-8 points',
            'details': [f"Consider adding: {s}" for s in gap]
        })
    
    # Sort by priority
    priority_order = {'critical': 0, 'high': 1, 'medium': 2}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return recommendations


def display_recommendations_section(recommendations: List[Dict]) -> None:
    """
    Display recommendations section with expandable details.
    
    Args:
        recommendations: List of recommendation dictionaries
    """
    st.markdown("### 🎯 Recommendations")
    
    if not recommendations:
        st.success("🎉 Your resume is well-optimized! No major recommendations at this time.")
        return
    
    st.markdown("Prioritized actions to improve your ATS score:")
    
    # Group by priority
    critical = [r for r in recommendations if r['priority'] == 'critical']
    high = [r for r in recommendations if r['priority'] == 'high']
    medium = [r for r in recommendations if r['priority'] == 'medium']
    
    # Display critical recommendations
    if critical:
        st.markdown("#### 🔴 Critical Priority")
        for rec in critical:
            with st.expander(f"**{rec['title']}** - {rec['category']} ({rec['impact']})", expanded=True):
                st.markdown(f"*{rec['description']}*")
                st.markdown("**Action Items:**")
                for detail in rec['details']:
                    st.markdown(f"- {detail}")
    
    # Display high priority recommendations
    if high:
        st.markdown("#### 🟡 High Priority")
        for rec in high:
            with st.expander(f"**{rec['title']}** - {rec['category']} ({rec['impact']})", expanded=False):
                st.markdown(f"*{rec['description']}*")
                st.markdown("**Action Items:**")
                for detail in rec['details']:
                    st.markdown(f"- {detail}")
    
    # Display medium priority recommendations
    if medium:
        st.markdown("#### 🟢 Medium Priority")
        for rec in medium:
            with st.expander(f"**{rec['title']}** - {rec['category']} ({rec['impact']})", expanded=False):
                st.markdown(f"*{rec['description']}*")
                st.markdown("**Action Items:**")
                for detail in rec['details']:
                    st.markdown(f"- {detail}")
    
    # Summary
    st.markdown("---")
    total_impact = len(critical) * 8 + len(high) * 5 + len(medium) * 3
    st.info(f"💡 **Potential Score Improvement:** Addressing all recommendations could improve your score by approximately **{total_impact}+ points**.")


def generate_action_items(scores: Dict, skill_validation: Dict,
                         grammar_results: Dict, location_results: Dict,
                         jd_comparison: Optional[Dict] = None) -> List[Dict]:
    """
    Generate prioritized action items based on analysis results.
    
    Requirements: 11.8 - Display prioritized action items categorized as critical, high, or medium priority
    
    Args:
        scores: Score results dictionary
        skill_validation: Skill validation results
        grammar_results: Grammar check results
        location_results: Location detection results
        jd_comparison: Optional JD comparison results
        
    Returns:
        List of action item dictionaries with id, priority, text, category, and completed status
    """
    action_items = []
    item_id = 0
    
    # Critical priority action items
    
    # Grammar critical errors - each error is an action item
    critical_errors = grammar_results.get('critical_errors', [])
    for i, error in enumerate(critical_errors[:5]):  # Limit to top 5
        item_id += 1
        suggestion = error.get('suggestions', [''])[0] if error.get('suggestions') else ''
        error_text = error.get('error_text', '')
        action_text = f"Fix spelling/grammar: '{error_text}'"
        if suggestion:
            action_text += f" → '{suggestion}'"
        action_items.append({
            'id': item_id,
            'priority': 'critical',
            'text': action_text,
            'category': 'Grammar',
            'completed': False,
            'impact': 5
        })
    
    # Location privacy - critical if high risk
    if location_results.get('privacy_risk') == 'high':
        detected = location_results.get('detected_locations', [])
        addresses = [loc for loc in detected if loc.get('type') == 'address']
        zip_codes = [loc for loc in detected if loc.get('type') == 'zip']
        
        if addresses:
            item_id += 1
            action_items.append({
                'id': item_id,
                'priority': 'critical',
                'text': f"Remove full street address from resume",
                'category': 'Privacy',
                'completed': False,
                'impact': 4
            })
        
        if zip_codes:
            item_id += 1
            action_items.append({
                'id': item_id,
                'priority': 'critical',
                'text': f"Remove zip code from resume",
                'category': 'Privacy',
                'completed': False,
                'impact': 4
            })
    
    # Very low formatting score
    if scores['formatting_score'] < 10:
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'critical',
            'text': "Add clear section headers (Experience, Education, Skills)",
            'category': 'Formatting',
            'completed': False,
            'impact': 8
        })
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'critical',
            'text': "Convert paragraphs to bullet points",
            'category': 'Formatting',
            'completed': False,
            'impact': 5
        })
    
    # High priority action items
    
    # Unvalidated skills
    unvalidated = skill_validation.get('unvalidated_skills', [])
    for skill in unvalidated[:5]:  # Limit to top 5
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'high',
            'text': f"Add project demonstrating '{skill}' or remove from skills",
            'category': 'Skills',
            'completed': False,
            'impact': 3
        })
    
    # Moderate grammar errors
    moderate_errors = grammar_results.get('moderate_errors', [])
    for i, error in enumerate(moderate_errors[:3]):  # Limit to top 3
        item_id += 1
        suggestion = error.get('suggestions', [''])[0] if error.get('suggestions') else ''
        error_text = error.get('error_text', '')
        action_text = f"Fix punctuation/grammar: '{error_text}'"
        if suggestion:
            action_text += f" → '{suggestion}'"
        action_items.append({
            'id': item_id,
            'priority': 'high',
            'text': action_text,
            'category': 'Grammar',
            'completed': False,
            'impact': 2
        })
    
    # Missing JD keywords (if JD provided)
    if jd_comparison:
        missing = jd_comparison.get('missing_keywords', [])
        for keyword in missing[:5]:  # Top 5 missing keywords
            item_id += 1
            action_items.append({
                'id': item_id,
                'priority': 'high',
                'text': f"Add keyword '{keyword}' to resume",
                'category': 'Keywords',
                'completed': False,
                'impact': 3
            })
    
    # Low keywords score (if no JD)
    if not jd_comparison and scores['keywords_score'] < 15:
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'high',
            'text': "Add more technical skills and industry keywords",
            'category': 'Keywords',
            'completed': False,
            'impact': 5
        })
    
    # Medium priority action items
    
    # Content improvements
    if 14 <= scores['content_score'] < 20:
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'medium',
            'text': "Start experience bullets with strong action verbs",
            'category': 'Content',
            'completed': False,
            'impact': 2
        })
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'medium',
            'text': "Add quantifiable metrics to achievements (%, $, numbers)",
            'category': 'Content',
            'completed': False,
            'impact': 3
        })
    
    # Formatting improvements
    if 12 <= scores['formatting_score'] < 16:
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'medium',
            'text': "Add more bullet points (aim for 3-5 per role)",
            'category': 'Formatting',
            'completed': False,
            'impact': 2
        })
    
    # Minor grammar issues
    minor_errors = grammar_results.get('minor_errors', [])
    if len(minor_errors) > 3:
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'medium',
            'text': f"Review and fix {len(minor_errors)} minor style issues",
            'category': 'Grammar',
            'completed': False,
            'impact': 1
        })
    
    # Skills gap from JD
    if jd_comparison:
        skills_gap = jd_comparison.get('skills_gap', [])
        for skill in skills_gap[:3]:  # Top 3 skills gap
            item_id += 1
            action_items.append({
                'id': item_id,
                'priority': 'medium',
                'text': f"Consider adding skill: '{skill}'",
                'category': 'Skills Gap',
                'completed': False,
                'impact': 2
            })
    
    # Medium location risk
    if location_results.get('privacy_risk') == 'medium':
        item_id += 1
        action_items.append({
            'id': item_id,
            'priority': 'medium',
            'text': "Simplify location to just City, State in contact header",
            'category': 'Privacy',
            'completed': False,
            'impact': 2
        })
    
    # Sort by priority and impact
    priority_order = {'critical': 0, 'high': 1, 'medium': 2}
    action_items.sort(key=lambda x: (priority_order.get(x['priority'], 3), -x['impact']))
    
    return action_items


def get_priority_color(priority: str) -> Tuple[str, str, str]:
    """
    Get color coding for priority level.
    
    Requirements: 11.8 - Use color coding for priority levels
    
    Args:
        priority: Priority level ("critical", "high", "medium")
        
    Returns:
        Tuple of (text_color, background_color, border_color)
    """
    if priority == "critical":
        return "#c62828", "#ffebee", "#ef5350"  # Red
    elif priority == "high":
        return "#f57c00", "#fff3e0", "#ffb74d"  # Orange
    else:  # medium
        return "#1976d2", "#e3f2fd", "#64b5f6"  # Blue


def get_priority_icon(priority: str) -> str:
    """
    Get icon for priority level.
    
    Args:
        priority: Priority level
        
    Returns:
        Emoji icon string
    """
    if priority == "critical":
        return "🔴"
    elif priority == "high":
        return "🟡"
    else:  # medium
        return "🔵"


def display_action_items_section(scores: Dict, skill_validation: Dict,
                                  grammar_results: Dict, location_results: Dict,
                                  jd_comparison: Optional[Dict] = None) -> None:
    """
    Display priority action items section as an interactive checklist.
    
    Requirements: 11.8 - Display prioritized action items categorized as critical, high, or medium priority
    
    Args:
        scores: Score results dictionary
        skill_validation: Skill validation results
        grammar_results: Grammar check results
        location_results: Location detection results
        jd_comparison: Optional JD comparison results
    """
    st.markdown("### ✅ Priority Action Items")
    
    # Generate action items
    action_items = generate_action_items(
        scores, skill_validation, grammar_results, location_results, jd_comparison
    )
    
    if not action_items:
        st.success("🎉 Excellent! No action items needed. Your resume is well-optimized!")
        return
    
    # Group by priority
    critical_items = [item for item in action_items if item['priority'] == 'critical']
    high_items = [item for item in action_items if item['priority'] == 'high']
    medium_items = [item for item in action_items if item['priority'] == 'medium']
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Items",
            value=len(action_items)
        )
    
    with col2:
        st.metric(
            label="🔴 Critical",
            value=len(critical_items),
            help="Must fix immediately"
        )
    
    with col3:
        st.metric(
            label="🟡 High",
            value=len(high_items),
            help="Should address soon"
        )
    
    with col4:
        st.metric(
            label="🔵 Medium",
            value=len(medium_items),
            help="Nice to have improvements"
        )
    
    # Calculate potential score improvement
    total_impact = sum(item['impact'] for item in action_items)
    st.info(f"💡 **Potential Score Improvement:** Completing all items could add up to **{total_impact}+ points** to your score.")
    
    st.markdown("---")
    
    # Initialize session state for checkboxes if not exists
    if 'action_items_state' not in st.session_state:
        st.session_state.action_items_state = {}
    
    # Display critical priority items
    # Requirements: 11.8 - Display items categorized by priority (critical, high, medium)
    if critical_items:
        text_color, bg_color, border_color = get_priority_color('critical')
        st.markdown(f"""
        <div style="padding: 0.5rem 1rem; background-color: {bg_color}; 
                    border-left: 4px solid {border_color}; border-radius: 5px; margin-bottom: 0.5rem;">
            <h4 style="color: {text_color}; margin: 0;">🔴 Critical Priority ({len(critical_items)} items)</h4>
            <p style="color: #666; margin: 0; font-size: 0.9em;">These issues must be fixed immediately</p>
        </div>
        """, unsafe_allow_html=True)
        
        display_action_items_checklist(critical_items, 'critical')
        st.markdown("")
    
    # Display high priority items
    if high_items:
        text_color, bg_color, border_color = get_priority_color('high')
        st.markdown(f"""
        <div style="padding: 0.5rem 1rem; background-color: {bg_color}; 
                    border-left: 4px solid {border_color}; border-radius: 5px; margin-bottom: 0.5rem;">
            <h4 style="color: {text_color}; margin: 0;">🟡 High Priority ({len(high_items)} items)</h4>
            <p style="color: #666; margin: 0; font-size: 0.9em;">Should be addressed for better results</p>
        </div>
        """, unsafe_allow_html=True)
        
        display_action_items_checklist(high_items, 'high')
        st.markdown("")
    
    # Display medium priority items
    if medium_items:
        text_color, bg_color, border_color = get_priority_color('medium')
        st.markdown(f"""
        <div style="padding: 0.5rem 1rem; background-color: {bg_color}; 
                    border-left: 4px solid {border_color}; border-radius: 5px; margin-bottom: 0.5rem;">
            <h4 style="color: {text_color}; margin: 0;">🔵 Medium Priority ({len(medium_items)} items)</h4>
            <p style="color: #666; margin: 0; font-size: 0.9em;">Nice to have improvements</p>
        </div>
        """, unsafe_allow_html=True)
        
        display_action_items_checklist(medium_items, 'medium')
    
    # Display completion summary
    st.markdown("---")
    display_action_items_summary(action_items)


def display_action_items_checklist(items: List[Dict], priority: str) -> None:
    """
    Display action items as an interactive checklist.
    
    Requirements: 11.8 - Format as interactive checklist
    
    Args:
        items: List of action item dictionaries
        priority: Priority level for styling
    """
    icon = get_priority_icon(priority)
    
    for item in items:
        item_key = f"action_item_{item['id']}"
        
        # Get current state from session state
        is_checked = st.session_state.action_items_state.get(item_key, False)
        
        # Create checkbox with styled label
        col1, col2 = st.columns([0.9, 0.1])
        
        with col1:
            # Use checkbox for interactive checklist
            checked = st.checkbox(
                f"{icon} {item['text']}",
                value=is_checked,
                key=item_key,
                help=f"Category: {item['category']} | Impact: +{item['impact']} pts"
            )
            
            # Update session state
            st.session_state.action_items_state[item_key] = checked
        
        with col2:
            # Show category badge
            st.caption(item['category'])


def display_action_items_summary(action_items: List[Dict]) -> None:
    """
    Display summary of action items completion status.
    
    Requirements: 11.8 - Action items section
    
    Args:
        action_items: List of all action items
    """
    # Count completed items from session state
    completed_count = sum(
        1 for item in action_items 
        if st.session_state.action_items_state.get(f"action_item_{item['id']}", False)
    )
    
    total_count = len(action_items)
    completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0
    
    # Calculate remaining impact
    remaining_impact = sum(
        item['impact'] for item in action_items
        if not st.session_state.action_items_state.get(f"action_item_{item['id']}", False)
    )
    
    with st.expander("📊 Progress Summary", expanded=False):
        st.markdown(f"**Completion Status:** {completed_count}/{total_count} items ({completion_percentage:.0f}%)")
        
        # Progress bar
        progress_color = "#2e7d32" if completion_percentage >= 80 else "#f57c00" if completion_percentage >= 50 else "#c62828"
        st.markdown(f"""
        <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px; margin: 10px 0;">
            <div style="background-color: {progress_color}; width: {completion_percentage}%; 
                        height: 100%; border-radius: 10px; transition: width 0.5s ease-in-out;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        if completed_count == total_count:
            st.success("🎉 All action items completed! Great job optimizing your resume!")
        elif completed_count > 0:
            st.info(f"💪 Keep going! {total_count - completed_count} items remaining. Potential improvement: +{remaining_impact} points.")
        else:
            st.warning(f"📝 Start checking off items to track your progress. Potential improvement: +{remaining_impact} points.")
        
        # Tips
        st.markdown("""
        **💡 Tips:**
        - Focus on critical items first for maximum impact
        - Re-upload your resume after making changes to see updated scores
        - Check items as you complete them to track progress
        """)


def get_action_items_summary(scores: Dict, skill_validation: Dict,
                             grammar_results: Dict, location_results: Dict,
                             jd_comparison: Optional[Dict] = None) -> Dict:
    """
    Get a summary of action items for use in other components.
    
    Args:
        scores: Score results dictionary
        skill_validation: Skill validation results
        grammar_results: Grammar check results
        location_results: Location detection results
        jd_comparison: Optional JD comparison results
        
    Returns:
        Dictionary with summary statistics
    """
    action_items = generate_action_items(
        scores, skill_validation, grammar_results, location_results, jd_comparison
    )
    
    critical_count = len([item for item in action_items if item['priority'] == 'critical'])
    high_count = len([item for item in action_items if item['priority'] == 'high'])
    medium_count = len([item for item in action_items if item['priority'] == 'medium'])
    total_impact = sum(item['impact'] for item in action_items)
    
    return {
        'total_items': len(action_items),
        'critical_count': critical_count,
        'high_count': high_count,
        'medium_count': medium_count,
        'total_impact': total_impact,
        'has_critical': critical_count > 0,
        'items': action_items
    }


def display_results_dashboard(results: Dict) -> None:
    """
    Display the complete results dashboard.
    
    This is the main entry point for displaying analysis results.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.8
    
    Args:
        results: Complete analysis results dictionary
    """
    scores = results['scores']
    skill_validation = results['skill_validation']
    grammar_results = results['grammar_results']
    location_results = results['location_results']
    jd_comparison = results.get('jd_comparison')
    
    # 1. Overall Score Display
    # Requirements: 11.1 - Score color coding
    display_overall_score(scores)
    
    st.markdown("---")
    
    # 2. Score Breakdown
    # Requirements: 11.2 - Component score display
    display_score_breakdown(scores)
    
    st.markdown("---")
    
    # 3. Strengths Section with expandable details
    display_strengths_section(
        results['strengths'],
        scores,
        skill_validation,
        grammar_results
    )
    
    st.markdown("---")
    
    # 4. Critical Issues Section with expandable details
    display_critical_issues_section(
        results['critical_issues'],
        scores,
        grammar_results,
        location_results
    )
    
    st.markdown("---")
    
    # 5. Areas for Improvement Section
    display_improvements_section(
        results['improvements'],
        scores,
        skill_validation
    )
    
    st.markdown("---")
    
    # 6. Skill Validation Analysis Section
    # Requirements: 11.3 - Display validated skills with associated project names
    # Requirements: 11.4 - Display unvalidated skills with warning indicators
    display_skill_validation_section(skill_validation, scores)
    
    st.markdown("---")
    
    # 7. Experience Section Analysis (replaced grammar check)
    experience_results = results.get('experience_results', {})
    display_experience_section(experience_results)
    
    st.markdown("---")
    
    # 8. Privacy Check Display Section
    # Requirements: 11.6 - Display privacy alert with detected locations and removal recommendations
    display_privacy_check_section(location_results)
    
    st.markdown("---")
    
    # 9. JD Comparison Display Section (conditional on JD provided)
    # Requirements: 11.7 - Display matched keywords, missing keywords, and skills gap analysis
    if jd_comparison:
        display_jd_comparison_section(jd_comparison)
        st.markdown("---")
    
    # 10. Action Items Section
    # Requirements: 11.8 - Display prioritized action items categorized as critical, high, or medium priority
    display_action_items_section(
        scores,
        skill_validation,
        grammar_results,
        location_results,
        jd_comparison
    )
    
    st.markdown("---")
    
    # 11. Recommendations Section
    recommendations = generate_recommendations(
        scores,
        skill_validation,
        grammar_results,
        location_results,
        jd_comparison
    )
    display_recommendations_section(recommendations)
