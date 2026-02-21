from typing import Dict, List, Optional, Tuple
import re
import streamlit as st
import hashlib
from app.core.scorer_calc import calculate_formatting_score, calculate_keywords_score, calculate_content_score, calculate_skill_validation_score, calculate_ats_compatibility_score, apply_penalties_and_bonuses
from app.core.scorer_feedback import generate_score_interpretation, generate_score_breakdown_messages, generate_strengths, generate_critical_issues, generate_improvements


def _compute_overall_score(text: str, sections: Dict[str, str], skills:
    List[str], keywords: List[str], action_verbs: List[str],
    skill_validation_results: Dict, grammar_results: Dict, location_results:
    Dict, jd_keywords: Optional[List[str]]=None) ->Dict:
    formatting_score = calculate_formatting_score(sections, text)
    keywords_score = calculate_keywords_score(keywords, skills, jd_keywords)
    content_score = calculate_content_score(text, action_verbs, grammar_results
        )
    skill_validation_score = calculate_skill_validation_score(
        skill_validation_results)
    ats_compatibility_score = calculate_ats_compatibility_score(text,
        location_results, sections)
    base_score = (formatting_score + keywords_score + content_score +
        skill_validation_score + ats_compatibility_score)
    overall_score, penalties, bonuses = apply_penalties_and_bonuses(base_score,
        grammar_results, location_results, skill_validation_results)
    overall_interpretation = generate_score_interpretation(overall_score)
    component_messages = generate_score_breakdown_messages(formatting_score,
        keywords_score, content_score, skill_validation_score,
        ats_compatibility_score)
    return {'overall_score': round(overall_score, 1),
        'overall_interpretation': overall_interpretation,
        'formatting_score': round(formatting_score, 1), 'keywords_score':
        round(keywords_score, 1), 'content_score': round(content_score, 1),
        'skill_validation_score': round(skill_validation_score, 1),
        'ats_compatibility_score': round(ats_compatibility_score, 1),
        'component_messages': component_messages, 'penalties': penalties,
        'bonuses': bonuses}


def calculate_overall_score(text: str, sections: Dict[str, str], skills:
    List[str], keywords: List[str], action_verbs: List[str],
    skill_validation_results: Dict, grammar_results: Dict, location_results:
    Dict, jd_keywords: Optional[List[str]]=None, use_cache: bool=True) ->Dict:
    try:
        from streamlit.runtime.state import SessionState
        in_streamlit = isinstance(st.session_state, SessionState)
    except Exception:
        in_streamlit = False
    if use_cache and in_streamlit:
        import json
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        skills_key = tuple(sorted(skills)) if skills else ()
        keywords_key = tuple(sorted(keywords)) if keywords else ()
        jd_key = tuple(sorted(jd_keywords)) if jd_keywords else ()
        cache_key = (
            f'score_{text_hash}_{hash((skills_key, keywords_key, jd_key))}')
        if 'score_cache' not in st.session_state:
            st.session_state.score_cache = {}
        if cache_key in st.session_state.score_cache:
            return st.session_state.score_cache[cache_key]
        result = _compute_overall_score(text, sections, skills, keywords,
            action_verbs, skill_validation_results, grammar_results,
            location_results, jd_keywords)
        st.session_state.score_cache[cache_key] = result
        if len(st.session_state.score_cache) > 20:
            oldest_key = next(iter(st.session_state.score_cache))
            del st.session_state.score_cache[oldest_key]
        return result
    else:
        return _compute_overall_score(text, sections, skills, keywords,
            action_verbs, skill_validation_results, grammar_results,
            location_results, jd_keywords)
