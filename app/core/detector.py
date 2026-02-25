"""
Location Detector Module
Detects privacy-sensitive location information in resume text.

📌 TEACHING NOTE — Why detect location in a resume?
    Modern resume best practices say candidates should NOT include:
    - Full street addresses  ("123 MG Road, Bengaluru 560001")
    - ZIP/PIN codes          ("560001")
    
    Reasons:
    1. Privacy risk — detailed address can identify where someone lives
    2. ATS irrelevance — ATS systems don't need a full address
    3. Bias risk — location details can introduce unconscious bias

    What IS acceptable:
    - City + State/Country in the contact header ("Bengaluru, India")

    This module:
    1. Detects all location mentions using NER + regex
    2. Classifies each as acceptable or problematic
    3. Assigns a privacy risk level (none/low/medium/high)
    4. Calculates a score penalty (up to -5 points on ATS compatibility)

📌 TEACHING NOTE — This file follows the same three-layer pattern as comparator.py:
    _perform_location_detection()  → pure logic
    _cached_location_detection()   → @st.cache_data wrapper
    detect_location_info()         → public entry point
"""

import streamlit as st
import spacy
import re
from typing import Dict, List, Tuple

# Import all helper functions from the companion file
# detector_helpers.py handles the low-level pattern matching and classification
from app.core.detector_helpers import (
    extract_contact_section,
    is_in_contact_header,
    is_acceptable_location,
    detect_zip_codes,
    detect_street_addresses,
    detect_locations_with_ner,
    determine_section,
    assess_privacy_risk,
    generate_privacy_recommendations,
    calculate_location_penalty
)


def _perform_location_detection(text: str, nlp: spacy.Language) -> Dict:
    """
    Core location detection pipeline — runs all three detection methods and assembles results.

    📌 TEACHING NOTE — Three Detection Methods (Defense in Depth):
        We use three different techniques because no single method catches everything:

        1. NER (Named Entity Recognition) via spaCy:
           Catches: "Bengaluru", "New York", "India"
           Misses: ZIP codes, street numbers

        2. Street Address Regex:
           Catches: "123 MG Road", "456 Oak Avenue"
           Misses: city names without street format

        3. ZIP Code Regex:
           Catches: "560001", "90210", "10001-2345"
           Misses: city names, country names

        Using all three = maximum coverage. This "defense in depth" approach
        is also used in cybersecurity — multiple layers catch what one layer misses.

    📌 TEACHING NOTE — all_locations list and then filtering:
        We first collect ALL detected locations (raw), then filter to
        only the "problematic" ones. This two-step approach is cleaner than
        trying to filter during detection — separation of concerns again.

        Also, adding a 'section' key to each location AFTER collection
        (not during) keeps the detection functions simple and focused.

    Args:
        text: Full resume text
        nlp: Loaded spaCy model

    Returns:
        Dict with location_found, detected_locations, privacy_risk,
        recommendations, and penalty_applied
    """
    all_locations = []

    # ── Method 1: AI-powered Named Entity Recognition ────────────────────
    # spaCy identifies GPE (Geopolitical Entity) and LOC (Location) entities
    ner_locations = detect_locations_with_ner(text, nlp)
    all_locations.extend(ner_locations)

    # ── Method 2: Regex pattern for street addresses ──────────────────────
    # Catches: "123 MG Road", "45 Park Avenue"
    addresses = detect_street_addresses(text)
    all_locations.extend(addresses)

    # ── Method 3: Regex pattern for ZIP/PIN codes ─────────────────────────
    # Catches: "560001", "10001", "90210-1234"
    zip_codes = detect_zip_codes(text)
    all_locations.extend(zip_codes)

    # ── Add section context to each location ─────────────────────────────
    # Knowing WHERE in the resume a location appears matters:
    # "Bengaluru" in contact header → acceptable
    # "Bengaluru" mid-resume → potentially unnecessary
    for location in all_locations:
        location['section'] = determine_section(text, location['start'])

    # ── Filter: keep only PROBLEMATIC locations ───────────────────────────
    # is_acceptable_location() decides if a location is OK based on:
    # type (city vs ZIP vs street) + section (contact header vs body)
    problematic_locations = []
    for location in all_locations:
        if not is_acceptable_location(
            location['text'],
            location['type'],
            location['section']
        ):
            problematic_locations.append(location)

    # ── Assess overall risk and generate output ───────────────────────────
    privacy_risk    = assess_privacy_risk(problematic_locations)
    recommendations = generate_privacy_recommendations(problematic_locations)
    penalty         = calculate_location_penalty(problematic_locations, privacy_risk)

    return {
        'location_found':      len(problematic_locations) > 0,
        'detected_locations':  problematic_locations,
        'privacy_risk':        privacy_risk,        # 'none' | 'low' | 'medium' | 'high'
        'recommendations':     recommendations,     # List of actionable strings
        'penalty_applied':     penalty              # Float: 0.0 to 5.0
    }


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_location_detection(text_hash: str, text: str, _nlp) -> Dict:
    """
    Cached wrapper — returns stored result if same text was analyzed before.

    📌 TEACHING NOTE — Caching NLP analysis:
        Running spaCy NER on a full resume takes ~0.5-1.5 seconds.
        If the user navigates to another page and comes back, we don't
        want to re-run the analysis. The cache key is text_hash —
        same resume text = same hash = instant cached result.

        The _nlp underscore prefix tells Streamlit: "don't try to hash
        this argument when building the cache key" (it's a complex object).

    Args:
        text_hash: SHA-256 hash of the resume text (cache key)
        text: Actual resume text (for computation)
        _nlp: spaCy model (excluded from cache key, prefix with _)
    """
    return _perform_location_detection(text, _nlp)


