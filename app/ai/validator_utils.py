"""
Validator Utilities Module
Provides foundational helper functions for skill validation.

📚 TEACHING NOTE — What belongs in a 'utils' file?
    'utils' (short for utilities) files contain small, reusable helper functions
    that are general enough to be used across multiple modules.
    Think of them as your "toolbox" — individual tools like a hammer or screwdriver.
    
    This file specifically provides:
    1. A way to load the AI embedding model
    2. A way to calculate how similar two texts are (semantic similarity)
    3. A simple exact-word match check
    
    These are used by validator_core.py to do the actual skill validation.
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np  # NumPy = fast numerical computing library (used for math operations on arrays)


# ============================================================
# 📚 TEACHING NOTE — Duplicate Code Warning ⚠️
# This load_embedder() function does the SAME thing as
# load_sentence_transformer() in ai_helper.py.
# Having the same logic in two places is called "code duplication"
# and violates the DRY principle: Don't Repeat Yourself.
#
# Better approach: import and call ai_helper.load_sentence_transformer()
# here instead of defining a new function.
# This is a good discussion point for students about code organization.
# ============================================================
@st.cache_resource
def load_embedder(model_name: str = "all-MiniLM-L6-v2"):
    """
    Load and cache the SentenceTransformer embedding model.
    
    📚 TEACHING NOTE — What is an "embedder"?
        An embedder converts text into a numerical vector (a list of numbers).
        For example:
            "Python developer"  →  [0.12, -0.34, 0.87, ..., 0.21]  (384 numbers)
            "coded in Python"   →  [0.14, -0.31, 0.83, ..., 0.19]  (384 numbers)
        
        The two vectors are very similar (close together in mathematical space)
        even though the words are different. This is how semantic similarity works.
        
        'all-MiniLM-L6-v2':
            - 'MiniLM' = a smaller, faster version of large language models
            - 'L6' = 6 layers deep (architecture detail)
            - 'v2' = version 2
            - Produces 384-dimensional vectors
            - ~80MB model file, downloads automatically on first use
    """
    try:
        embedder = SentenceTransformer(model_name)
        return embedder
    except Exception as e:
        # If loading fails, show a clear error and crash gracefully
        st.error(f"Failed to load Sentence-Transformers model: {e}")
        raise  # Re-raise so the calling code knows something went wrong


def calculate_semantic_similarity(
    skill: str,
    text: str,
    embedder: SentenceTransformer
) -> float:
    """
    Calculate how semantically similar a skill is to a piece of text.
    
    📚 TEACHING NOTE — Cosine Similarity (core concept!):
        This function uses "cosine similarity" — a mathematical measure
        of how similar two vectors are, regardless of their magnitude.
        
        Formula:
            similarity = (A · B) / (|A| × |B|)
            
        Where:
            A · B    = dot product (how much two vectors point in the same direction)
            |A|, |B| = magnitude/length of each vector (normalized to account for length)
        
        Result: always between 0.0 (completely different) and 1.0 (identical meaning)
        
        Real-world analogy: Imagine pointing two arrows in space.
        Cosine similarity measures how parallel those arrows are.
        Parallel (same direction) = similar meaning.
        Perpendicular (90°) = unrelated meaning.
        
        Examples of expected scores:
            "Python" vs "Built Python scripts"         → ~0.75 (high similarity)
            "Python" vs "Managed team of 10 people"   → ~0.15 (low similarity)
            "Python" vs "Python"                       → ~1.00 (identical)
    
    Args:
        skill: The skill to check (e.g., "React.js")
        text: The text to check against (e.g., project description)
        embedder: The loaded SentenceTransformer model
        
    Returns:
        Float between 0.0 and 1.0 — higher means more similar
    """
    # Guard clause — if either input is empty, similarity is 0 by definition
    if not skill or not text:
        return 0.0
    
    try:
        # Step 1: Convert both texts into numerical vectors
        # convert_to_tensor=False → return plain NumPy array (not PyTorch tensor)
        # NumPy arrays are simpler to work with for math operations
        skill_embedding = embedder.encode(skill, convert_to_tensor=False)
        text_embedding = embedder.encode(text, convert_to_tensor=False)
        
        # Step 2: Calculate cosine similarity
        # np.dot() = dot product of two vectors (multiply element-by-element, then sum)
        # np.linalg.norm() = vector magnitude (length) — used to normalize
        similarity = np.dot(skill_embedding, text_embedding) / (
            np.linalg.norm(skill_embedding) * np.linalg.norm(text_embedding)
        )
        
        # Step 3: Clamp result to [0.0, 1.0]
        # Due to floating point math, result could be slightly outside this range
        # max(0.0, ...) removes negatives, min(1.0, ...) caps at 1.0
        similarity = float(max(0.0, min(1.0, similarity)))
        
        return similarity
    
    except Exception as e:
        # Don't crash the app — return 0.0 as a safe fallback
        st.warning(f"Error calculating similarity for skill '{skill}': {e}")
        return 0.0


def exact_skill_match(skill: str, text: str) -> bool:
    """
    Check if a skill word literally appears anywhere in the text.
    
    📚 TEACHING NOTE — Why have both exact match AND semantic similarity?
        Semantic similarity (cosine) is powerful but computationally expensive.
        Exact match is simple but fast.
        
        We use a "fast path, slow path" strategy:
        1. First try exact match (fast, O(n) string search)
        2. Only if that fails, run semantic similarity (slow, neural network)
        
        This is an optimization technique — avoid heavy computation when
        a simple check is enough. Always prefer the cheaper option first.
        
        Example:
            skill = "Python"
            text = "Developed REST APIs using Python and Django"
            exact_match → True (found "Python" in text)
            → No need to run semantic similarity at all!
            
        Another example:
            skill = "Python"
            text = "Built backend services in the interpreted scripting language"
            exact_match → False ("Python" not literally there)
            → Now run semantic similarity → likely ~0.7 (semantically related)
    
    Returns:
        True if skill is found as a substring in text (case-insensitive)
    """
    # Guard clause — if either is empty, there's nothing to match
    if not skill or not text:
        return False
    
    # .lower() makes it case-insensitive: "Python" == "python" == "PYTHON"
    # 'in' operator checks if left string is a substring of right string
    return skill.lower() in text.lower()