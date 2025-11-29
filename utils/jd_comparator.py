"""
Job Description Comparator Module for ATS Resume Scorer

This module handles comparison between resumes and job descriptions including
semantic similarity calculation, keyword matching, and skills gap analysis.
"""

import numpy as np
from typing import Dict, List, Set, Tuple
from sentence_transformers import SentenceTransformer
import spacy


def calculate_semantic_similarity(
    resume_text: str,
    jd_text: str,
    embedder: SentenceTransformer
) -> float:
    """
    Calculates semantic similarity between resume and job description using embeddings.
    
    Args:
        resume_text: Resume text content
        jd_text: Job description text content
        embedder: Loaded SentenceTransformer model
        
    Returns:
        Semantic similarity score between 0.0 and 1.0
        
    Validates:
        - Requirements 10.2: Calculate semantic similarity between resume and JD
    """
    # Limit text length for performance
    resume_text = resume_text[:5000]
    jd_text = jd_text[:5000]
    
    # Generate embeddings
    resume_embedding = embedder.encode(resume_text, convert_to_tensor=False)
    jd_embedding = embedder.encode(jd_text, convert_to_tensor=False)
    
    # Calculate cosine similarity
    similarity = np.dot(resume_embedding, jd_embedding) / (
        np.linalg.norm(resume_embedding) * np.linalg.norm(jd_embedding)
    )
    
    # Ensure result is between 0 and 1
    similarity = float(np.clip(similarity, 0.0, 1.0))
    
    return similarity


def identify_matched_keywords(
    resume_keywords: List[str],
    jd_keywords: List[str]
) -> List[str]:
    """
    Identifies keywords present in both resume and job description.
    
    Args:
        resume_keywords: List of keywords from resume
        jd_keywords: List of keywords from job description
        
    Returns:
        List of keywords present in both documents
        
    Validates:
        - Requirements 10.3: Identify keywords present in both resume and JD
    """
    # Convert to sets for efficient intersection
    resume_set = set(kw.lower() for kw in resume_keywords)
    jd_set = set(kw.lower() for kw in jd_keywords)
    
    # Find intersection
    matched = resume_set.intersection(jd_set)
    
    return sorted(list(matched))


def identify_missing_keywords(
    resume_keywords: List[str],
    jd_keywords: List[str],
    top_n: int = 15
) -> List[str]:
    """
    Identifies critical keywords present in JD but missing from resume.
    
    Args:
        resume_keywords: List of keywords from resume
        jd_keywords: List of keywords from job description
        top_n: Maximum number of missing keywords to return
        
    Returns:
        List of keywords present in JD but missing from resume
        
    Validates:
        - Requirements 10.4: Identify critical keywords in JD but missing from resume
    """
    # Convert to sets for efficient difference
    resume_set = set(kw.lower() for kw in resume_keywords)
    jd_set = set(kw.lower() for kw in jd_keywords)
    
    # Find keywords in JD but not in resume
    missing = jd_set - resume_set
    
    # Return top N (prioritize by order in JD keywords list)
    missing_ordered = [kw for kw in jd_keywords if kw.lower() in missing]
    
    return missing_ordered[:top_n]


def analyze_skills_gap(
    resume_skills: List[str],
    jd_text: str,
    nlp: spacy.Language
) -> List[str]:
    """
    Analyzes skills gap between resume and job description requirements.
    
    Args:
        resume_skills: List of skills from resume
        jd_text: Job description text content
        nlp: Loaded spaCy Language model
        
    Returns:
        List of skills mentioned in JD but not in resume
        
    Validates:
        - Requirements 10.5: Skills gap analysis
    """
    # Extract skills-like terms from JD
    doc = nlp(jd_text[:5000])
    
    jd_skills = set()
    
    # Extract technical terms and requirements
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
            jd_skills.add(ent.text.lower())
    
    # Extract noun chunks that might be skills
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        # Filter for skill-like phrases (2-4 words)
        if 1 <= len(chunk_text.split()) <= 4:
            jd_skills.add(chunk_text)
    
    # Convert resume skills to lowercase for comparison
    resume_skills_lower = set(skill.lower() for skill in resume_skills)
    
    # Find skills in JD but not in resume
    skills_gap = []
    for jd_skill in jd_skills:
        # Check if JD skill is not in resume skills
        if not any(jd_skill in resume_skill or resume_skill in jd_skill 
                   for resume_skill in resume_skills_lower):
            skills_gap.append(jd_skill)
    
    return sorted(skills_gap)[:20]  # Return top 20


def calculate_match_percentage(
    resume_keywords: List[str],
    jd_keywords: List[str],
    semantic_similarity: float
) -> float:
    """
    Calculates overall match percentage between resume and job description.
    Combines keyword overlap with semantic similarity.
    
    Args:
        resume_keywords: List of keywords from resume
        jd_keywords: List of keywords from job description
        semantic_similarity: Semantic similarity score (0.0-1.0)
        
    Returns:
        Match percentage between 0 and 100
        
    Validates:
        - Requirements 10.5: Calculate match percentage based on keyword overlap and semantic similarity
    """
    if not jd_keywords:
        return 0.0
    
    # Calculate keyword overlap percentage
    matched_keywords = identify_matched_keywords(resume_keywords, jd_keywords)
    keyword_overlap = len(matched_keywords) / len(jd_keywords) if jd_keywords else 0.0
    
    # Combine keyword overlap (60%) and semantic similarity (40%)
    match_percentage = (keyword_overlap * 0.6 + semantic_similarity * 0.4) * 100
    
    # Ensure result is between 0 and 100
    match_percentage = float(np.clip(match_percentage, 0.0, 100.0))
    
    return match_percentage


