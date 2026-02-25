"""
JD Comparator Module
Compares a resume against a job description and calculates a match percentage.

📌 TEACHING NOTE — What does this file do?
    This is the "Job Description Matching" engine — one of the most valuable
    features of any ATS scorer.

    When a candidate uploads both a resume AND a job description, this module:
    1. Calculates how semantically similar the two documents are (AI-powered)
    2. Finds which keywords appear in BOTH (direct overlap)
    3. Finds which JD keywords are MISSING from the resume (gaps to fill)
    4. Identifies skills the JD mentions that the resume doesn't (skill gaps)
    5. Combines all of this into a single "match percentage"

    📌 Match Percentage Formula:
        match% = (keyword_overlap × 0.6) + (semantic_similarity × 0.4) × 100

        60% weight on keyword overlap (what ATS systems actually check)
        40% weight on semantic similarity (overall meaning match)

    Files in this directory use a consistent pattern:
        _perform_*()        → pure logic, no caching
        _cached_*()         → @st.cache_data wrapper
        compare_*() / detect_*() → public entry point with cache decision
"""

import numpy as np
from typing import Dict, List, Set, Tuple
from sentence_transformers import SentenceTransformer
import spacy
import streamlit as st
import hashlib


def calculate_semantic_similarity(
    resume_text: str,
    jd_text: str,
    embedder: SentenceTransformer
) -> float:
    """
    Use AI embeddings to measure how similar the resume and JD are in MEANING.

    📌 TEACHING NOTE — Why truncate to 5000 characters?
        SentenceTransformer has a maximum input length (usually 512 tokens,
        roughly 400-500 words). For longer texts, it silently truncates anyway.

        By explicitly slicing to 5000 chars (~750 words), we:
        1. Make the truncation intentional and visible in the code
        2. Reduce memory usage and speed up encoding
        3. Focus on the most important part (beginning of each document)

        This is a trade-off: we might miss skills mentioned later in a long resume.
        A more sophisticated approach would split the text into chunks and
        average the similarity scores.

    📌 TEACHING NOTE — np.clip vs manual min/max:
        np.clip(value, 0.0, 1.0) is equivalent to min(1.0, max(0.0, value))
        but cleaner to read and works on arrays too.
        Cosine similarity can produce values like -0.001 or 1.0001 due to
        floating-point math — clipping keeps us in the valid [0, 1] range.

    Args:
        resume_text: Full resume text (truncated to 5000 chars)
        jd_text: Full job description text (truncated to 5000 chars)
        embedder: Loaded SentenceTransformer model

    Returns:
        Float between 0.0 (no similarity) and 1.0 (identical meaning)
    """
    # Truncate both documents to avoid memory issues and respect model limits
    resume_text = resume_text[:5000]
    jd_text = jd_text[:5000]

    # Convert both texts to numerical vectors (embeddings)
    # convert_to_tensor=False → return numpy array (faster for cosine calc)
    resume_embedding = embedder.encode(resume_text, convert_to_tensor=False)
    jd_embedding = embedder.encode(jd_text, convert_to_tensor=False)

    # Cosine Similarity formula:
    # dot_product(A, B) / (magnitude(A) × magnitude(B))
    # Result: 1.0 = same direction (same meaning), 0.0 = perpendicular (unrelated)
    similarity = np.dot(resume_embedding, jd_embedding) / (
        np.linalg.norm(resume_embedding) * np.linalg.norm(jd_embedding)
    )

    # Clamp to [0.0, 1.0] — floating point math can produce tiny out-of-range values
    similarity = float(np.clip(similarity, 0.0, 1.0))
    return similarity


