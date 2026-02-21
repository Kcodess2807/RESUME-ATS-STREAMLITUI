import streamlit as st
from sentence_transformers import SentenceTransformer
from typing import Dict, List
from app.ai.validator_utils import load_embedder
from app.ai.validator_core import _compute_skill_validation

# Re-export for backward compatibility
__all__ = ['load_embedder', 'validate_skills_with_projects', 'generate_validation_feedback', 'calculate_skill_validation_score']


def validate_skills_with_projects(
    skills: List[str],
    projects: List[Dict[str, str]],
    experience: str,
    embedder: SentenceTransformer = None,
    threshold: float = 0.6,
    use_cache: bool = True
) -> Dict:
    if embedder is None:
        embedder = load_embedder()
    
    try:
        from streamlit.runtime.state import SessionState
        in_streamlit = isinstance(st.session_state, SessionState)
    except Exception:
        in_streamlit = False
    
    if use_cache and in_streamlit:
        import hashlib
        import json
        
        skills_key = tuple(sorted(skills)) if skills else ()
        projects_key = json.dumps(projects, sort_keys=True) if projects else "[]"
        experience_key = hashlib.sha256(experience.encode('utf-8')).hexdigest() if experience else ""
        
        cache_key = f"skill_validation_{hash((skills_key, projects_key, experience_key, threshold))}"
        
        if 'skill_validation_cache' not in st.session_state:
            st.session_state.skill_validation_cache = {}
        
        if cache_key in st.session_state.skill_validation_cache:
            return st.session_state.skill_validation_cache[cache_key]
        
        result = _compute_skill_validation(skills, projects, experience, embedder, threshold)
        st.session_state.skill_validation_cache[cache_key] = result
        
        if len(st.session_state.skill_validation_cache) > 20:
            oldest_key = next(iter(st.session_state.skill_validation_cache))
            del st.session_state.skill_validation_cache[oldest_key]
        
        return result
    else:
        return _compute_skill_validation(skills, projects, experience, embedder, threshold)


def generate_validation_feedback(validation_results: Dict) -> List[str]:
    feedback = []
    
    validated_skills = validation_results.get("validated_skills", [])
    unvalidated_skills = validation_results.get("unvalidated_skills", [])
    validation_percentage = validation_results.get("validation_percentage", 0.0)
    
    if validation_percentage >= 0.8:
        feedback.append(
            f"✅ Excellent! {validation_percentage*100:.0f}% of your skills are validated by your projects and experience."
        )
    elif validation_percentage >= 0.6:
        feedback.append(
            f"👍 Good! {validation_percentage*100:.0f}% of your skills are validated, but there's room for improvement."
        )
    elif validation_percentage >= 0.4:
        feedback.append(
            f"⚠️ {validation_percentage*100:.0f}% of your skills are validated. Consider adding more project details."
        )
    else:
        feedback.append(
            f"❌ Only {validation_percentage*100:.0f}% of your skills are validated. Many skills lack supporting evidence."
        )
    
    if validated_skills:
        feedback.append(f"\n✅ Validated Skills ({len(validated_skills)}):")
        for skill_info in validated_skills[:5]:
            skill = skill_info["skill"]
            projects = skill_info["projects"]
            if len(projects) == 1:
                feedback.append(f"  • {skill} - demonstrated in {projects[0]}")
            else:
                feedback.append(f"  • {skill} - demonstrated in {len(projects)} projects")
    
    if unvalidated_skills:
        feedback.append(f"\n❌ Unvalidated Skills ({len(unvalidated_skills)}):")
        for skill in unvalidated_skills[:5]:
            feedback.append(f"  • {skill} - not found in projects or experience")
        
        feedback.append(
            "\n💡 Recommendation: Either add projects demonstrating these skills or remove them from your skills list."
        )
    
    return feedback


def calculate_skill_validation_score(validation_results: Dict) -> float:
    return validation_results.get("validation_score", 0.0)
