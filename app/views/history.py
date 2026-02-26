"""History view"""
import streamlit as st
from app.config.database import get_user_history, clear_user_history, delete_history_entry


def render():
    """Render the history page"""
    
    st.title("📊 Analysis History")
    st.markdown("View your past resume analyses")
    
    # Get user's history
    history = get_user_history()
    
    if not history:
        st.info("No analysis history yet. Upload a resume to get started!")
        
        if st.button("🎯 Go to ATS Scorer"):
            st.session_state.current_view = 'scorer'
            st.rerun()
    else:
        # Header with clear all button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Total Analyses:** {len(history)}")
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                if clear_user_history():
                    st.success("History cleared!")
                    st.rerun()
        
        st.markdown("---")
        
        # Display history items
        for idx, item in enumerate(history):
            filename = item.get('filename', 'Unknown')
            overall_score = item.get('overall_score', 0)
            timestamp = item.get('timestamp', 'N/A')
            
            with st.expander(f"📄 {filename} - Score: {overall_score}/100 - {timestamp}"):
                # Component scores
                component_scores = item.get('component_scores', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Score", f"{overall_score}/100")
                    st.metric("Formatting", f"{component_scores.get('formatting_score', 0)}/100")
                
                with col2:
                    st.metric("Keywords", f"{component_scores.get('keywords_score', 0)}/100")
                    st.metric("Content", f"{component_scores.get('content_score', 0)}/100")
                
                with col3:
                    st.metric("Skill Validation", f"{component_scores.get('skill_validation_score', 0)}/100")
                    st.metric("ATS Compatibility", f"{component_scores.get('ats_compatibility_score', 0)}/100")
                
                # JD Match if available
                jd_match = item.get('jd_match')
                if jd_match is not None:
                    st.markdown(f"**Job Description Match:** {jd_match}%")
                
                # Delete button
                if 'id' in item:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        if delete_history_entry(item['id']):
                            st.success("Entry deleted!")
                            st.rerun()