def identify_matched_keywords(
    resume_keywords: List[str],
    jd_keywords: List[str]
) -> List[str]:
    """
    Find keywords that appear in BOTH the resume and the job description.

    📌 TEACHING NOTE — Set Intersection:
        Python sets have a built-in intersection() method:
            {1, 2, 3}.intersection({2, 3, 4}) → {2, 3}

        We convert keyword lists to sets because:
        1. Sets have O(1) lookup (vs O(n) for lists)
        2. intersection() is a single operation (vs nested loops)
        3. Sets automatically handle duplicates

        We lowercase both sets before intersecting to make matching
        case-insensitive: "Python" and "python" should count as a match.

    📌 Example:
        resume_keywords = ["Python", "React", "AWS"]
        jd_keywords     = ["python", "django", "aws", "docker"]
        matched         = ["aws", "python"]  (sorted alphabetically)

    Args:
        resume_keywords: Keywords extracted from resume
        jd_keywords: Keywords extracted from job description

    Returns:
        Sorted list of keywords found in both documents (lowercase)
    """
    resume_set = set(kw.lower() for kw in resume_keywords)
    jd_set = set(kw.lower() for kw in jd_keywords)

    # Set intersection: only elements present in BOTH sets
    matched = resume_set.intersection(jd_set)

    return sorted(list(matched))  # sorted() for consistent ordering


def identify_missing_keywords(
    resume_keywords: List[str],
    jd_keywords: List[str],
    top_n: int = 15
) -> List[str]:
    """
    Find keywords the JD mentions that are MISSING from the resume.

    📌 TEACHING NOTE — Set Difference:
        jd_set - resume_set → elements in jd_set that are NOT in resume_set
        This is set DIFFERENCE (also called set subtraction).

        {A, B, C} - {B, C, D} = {A}  (A is in first but not second)

        For the candidate, these are the "gaps to fill" — words they should
        try to add to their resume to improve the match score.

    📌 TEACHING NOTE — Preserving JD order:
        After finding the missing set, we rebuild the list by iterating
        the ORIGINAL jd_keywords list and keeping only the missing ones.

        Why? Sets don't preserve order. By iterating jd_keywords (which is
        ordered by importance/frequency), we get missing keywords in the
        order they appeared in the JD — more important ones first.

        This is a useful trick: use a set for fast lookups but an ordered
        list to control output order.

    Args:
        resume_keywords: Keywords from resume
        jd_keywords: Keywords from JD
        top_n: Maximum number of missing keywords to return (default 15)

    Returns:
        Up to top_n missing keywords, ordered by their position in the JD
    """
    resume_set = set(kw.lower() for kw in resume_keywords)
    jd_set = set(kw.lower() for kw in jd_keywords)

    # Set difference: JD keywords NOT found in resume
    missing = jd_set - resume_set

    # Rebuild in JD order (preserves importance ordering from the JD)
    missing_ordered = [kw for kw in jd_keywords if kw.lower() in missing]

    return missing_ordered[:top_n]  # Cap to avoid overwhelming the user


def analyze_skills_gap(
    resume_skills: List[str],
    jd_text: str,
    nlp: spacy.Language
) -> List[str]:
    """
    Use spaCy NLP to extract skills from the JD and identify gaps vs resume.

    📌 TEACHING NOTE — Two extraction methods combined:

        Method 1: Named Entity Recognition (NER)
            spaCy identifies named entities and their types.
            We look for:
            - PRODUCT → technology names (TensorFlow, PostgreSQL)
            - ORG     → company/framework names (Google, Spring)
            - LANGUAGE → programming languages (Python, Java)

        Method 2: Noun Chunks
            spaCy identifies noun phrases (groups of words centered on a noun).
            Examples: "machine learning", "project management", "REST API"
            We keep chunks of 1-4 words (skills are rarely longer).

        Combining both methods captures more skills than either alone.

    📌 TEACHING NOTE — Partial match logic:
        When checking if a resume skill covers a JD skill, we use:
            jd_skill in resume_skill OR resume_skill in jd_skill

        This handles partial overlaps:
        - JD says "machine learning", resume says "deep learning and machine learning"
          → jd_skill ("machine learning") IS in resume_skill → not a gap ✅
        - JD says "python", resume says "python developer"
          → resume_skill ("python") IS in jd_skill... wait, actually jd_skill
          is "python" and resume_skill is "python developer" so the check works.

    📌 TEACHING NOTE — [:5000] truncation again:
        Same reason as calculate_semantic_similarity() — respect model limits.

    Args:
        resume_skills: Skills list from resume
        jd_text: Full job description text
        nlp: Loaded spaCy model

    Returns:
        Sorted list of up to 20 skills mentioned in JD but not in resume
    """
    # Process only first 5000 chars to respect spaCy's practical limits
    doc = nlp(jd_text[:5000])

    jd_skills = set()

    # Method 1: Named Entity Recognition
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
            jd_skills.add(ent.text.lower())

    # Method 2: Noun chunks (multi-word skill phrases)
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        # Keep only reasonable-length phrases (1-4 words = likely a skill)
        if 1 <= len(chunk_text.split()) <= 4:
            jd_skills.add(chunk_text)

    # Check each JD skill against resume skills
    resume_skills_lower = set(skill.lower() for skill in resume_skills)

    skills_gap = []
    for jd_skill in jd_skills:
        # Partial match: neither is substring of the other → genuine gap
        if not any(
            jd_skill in resume_skill or resume_skill in jd_skill
            for resume_skill in resume_skills_lower
        ):
            skills_gap.append(jd_skill)

    # Sort alphabetically, cap at 20 to keep UI manageable
    return sorted(skills_gap)[:20]