def detect_location_info(
    text: str,
    nlp: spacy.Language = None,
    use_cache: bool = True
) -> Dict:
    """
    Public entry point — detect location/privacy issues in resume text.

    📌 TEACHING NOTE — Auto-loading the model:
        If nlp is not provided, this function loads spaCy automatically.
        This is convenient for callers who don't manage models themselves.
        But note: loading spaCy takes time! If this function is called in
        a loop, the caller should load the model once and pass it in.

        Pattern: Optional parameter with lazy loading inside
            nlp = None → function loads it
            nlp = some_model → function uses what you gave it

    📌 TEACHING NOTE — use_cache=True default:
        In production, always cache. But for unit tests, set use_cache=False
        to always get a fresh result and avoid test interference.

    Args:
        text: Full resume text to analyze
        nlp: Optional pre-loaded spaCy model
        use_cache: Whether to use caching (default True)

    Returns:
        Dict with privacy risk assessment and recommendations
    """
    # Auto-load spaCy if not provided
    if nlp is None:
        from app.ai.ai_helper import load_spacy_model
        nlp = load_spacy_model()

    if use_cache:
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_location_detection(text_hash, text, nlp)
    else:
        return _perform_location_detection(text, nlp)


def generate_location_feedback(location_results: Dict) -> List[str]:
    """
    Convert raw location detection results into user-friendly feedback messages.

    📌 TEACHING NOTE — Separation of concerns (again):
        _perform_location_detection() collects data (WHAT was found).
        THIS function communicates the data to the user (WHAT TO DO).

        These are two different jobs — kept in separate functions.
        The UI layer calls generate_location_feedback() and displays the
        returned strings without needing to understand the detection logic.

    📌 TEACHING NOTE — Risk Level to Message Mapping:
        none   → all clear ✅
        low    → minor issue, acceptable in context 🟢
        medium → should simplify 🟡
        high   → immediate action required 🔴

        This is a "strategy" for translating internal codes to user messages.
        Adding a new risk level in the future only requires adding one elif here.

    📌 TEACHING NOTE — feedback.extend() vs append():
        .append(item)       → adds ONE item to the list
        .extend(other_list) → adds ALL items from another list to this list
        
        We use extend() to merge the recommendations list into feedback
        without creating a nested list.

    Args:
        location_results: Dict returned by detect_location_info()

    Returns:
        List of feedback strings ready to display in the UI
    """
    feedback = []
    privacy_risk   = location_results['privacy_risk']
    penalty        = location_results['penalty_applied']
    detected_count = len(location_results['detected_locations'])

    # ── Overall risk summary message ─────────────────────────────────────
    if privacy_risk == 'none':
        feedback.append('✅ Excellent! No privacy concerns detected in your resume.')
    elif privacy_risk == 'low':
        feedback.append(
            f'🟢 Low privacy risk detected. {detected_count} location mention(s) found, '
            f'but they appear acceptable.'
        )
    elif privacy_risk == 'medium':
        feedback.append(
            f'🟡 Medium privacy risk. {detected_count} location mention(s) found. '
            f'Consider simplifying location information.'
        )
    else:  # high
        feedback.append(
            f'🔴 High privacy risk! {detected_count} detailed location(s) found. '
            f'Remove sensitive location information immediately.'
        )

    # ── Penalty notification ──────────────────────────────────────────────
    if penalty > 0:
        feedback.append(
            f'⚠️ Location privacy issues resulted in a {penalty:.1f} point penalty '
            f'on your ATS compatibility score.'
        )

    # ── Specific recommendations from the detection step ─────────────────
    # extend() merges the recommendations list INTO the feedback list
    feedback.extend(location_results['recommendations'])

    return feedback