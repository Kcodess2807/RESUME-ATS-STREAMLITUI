"""
Validator Core Module
Contains the core skill validation algorithms.

📚 TEACHING NOTE — Why is this called 'core'?
    The 'core' module contains the most critical business logic —
    the actual algorithm that decides if a skill is validated or not.
    
    Think of the layers like this:
        validator_utils.py  →  basic tools (similarity math, exact match)
        validator_core.py   →  the algorithm (uses those tools to validate skills)
        validator.py        →  the interface (orchestrates core + adds caching)
    
    This layered design is called "separation of concerns" —
    each layer has a specific role and doesn't mix responsibilities.
"""

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
    """
    Check if a single skill is backed up by the candidate's projects or experience.
    
    📚 TEACHING NOTE — The Core Algorithm:
        A skill listed on a resume means very little if it's not demonstrated.
        This function checks: "Does the candidate actually SHOW this skill
        somewhere in their projects or work experience?"
        
        Strategy (for each skill):
        1. Loop through every project
        2. Try exact match first (fast)
        3. If no exact match, try semantic similarity (AI-powered)
        4. If similarity >= threshold, the project "validates" the skill
        5. Also check the experience section the same way
        6. Return: validated? which projects? highest confidence score?
    
    Args:
        skill:      The skill to validate (e.g., "TensorFlow")
        projects:   List of project dicts with 'title' and 'description' keys
        experience: Full experience section text
        threshold:  Minimum similarity score to count as validated (default 0.6 = 60%)
        
    Returns:
        Tuple of:
        - is_validated (bool): True if skill is backed by at least one project/experience
        - matching_projects (List[str]): Names of projects that demonstrate this skill
        - max_similarity (float): Highest confidence score found (0.0–1.0)
        
    📚 TEACHING NOTE — What is a Tuple?
        A Tuple is like a list, but immutable (can't be changed after creation).
        We use it here to return 3 values at once from one function call.
        Callers unpack it like: is_valid, projects, score = validate_skill_against_projects(...)
    """
    matching_projects = []  # Will store names of projects that validate this skill
    max_similarity = 0.0    # Track the highest confidence score found
    
    # -----------------------------------------------
    # Step 1: Check each project
    # -----------------------------------------------
    for project in projects:
        # Combine title and description into one string for better matching
        # A skill might appear in the title OR the description
        project_text = f"{project.get('title', '')} {project.get('description', '')}"
        # .get('title', '') safely returns '' if 'title' key doesn't exist
        
        # Fast path: Try exact keyword match first
        if exact_skill_match(skill, project_text):
            matching_projects.append(project.get('title', 'Untitled Project'))
            max_similarity = 1.0  # Exact match = 100% confidence
            continue  # Skip semantic check — no need, already validated
        
        # Slow path: Exact match failed → try AI semantic similarity
        similarity = calculate_semantic_similarity(skill, project_text, embedder)
        max_similarity = max(max_similarity, similarity)  # Keep the highest score
        
        # If similarity meets or exceeds the threshold → this project validates the skill
        if similarity >= threshold:
            matching_projects.append(project.get('title', 'Untitled Project'))
    
    # -----------------------------------------------
    # Step 2: Also check the experience section
    # Experience is treated as one big text block (not split per job)
    # -----------------------------------------------
    if experience:  # Only check if experience text is provided
        if exact_skill_match(skill, experience):
            # Skill found explicitly in experience text
            if 'Experience Section' not in matching_projects:
                matching_projects.append('Experience Section')
            max_similarity = 1.0
        else:
            # Try semantic similarity on the experience text
            similarity = calculate_semantic_similarity(skill, experience, embedder)
            max_similarity = max(max_similarity, similarity)
            
            if similarity >= threshold and 'Experience Section' not in matching_projects:
                matching_projects.append('Experience Section')
                # Guard: 'not in' prevents duplicates if already added above
    
    # -----------------------------------------------
    # Step 3: Determine final validation result
    # -----------------------------------------------
    is_validated = len(matching_projects) > 0  # Validated if at least one match found
    
    return is_validated, matching_projects, max_similarity


