"""
Skill Validator Module for ATS Resume Scorer

This module validates that claimed skills are demonstrated in projects and experience
using exact matching and semantic similarity with embeddings.
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
import numpy as np


@st.cache_resource
def load_embedder(model_name: str = "all-MiniLM-L6-v2"):
    """
    Load and cache Sentence-Transformers model for embeddings.
    
    Args:
        model_name: Name of the Sentence-Transformers model
        
    Returns:
        Loaded SentenceTransformer object
        
    Validates:
        - Requirements 14.2: Load Sentence-Transformers model from local storage
        - Requirements 14.4: Cache models in memory
    """
    try:
        embedder = SentenceTransformer(model_name)
        return embedder
    except Exception as e:
        st.error(f"Failed to load Sentence-Transformers model: {e}")
        raise


def calculate_semantic_similarity(
    skill: str,
    text: str,
    embedder: SentenceTransformer
) -> float:
    """
    Calculates cosine similarity between skill and text embeddings.
    
    Args:
        skill: Skill text to validate
        text: Project or experience text to check against
        embedder: Loaded SentenceTransformer model
        
    Returns:
        Similarity score between 0.0 and 1.0
        
    Validates:
        - Requirements 6.2: Calculate semantic similarity using embeddings
    """
    if not skill or not text:
        return 0.0
    
    try:
        # Generate embeddings
        skill_embedding = embedder.encode(skill, convert_to_tensor=False)
        text_embedding = embedder.encode(text, convert_to_tensor=False)
        
        # Calculate cosine similarity
        similarity = np.dot(skill_embedding, text_embedding) / (
            np.linalg.norm(skill_embedding) * np.linalg.norm(text_embedding)
        )
        
        # Ensure result is between 0 and 1
        similarity = float(max(0.0, min(1.0, similarity)))
        
        return similarity
    except Exception as e:
        st.warning(f"Error calculating similarity for skill '{skill}': {e}")
        return 0.0


def exact_skill_match(skill: str, text: str) -> bool:
    """
    Checks if skill appears exactly in the text (case-insensitive).
    
    Args:
        skill: Skill text to search for
        text: Text to search in
        
    Returns:
        True if skill appears in text, False otherwise
        
    Validates:
        - Requirements 6.1: Match skills against project descriptions using exact text matching
    """
    if not skill or not text:
        return False
    
    # Case-insensitive exact matching
    return skill.lower() in text.lower()


def validate_skill_against_projects(
    skill: str,
    projects: List[Dict[str, str]],
    experience: str,
    embedder: SentenceTransformer,
    threshold: float = 0.6
) -> Tuple[bool, List[str], float]:
    """
    Validates a single skill against projects and experience.
    
    Args:
        skill: Skill to validate
        projects: List of project dictionaries with 'title', 'description', 'technologies'
        experience: Experience section text
        embedder: Loaded SentenceTransformer model
        threshold: Similarity threshold for validation (default 0.6)
        
    Returns:
        Tuple of (is_validated, matching_projects, max_similarity)
        
    Validates:
        - Requirements 6.1: Exact text matching
        - Requirements 6.2: Semantic similarity calculation
        - Requirements 6.3: Validation threshold of 0.6
    """
    matching_projects = []
    max_similarity = 0.0
    
    # Check each project
    for project in projects:
        project_text = f"{project.get('title', '')} {project.get('description', '')}"
        
        # Check for exact match first
        if exact_skill_match(skill, project_text):
            matching_projects.append(project.get('title', 'Untitled Project'))
            max_similarity = 1.0
            continue
        
        # Calculate semantic similarity
        similarity = calculate_semantic_similarity(skill, project_text, embedder)
        max_similarity = max(max_similarity, similarity)
        
        # Check if similarity exceeds threshold
        if similarity >= threshold:
            matching_projects.append(project.get('title', 'Untitled Project'))
    
    # Also check experience section
    if experience:
        if exact_skill_match(skill, experience):
            if 'Experience Section' not in matching_projects:
                matching_projects.append('Experience Section')
            max_similarity = 1.0
        else:
            similarity = calculate_semantic_similarity(skill, experience, embedder)
            max_similarity = max(max_similarity, similarity)
            
            if similarity >= threshold and 'Experience Section' not in matching_projects:
                matching_projects.append('Experience Section')
    
    # Skill is validated if it matches at least one project or experience
    is_validated = len(matching_projects) > 0
    
    return is_validated, matching_projects, max_similarity


def _compute_skill_validation(
    skills: List[str],
    projects: List[Dict[str, str]],
    experience: str,
    embedder: SentenceTransformer,
    threshold: float
) -> Dict:
    """
    Internal function to compute skill validation.
    
    Args:
        skills: List of skills to validate
        projects: List of project dictionaries
        experience: Experience section text
        embedder: SentenceTransformer model
        threshold: Similarity threshold for validation
        
    Returns:
        Dictionary with validation results
    """
    validated_skills = []
    unvalidated_skills = []
    skill_project_mapping = {}
    
    # Handle empty skills list
    if not skills:
        return {
            "validated_skills": [],
            "unvalidated_skills": [],
            "validation_percentage": 0.0,
            "skill_project_mapping": {},
            "validation_score": 0.0
        }
    
    # Validate each skill
    for skill in skills:
        is_validated, matching_projects, similarity = validate_skill_against_projects(
            skill, projects, experience, embedder, threshold
        )
        
        if is_validated:
            validated_skills.append({
                "skill": skill,
                "projects": matching_projects,
                "similarity": similarity
            })
            skill_project_mapping[skill] = matching_projects
        else:
            unvalidated_skills.append(skill)
            skill_project_mapping[skill] = []
    
    # Calculate validation percentage
    validation_percentage = len(validated_skills) / len(skills) if skills else 0.0
    
    # Calculate validation score: (validated / total) × 15
    validation_score = validation_percentage * 15.0
    
    return {
        "validated_skills": validated_skills,
        "unvalidated_skills": unvalidated_skills,
        "validation_percentage": validation_percentage,
        "skill_project_mapping": skill_project_mapping,
        "validation_score": validation_score
    }


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_skill_validation(
    skills_tuple: tuple,
    projects_json: str,
    experience_hash: str,
    threshold: float,
    _embedder
) -> Dict:
    """
    Cached version of skill validation.
    
    Args:
        skills_tuple: Tuple of skills (hashable)
        projects_json: JSON string of projects (hashable)
        experience_hash: Hash of experience text
        threshold: Similarity threshold
        _embedder: Sentence transformer model (excluded from hash)
        
    Returns:
        Dictionary with validation results
        
    Validates:
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    import json
    skills = list(skills_tuple)
    projects = json.loads(projects_json)
    
    # We need to retrieve experience from somewhere - use hash as marker
    # The actual experience is passed through the non-cached wrapper
    return None  # Placeholder - actual caching done in wrapper