def calculate_match_percentage(
    resume_keywords: List[str],
    jd_keywords: List[str],
    semantic_similarity: float
) -> float:
    """
    Calculate the final match percentage combining keyword overlap and semantic similarity.

    📌 TEACHING NOTE — Weighted Average Formula:
        match% = (keyword_overlap × 0.6 + semantic_similarity × 0.4) × 100

        Why 60/40 split?
        Real ATS systems heavily rely on EXACT keyword matching.
        Recruiters also search for specific keywords.
        So we weight keyword overlap (0.6) higher than AI similarity (0.4).

        keyword_overlap = matched_keywords / total_jd_keywords
        e.g., 8 of 20 JD keywords found → 0.40 overlap

        With semantic_similarity = 0.75:
        match% = (0.40 × 0.6 + 0.75 × 0.4) × 100
               = (0.24 + 0.30) × 100
               = 54%

    📌 TEACHING NOTE — np.clip for safe range:
        After multiplication, floating-point errors could push the result
        slightly outside [0, 100]. np.clip guarantees it stays in range.

    Args:
        resume_keywords: All keywords from resume
        jd_keywords: All keywords from JD
        semantic_similarity: Float 0.0-1.0 from calculate_semantic_similarity()

    Returns:
        Match percentage float between 0.0 and 100.0
    """
    if not jd_keywords:
        return 0.0  # Guard: can't calculate match if JD has no keywords

    matched_keywords = identify_matched_keywords(resume_keywords, jd_keywords)

    # Keyword overlap ratio: 0.0 to 1.0
    keyword_overlap = len(matched_keywords) / len(jd_keywords) if jd_keywords else 0.0

    # Weighted combination: 60% keyword overlap, 40% semantic similarity
    match_percentage = (keyword_overlap * 0.6 + semantic_similarity * 0.4) * 100

    # Clamp to valid percentage range
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
    Internal function — run the full JD comparison pipeline (no caching).

    📌 TEACHING NOTE — Pipeline Pattern:
        This function calls each analysis step in sequence and assembles
        the results into one dict. Each step is independent and testable
        on its own. This is a simple data pipeline:

        resume + JD
            ↓ calculate_semantic_similarity()  → similarity score
            ↓ identify_matched_keywords()       → matched list
            ↓ identify_missing_keywords()       → missing list
            ↓ analyze_skills_gap()              → gap list
            ↓ calculate_match_percentage()      → final score
            ↓ return combined dict

    📌 TEACHING NOTE — Underscore prefix = private:
        The _ prefix signals this is an internal function.
        External code should call compare_resume_with_jd() instead,
        which handles caching logic before delegating here.

    Returns:
        Dict with semantic_similarity, matched_keywords, missing_keywords,
        skills_gap, and match_percentage
    """
    semantic_similarity  = calculate_semantic_similarity(resume_text, jd_text, embedder)
    matched_keywords     = identify_matched_keywords(resume_keywords, jd_keywords)
    missing_keywords     = identify_missing_keywords(resume_keywords, jd_keywords)
    skills_gap           = analyze_skills_gap(resume_skills, jd_text, nlp)
    match_percentage     = calculate_match_percentage(resume_keywords, jd_keywords, semantic_similarity)

    return {
        'semantic_similarity': semantic_similarity,
        'matched_keywords':    matched_keywords,
        'missing_keywords':    missing_keywords,
        'skills_gap':          skills_gap,
        'match_percentage':    match_percentage
    }


# ============================================================
# 📌 TEACHING NOTE — Why are imports at the bottom of the file?
#   streamlit and hashlib are imported here, not at the top.
#   This is unusual and generally considered bad practice
#   (PEP 8 says all imports should be at the top of the file).
#
#   It works because Python imports are lazy — the import only
#   executes when the line is reached. But it makes the file
#   harder to read (you can't see all dependencies at a glance).
#
#   ✅ Suggested Fix: Move these to the top of the file with the other imports.
# ============================================================


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_jd_comparison(
    resume_hash: str,
    jd_hash: str,
    resume_text: str,
    resume_keywords_tuple: tuple,   # tuple (not list) — must be hashable for cache key
    resume_skills_tuple: tuple,     # tuple (not list)
    jd_text: str,
    jd_keywords_tuple: tuple,       # tuple (not list)
    _embedder,                      # excluded from cache key (underscore prefix)
    _nlp                            # excluded from cache key
) -> Dict:
    """
    Cached wrapper around _perform_jd_comparison().

    📌 TEACHING NOTE — Why tuples instead of lists?
        @st.cache_data builds a cache key from all function arguments.
        Lists are NOT hashable (mutable), so Streamlit can't hash them.
        Tuples ARE hashable (immutable), so they work as cache key components.

        Caller converts: list → tuple before calling this function.
        We convert back: tuple → list before passing to _perform_jd_comparison().

    📌 TEACHING NOTE — Two hash params (resume_hash, jd_hash):
        The cache key is built from ALL parameters.
        resume_hash and jd_hash are SHA-256 strings of the full texts.
        We pass both so the cache key changes if either document changes.
        resume_text and jd_text are also passed — for the actual computation,
        not the cache key (the hashes already uniquely identify them).

    Args:
        resume_hash: SHA-256 hash of resume text (cache key component)
        jd_hash: SHA-256 hash of JD text (cache key component)
        ... (other args for computation)
    """
    return _perform_jd_comparison(
        resume_text=resume_text,
        resume_keywords=list(resume_keywords_tuple),  # Convert back from tuple to list
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
    Public entry point — compare resume against job description.

    📌 TEACHING NOTE — The Three-Layer Pattern (consistent across this codebase):
        Layer 1 (this function):   public API, decides whether to use cache
        Layer 2 (_cached_*):       @st.cache_data wrapper, handles serialization
        Layer 3 (_perform_*):      pure logic, no caching concerns

        This same pattern appears in detector.py, grammar.py, and validator.py.
        Consistent patterns across a codebase make it much easier to maintain
        and onboard new developers.

    📌 TEACHING NOTE — SHA-256 for cache keys:
        We hash the full texts (which can be thousands of characters) down to
        64-character strings. These become part of the cache key.
        Same resume + same JD = same hashes = cache hit (instant result).
        Changed resume or JD = different hashes = cache miss (recompute).

    Args:
        resume_text: Full resume content
        resume_keywords: Keywords extracted from resume
        resume_skills: Skills list from resume
        jd_text: Full job description content
        jd_keywords: Keywords extracted from job description
        embedder: Loaded SentenceTransformer model
        nlp: Loaded spaCy model
        use_cache: True for normal use, False for testing/debugging

    Returns:
        Dict with match_percentage, matched_keywords, missing_keywords, skills_gap
    """
    if use_cache:
        # Generate stable hash keys for cache lookup
        resume_hash = hashlib.sha256(resume_text.encode('utf-8')).hexdigest()
        jd_hash     = hashlib.sha256(jd_text.encode('utf-8')).hexdigest()

        return _cached_jd_comparison(
            resume_hash=resume_hash,
            jd_hash=jd_hash,
            resume_text=resume_text,
            resume_keywords_tuple=tuple(resume_keywords),  # list → tuple for hashability
            resume_skills_tuple=tuple(resume_skills),
            jd_text=jd_text,
            jd_keywords_tuple=tuple(jd_keywords),
            _embedder=embedder,
            _nlp=nlp
        )
    else:
        # Skip cache — run directly (useful for tests or forced refresh)
        return _perform_jd_comparison(
            resume_text=resume_text,
            resume_keywords=resume_keywords,
            resume_skills=resume_skills,
            jd_text=jd_text,
            jd_keywords=jd_keywords,
            embedder=embedder,
            nlp=nlp
        )