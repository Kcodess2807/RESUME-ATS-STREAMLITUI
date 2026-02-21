import numpy as np
from typing import Dict, List, Set, Tuple
from sentence_transformers import SentenceTransformer
import spacy


def calculate_semantic_similarity(resume_text: str, jd_text: str, embedder:
    SentenceTransformer) ->float:
    resume_text = resume_text[:5000]
    jd_text = jd_text[:5000]
    resume_embedding = embedder.encode(resume_text, convert_to_tensor=False)
    jd_embedding = embedder.encode(jd_text, convert_to_tensor=False)
    similarity = np.dot(resume_embedding, jd_embedding) / (np.linalg.norm(
        resume_embedding) * np.linalg.norm(jd_embedding))
    similarity = float(np.clip(similarity, 0.0, 1.0))
    return similarity


def identify_matched_keywords(resume_keywords: List[str], jd_keywords: List
    [str]) ->List[str]:
    resume_set = set(kw.lower() for kw in resume_keywords)
    jd_set = set(kw.lower() for kw in jd_keywords)
    matched = resume_set.intersection(jd_set)
    return sorted(list(matched))


def identify_missing_keywords(resume_keywords: List[str], jd_keywords: List
    [str], top_n: int=15) ->List[str]:
    resume_set = set(kw.lower() for kw in resume_keywords)
    jd_set = set(kw.lower() for kw in jd_keywords)
    missing = jd_set - resume_set
    missing_ordered = [kw for kw in jd_keywords if kw.lower() in missing]
    return missing_ordered[:top_n]


def analyze_skills_gap(resume_skills: List[str], jd_text: str, nlp: spacy.
    Language) ->List[str]:
    doc = nlp(jd_text[:5000])
    jd_skills = set()
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
            jd_skills.add(ent.text.lower())
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        if 1 <= len(chunk_text.split()) <= 4:
            jd_skills.add(chunk_text)
    resume_skills_lower = set(skill.lower() for skill in resume_skills)
    skills_gap = []
    for jd_skill in jd_skills:
        if not any(jd_skill in resume_skill or resume_skill in jd_skill for
            resume_skill in resume_skills_lower):
            skills_gap.append(jd_skill)
    return sorted(skills_gap)[:20]


def calculate_match_percentage(resume_keywords: List[str], jd_keywords:
    List[str], semantic_similarity: float) ->float:
    if not jd_keywords:
        return 0.0
    matched_keywords = identify_matched_keywords(resume_keywords, jd_keywords)
    keyword_overlap = len(matched_keywords) / len(jd_keywords
        ) if jd_keywords else 0.0
    match_percentage = (keyword_overlap * 0.6 + semantic_similarity * 0.4
        ) * 100
    match_percentage = float(np.clip(match_percentage, 0.0, 100.0))
    return match_percentage


def _perform_jd_comparison(resume_text: str, resume_keywords: List[str],
    resume_skills: List[str], jd_text: str, jd_keywords: List[str],
    embedder: SentenceTransformer, nlp: spacy.Language) ->Dict:
    semantic_similarity = calculate_semantic_similarity(resume_text,
        jd_text, embedder)
    matched_keywords = identify_matched_keywords(resume_keywords, jd_keywords)
    missing_keywords = identify_missing_keywords(resume_keywords, jd_keywords)
    skills_gap = analyze_skills_gap(resume_skills, jd_text, nlp)
    match_percentage = calculate_match_percentage(resume_keywords,
        jd_keywords, semantic_similarity)
    return {'semantic_similarity': semantic_similarity, 'matched_keywords':
        matched_keywords, 'missing_keywords': missing_keywords,
        'skills_gap': skills_gap, 'match_percentage': match_percentage}


import streamlit as st
import hashlib


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_jd_comparison(resume_hash: str, jd_hash: str, resume_text: str,
    resume_keywords_tuple: tuple, resume_skills_tuple: tuple, jd_text: str,
    jd_keywords_tuple: tuple, _embedder, _nlp) ->Dict:
    return _perform_jd_comparison(resume_text=resume_text, resume_keywords=
        list(resume_keywords_tuple), resume_skills=list(resume_skills_tuple
        ), jd_text=jd_text, jd_keywords=list(jd_keywords_tuple), embedder=
        _embedder, nlp=_nlp)


def compare_resume_with_jd(resume_text: str, resume_keywords: List[str],
    resume_skills: List[str], jd_text: str, jd_keywords: List[str],
    embedder: SentenceTransformer, nlp: spacy.Language, use_cache: bool=True
    ) ->Dict:
    if use_cache:
        resume_hash = hashlib.sha256(resume_text.encode('utf-8')).hexdigest()
        jd_hash = hashlib.sha256(jd_text.encode('utf-8')).hexdigest()
        return _cached_jd_comparison(resume_hash=resume_hash, jd_hash=
            jd_hash, resume_text=resume_text, resume_keywords_tuple=tuple(
            resume_keywords), resume_skills_tuple=tuple(resume_skills),
            jd_text=jd_text, jd_keywords_tuple=tuple(jd_keywords),
            _embedder=embedder, _nlp=nlp)
    else:
        return _perform_jd_comparison(resume_text=resume_text,
            resume_keywords=resume_keywords, resume_skills=resume_skills,
            jd_text=jd_text, jd_keywords=jd_keywords, embedder=embedder,
            nlp=nlp)
