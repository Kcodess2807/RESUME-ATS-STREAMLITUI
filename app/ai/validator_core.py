import streamlit as st
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
from app.ai.validator_utils import calculate_semantic_similarity, exact_skill_match


def validate_skill_against_projects(
    skill: str,
    projects: List[Dict[str, str]],
    experience: str,
    embedder: SentenceTransformer,
    threshold: float = 0.6
) -> Tuple[bool, List[str], float]:
    matching_projects = []
    max_similarity = 0.0
    
    for project in projects:
        project_text = f"{project.get('title', '')} {project.get('description', '')}"
        
        if exact_skill_match(skill, project_text):
            matching_projects.append(project.get('title', 'Untitled Project'))
            max_similarity = 1.0
            continue
        
        similarity = calculate_semantic_similarity(skill, project_text, embedder)
        max_similarity = max(max_similarity, similarity)
        
        if similarity >= threshold:
            matching_projects.append(project.get('title', 'Untitled Project'))
    
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
    
    is_validated = len(matching_projects) > 0
    
    return is_validated, matching_projects, max_similarity


def _compute_skill_validation(
    skills: List[str],
    projects: List[Dict[str, str]],
    experience: str,
    embedder: SentenceTransformer,
    threshold: float
) -> Dict:
    validated_skills = []
    unvalidated_skills = []
    skill_project_mapping = {}
    
    if not skills:
        return {
            "validated_skills": [],
            "unvalidated_skills": [],
            "validation_percentage": 0.0,
            "skill_project_mapping": {},
            "validation_score": 0.0
        }
    
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
    
    validation_percentage = len(validated_skills) / len(skills) if skills else 0.0
    
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
    import json
    skills = list(skills_tuple)
    projects = json.loads(projects_json)
    
    return None