def _compute_skill_validation(
    skills: List[str],
    projects: List[Dict[str, str]],
    experience: str,
    embedder: SentenceTransformer,
    threshold: float
) -> Dict:
    """
    Run validation for ALL skills and compile the full results report.
    
    📚 TEACHING NOTE — This is the "main loop" of the validator:
        For each skill in the resume's skills list, it calls
        validate_skill_against_projects() and collects results.
        
        At the end, it calculates:
        - validation_percentage: What % of skills have evidence
        - validation_score: Converts percentage to points (out of 15)
        
    📚 TEACHING NOTE — Early Return Pattern (Guard Clause):
        The first if-block checks for empty skills list and returns immediately.
        This avoids running the whole loop on empty data.
        It also prevents division by zero (can't divide by 0 skills).
        Always check edge cases at the TOP of a function — it makes the
        happy-path code below cleaner and easier to read.
    
    Returns:
        Dict with keys: validated_skills, unvalidated_skills,
                        validation_percentage, skill_project_mapping, validation_score
    """
    validated_skills = []       # Skills with supporting evidence
    unvalidated_skills = []     # Skills with no supporting evidence
    skill_project_mapping = {}  # Maps each skill → list of projects that demonstrate it
    
    # Guard clause: handle empty input gracefully
    if not skills:
        return {
            "validated_skills": [],
            "unvalidated_skills": [],
            "validation_percentage": 0.0,
            "skill_project_mapping": {},
            "validation_score": 0.0
        }
    
    # Main loop: validate each skill one by one
    for skill in skills:
        is_validated, matching_projects, similarity = validate_skill_against_projects(
            skill, projects, experience, embedder, threshold
        )
        
        if is_validated:
            # Skill has evidence — store with details
            validated_skills.append({
                "skill": skill,
                "projects": matching_projects,  # Which projects demonstrate this skill
                "similarity": similarity         # Confidence score
            })
            skill_project_mapping[skill] = matching_projects
        else:
            # No evidence found for this skill
            unvalidated_skills.append(skill)
            skill_project_mapping[skill] = []  # Empty list = no matching projects
    
    # Calculate what percentage of skills are validated
    # Guard against division by zero with 'if skills' check
    validation_percentage = len(validated_skills) / len(skills) if skills else 0.0
    
    # ============================================================
    # 📚 TEACHING NOTE — Scoring Formula:
    # Skill validation contributes 15 points to the total ATS score.
    # validation_percentage is 0.0 to 1.0, so:
    #   0% validated  → 0.0 × 15 = 0 points
    #   50% validated → 0.5 × 15 = 7.5 points
    #   100% validated→ 1.0 × 15 = 15 points (max)
    # ============================================================
    validation_score = validation_percentage * 15.0
    
    return {
        "validated_skills": validated_skills,       # List of dicts with skill + project details
        "unvalidated_skills": unvalidated_skills,   # List of skill strings with no evidence
        "validation_percentage": validation_percentage,
        "skill_project_mapping": skill_project_mapping,
        "validation_score": validation_score
    }


# ============================================================
# 📚 TEACHING NOTE — ⚠️ Incomplete / Dead Code
# This function was clearly intended to be a cached version of
# _compute_skill_validation(), but it was never finished.
# It returns None, which would crash any code that calls it.
#
# The @st.cache_data decorator is set up correctly, but the
# actual logic inside is missing (just returns None).
#
# RECOMMENDATION FOR STUDENTS:
# Either complete this function or delete it.
# Leaving dead code like this causes confusion and could introduce bugs.
# 
# A completed version would look like:
#   skills = list(skills_tuple)
#   projects = json.loads(projects_json)
#   return _compute_skill_validation(skills, projects, experience_text, _embedder, threshold)
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def _cached_skill_validation(
    skills_tuple: tuple,    # tuple instead of list because lists can't be hashed for cache keys
    projects_json: str,     # JSON string instead of dict (dicts can't be hashed either)
    experience_hash: str,   # Hash of experience text (used as cache key)
    threshold: float,
    _embedder               # Underscore prefix: Streamlit ignores this when creating cache key
) -> Dict:
    """
    ⚠️ INCOMPLETE FUNCTION — Currently returns None (bug).
    Intended to be a cached wrapper around _compute_skill_validation().
    
    📚 TEACHING NOTE — Why convert list → tuple and dict → JSON string?
        Streamlit's @st.cache_data needs to create a "hash" of inputs
        to use as a cache key. But lists and dicts are "unhashable" in Python.
        The workaround: convert them to hashable types:
            list  → tuple  (immutable, hashable)
            dict  → JSON string (strings are hashable)
    """
    import json
    skills = list(skills_tuple)    # Convert back from tuple to list
    projects = json.loads(projects_json)  # Convert back from JSON string to list of dicts
    
    # ⚠️ BUG: This returns None instead of calling _compute_skill_validation()
    return None