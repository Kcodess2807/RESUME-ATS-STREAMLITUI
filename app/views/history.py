"""History view"""
import streamlit as st
from app.config.database import get_user_history


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
        st.markdown(f"**Total Analyses:** {len(history)}")
        
        for idx, item in enumerate(history):
            with st.expander(f"📄 {item.get('filename', 'Unknown')} - Score: {item.get('score', 0)}/100"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Overall Score", f"{item.get('score', 0)}/100")
                
                with col2:
                    st.metric("Date", item.get('date', 'N/A'))
                
                with col3:
                    if st.button("View Details", key=f"view_{idx}"):
                        st.session_state.selected_history = item
                        st.rerun()