def _perform_jd_comparison(
    resume_text: str,
    resume_keywords: List[str],
    resume_skills: List[str],
    jd_text: str,
    jd_keywords: List[str],
    embedder: SentenceTransformer,
    nlp: spacy.Language
) -> Dict:
    """
    Internal function to perform JD comparison.
    
    Args:
        resume_text: Full resume text
        resume_keywords: Extracted keywords from resume
        resume_skills: Extracted skills from resume
        jd_text: Full job description text
        jd_keywords: Extracted keywords from job description
        embedder: Loaded SentenceTransformer model
        nlp: Loaded spaCy Language model
        
    Returns:
        Dictionary containing comparison results
    """
    # Calculate semantic similarity
    semantic_similarity = calculate_semantic_similarity(resume_text, jd_text, embedder)
    
    # Identify matched and missing keywords
    matched_keywords = identify_matched_keywords(resume_keywords, jd_keywords)
    missing_keywords = identify_missing_keywords(resume_keywords, jd_keywords)
    
    # Analyze skills gap
    skills_gap = analyze_skills_gap(resume_skills, jd_text, nlp)
    
    # Calculate overall match percentage
    match_percentage = calculate_match_percentage(
        resume_keywords, 
        jd_keywords, 
        semantic_similarity
    )
    
    return {
        'semantic_similarity': semantic_similarity,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords,
        'skills_gap': skills_gap,
        'match_percentage': match_percentage
    }


# Import streamlit for caching
import streamlit as st
import hashlib


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_jd_comparison(
    resume_hash: str,
    jd_hash: str,
    resume_text: str,
    resume_keywords_tuple: tuple,
    resume_skills_tuple: tuple,
    jd_text: str,
    jd_keywords_tuple: tuple,
    _embedder,
    _nlp
) -> Dict:
    """
    Cached version of JD comparison.
    
    Args:
        resume_hash: Hash of resume text
        jd_hash: Hash of JD text
        resume_text: Full resume text
        resume_keywords_tuple: Tuple of resume keywords
        resume_skills_tuple: Tuple of resume skills
        jd_text: Full job description text
        jd_keywords_tuple: Tuple of JD keywords
        _embedder: SentenceTransformer model (excluded from hash)
        _nlp: spaCy model (excluded from hash)
        
    Returns:
        Dictionary containing comparison results
        
    Validates:
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    return _perform_jd_comparison(
        resume_text=resume_text,
        resume_keywords=list(resume_keywords_tuple),
        resume_skills=list(resume_skills_tuple),
        jd_text=jd_text,
        jd_keywords=list(jd_keywords_tuple),
        embedder=_embedder,
        nlp=_nlp
    )


def compare_resume_with_jd(
    resume_text: str,
    resume_keywords: List[str],
    resume_skills: List[str],
    jd_text: str,
    jd_keywords: List[str],
    embedder: SentenceTransformer,
    nlp: spacy.Language,
    use_cache: bool = True
) -> Dict:
    """
    Performs comprehensive comparison between resume and job description.
    
    Args:
        resume_text: Full resume text
        resume_keywords: Extracted keywords from resume
        resume_skills: Extracted skills from resume
        jd_text: Full job description text
        jd_keywords: Extracted keywords from job description
        embedder: Loaded SentenceTransformer model
        nlp: Loaded spaCy Language model
        use_cache: Whether to use caching for results (default: True)
        
    Returns:
        Dictionary containing comparison results:
        {
            'semantic_similarity': float (0.0-1.0),
            'matched_keywords': List[str],
            'missing_keywords': List[str],
            'skills_gap': List[str],
            'match_percentage': float (0-100)
        }
        
    Validates:
        - Requirements 10.1: Extract keywords from both documents
        - Requirements 10.2: Calculate semantic similarity
        - Requirements 10.3: Identify matched keywords
        - Requirements 10.4: Identify missing keywords
        - Requirements 10.5: Calculate match percentage and skills gap
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    if use_cache:
        # Generate hashes for caching
        resume_hash = hashlib.sha256(resume_text.encode('utf-8')).hexdigest()
        jd_hash = hashlib.sha256(jd_text.encode('utf-8')).hexdigest()
        
        return _cached_jd_comparison(
            resume_hash=resume_hash,
            jd_hash=jd_hash,
            resume_text=resume_text,
            resume_keywords_tuple=tuple(resume_keywords),
            resume_skills_tuple=tuple(resume_skills),
            jd_text=jd_text,
            jd_keywords_tuple=tuple(jd_keywords),
            _embedder=embedder,
            _nlp=nlp
        )
    else:
        return _perform_jd_comparison(
            resume_text=resume_text,
            resume_keywords=resume_keywords,
            resume_skills=resume_skills,
            jd_text=jd_text,
            jd_keywords=jd_keywords,
            embedder=embedder,
            nlp=nlp
        )