def validate_skills_with_projects(
    skills: List[str],
    projects: List[Dict[str, str]],
    experience: str,
    embedder: SentenceTransformer = None,
    threshold: float = 0.6,
    use_cache: bool = True
) -> Dict:
    """
    Validates all skills against projects and experience.
    
    Args:
        skills: List of skills to validate
        projects: List of project dictionaries
        experience: Experience section text
        embedder: Optional pre-loaded SentenceTransformer model
        threshold: Similarity threshold for validation (default 0.6)
        use_cache: Whether to use session state caching (default: True)
        
    Returns:
        Dictionary with validation results:
        {
            "validated_skills": [{"skill": "...", "projects": [...], "similarity": 0.0-1.0}],
            "unvalidated_skills": ["..."],
            "validation_percentage": 0.0-1.0,
            "skill_project_mapping": {"skill": ["project1", "project2"]},
            "validation_score": 0.0-15.0
        }
        
    Validates:
        - Requirements 6.1: Exact skill matching
        - Requirements 6.2: Semantic similarity calculation
        - Requirements 6.3: Validation threshold of 0.6
        - Requirements 6.4: Unmatched skill detection
        - Requirements 6.5: Skill-project mapping generation
        - Requirements 6.6: Validation score calculation (validated / total) × 15
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    # Load embedder if not provided
    if embedder is None:
        embedder = load_embedder()
    
    # Check if we're in a Streamlit context
    try:
        # Check if session_state is a proper Streamlit SessionState object
        from streamlit.runtime.state import SessionState
        in_streamlit = isinstance(st.session_state, SessionState)
    except Exception:
        in_streamlit = False
    
    if use_cache and in_streamlit:
        # Generate cache key from inputs
        import hashlib
        import json
        
        skills_key = tuple(sorted(skills)) if skills else ()
        projects_key = json.dumps(projects, sort_keys=True) if projects else "[]"
        experience_key = hashlib.sha256(experience.encode('utf-8')).hexdigest() if experience else ""
        
        cache_key = f"skill_validation_{hash((skills_key, projects_key, experience_key, threshold))}"
        
        # Check session state cache
        if 'skill_validation_cache' not in st.session_state:
            st.session_state.skill_validation_cache = {}
        
        if cache_key in st.session_state.skill_validation_cache:
            return st.session_state.skill_validation_cache[cache_key]
        
        # Compute and cache
        result = _compute_skill_validation(skills, projects, experience, embedder, threshold)
        st.session_state.skill_validation_cache[cache_key] = result
        
        # Limit cache size
        if len(st.session_state.skill_validation_cache) > 20:
            # Remove oldest entry
            oldest_key = next(iter(st.session_state.skill_validation_cache))
            del st.session_state.skill_validation_cache[oldest_key]
        
        return result
    else:
        return _compute_skill_validation(skills, projects, experience, embedder, threshold)


def generate_validation_feedback(validation_results: Dict) -> List[str]:
    """
    Generates user-friendly feedback messages for validated/unvalidated skills.
    
    Args:
        validation_results: Results from validate_skills_with_projects
        
    Returns:
        List of feedback messages
        
    Validates:
        - Requirements 6.5: Generate validation feedback messages
    """
    feedback = []
    
    validated_skills = validation_results.get("validated_skills", [])
    unvalidated_skills = validation_results.get("unvalidated_skills", [])
    validation_percentage = validation_results.get("validation_percentage", 0.0)
    
    # Overall validation summary
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
    
    # Feedback for validated skills
    if validated_skills:
        feedback.append(f"\n✅ Validated Skills ({len(validated_skills)}):")
        for skill_info in validated_skills[:5]:  # Show top 5
            skill = skill_info["skill"]
            projects = skill_info["projects"]
            if len(projects) == 1:
                feedback.append(f"  • {skill} - demonstrated in {projects[0]}")
            else:
                feedback.append(f"  • {skill} - demonstrated in {len(projects)} projects")
    
    # Feedback for unvalidated skills
    if unvalidated_skills:
        feedback.append(f"\n❌ Unvalidated Skills ({len(unvalidated_skills)}):")
        for skill in unvalidated_skills[:5]:  # Show top 5
            feedback.append(f"  • {skill} - not found in projects or experience")
        
        feedback.append(
            "\n💡 Recommendation: Either add projects demonstrating these skills or remove them from your skills list."
        )
    
    return feedback


def calculate_skill_validation_score(validation_results: Dict) -> float:
    """
    Calculates the skill validation component score.
    
    Args:
        validation_results: Results from validate_skills_with_projects
        
    Returns:
        Score between 0.0 and 15.0
        
    Validates:
        - Requirements 6.6: Validation score calculation (validated / total) × 15
    """
    return validation_results.get("validation_score", 0.0)
