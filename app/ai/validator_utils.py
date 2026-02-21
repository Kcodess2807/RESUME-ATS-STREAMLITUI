import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np


@st.cache_resource
def load_embedder(model_name: str = "all-MiniLM-L6-v2"):
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
    if not skill or not text:
        return 0.0
    
    try:
        skill_embedding = embedder.encode(skill, convert_to_tensor=False)
        text_embedding = embedder.encode(text, convert_to_tensor=False)
        
        similarity = np.dot(skill_embedding, text_embedding) / (
            np.linalg.norm(skill_embedding) * np.linalg.norm(text_embedding)
        )
        
        similarity = float(max(0.0, min(1.0, similarity)))
        
        return similarity
    except Exception as e:
        st.warning(f"Error calculating similarity for skill '{skill}': {e}")
        return 0.0


def exact_skill_match(skill: str, text: str) -> bool:
    if not skill or not text:
        return False
    
    return skill.lower() in text.lower()
