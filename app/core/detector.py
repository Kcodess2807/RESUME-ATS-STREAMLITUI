import streamlit as st
import spacy
import re
from typing import Dict, List, Tuple
import streamlit as st
from app.core.detector_helpers import extract_contact_section, is_in_contact_header, is_acceptable_location, detect_zip_codes, detect_street_addresses, detect_locations_with_ner, determine_section, assess_privacy_risk, generate_privacy_recommendations, calculate_location_penalty


def _perform_location_detection(text: str, nlp: spacy.Language) ->Dict:
    all_locations = []
    ner_locations = detect_locations_with_ner(text, nlp)
    all_locations.extend(ner_locations)
    addresses = detect_street_addresses(text)
    all_locations.extend(addresses)
    zip_codes = detect_zip_codes(text)
    all_locations.extend(zip_codes)
    for location in all_locations:
        location['section'] = determine_section(text, location['start'])
    problematic_locations = []
    for location in all_locations:
        if not is_acceptable_location(location['text'], location['type'],
            location['section']):
            problematic_locations.append(location)
    privacy_risk = assess_privacy_risk(problematic_locations)
    recommendations = generate_privacy_recommendations(problematic_locations)
    penalty = calculate_location_penalty(problematic_locations, privacy_risk)
    return {'location_found': len(problematic_locations) > 0,
        'detected_locations': problematic_locations, 'privacy_risk':
        privacy_risk, 'recommendations': recommendations, 'penalty_applied':
        penalty}


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_location_detection(text_hash: str, text: str, _nlp) ->Dict:
    return _perform_location_detection(text, _nlp)


def detect_location_info(text: str, nlp: spacy.Language=None, use_cache:
    bool=True) ->Dict:
    if nlp is None:
        from app.ai.ai_helper import load_spacy_model
        nlp = load_spacy_model()
    if use_cache:
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_location_detection(text_hash, text, nlp)
    else:
        return _perform_location_detection(text, nlp)


def generate_location_feedback(location_results: Dict) ->List[str]:
    feedback = []
    privacy_risk = location_results['privacy_risk']
    penalty = location_results['penalty_applied']
    detected_count = len(location_results['detected_locations'])
    if privacy_risk == 'none':
        feedback.append(
            '✅ Excellent! No privacy concerns detected in your resume.')
    elif privacy_risk == 'low':
        feedback.append(
            f'🟢 Low privacy risk detected. {detected_count} location mention(s) found, but they appear acceptable.'
            )
    elif privacy_risk == 'medium':
        feedback.append(
            f'🟡 Medium privacy risk. {detected_count} location mention(s) found. Consider simplifying location information.'
            )
    else:
        feedback.append(
            f'🔴 High privacy risk! {detected_count} detailed location(s) found. Remove sensitive location information immediately.'
            )
    if penalty > 0:
        feedback.append(
            f'⚠️ Location privacy issues resulted in a {penalty:.1f} point penalty on your ATS compatibility score.'
            )
    feedback.extend(location_results['recommendations'])
    return feedback
