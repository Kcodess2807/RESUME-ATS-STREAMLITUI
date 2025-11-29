"""
Location Detector Module for ATS Resume Scorer

This module detects sensitive location information in resumes for privacy recommendations.
Identifies addresses, cities, states, and zip codes using spaCy NER and regex patterns.
"""

import streamlit as st
import spacy
import re
from typing import Dict, List, Tuple


# Common location patterns for regex matching
ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'  # 5-digit or 9-digit zip codes
STREET_ADDRESS_PATTERN = r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b'
STATE_ABBREV_PATTERN = r'\b(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'

# Contact section keywords to identify header
CONTACT_KEYWORDS = [
    'contact', 'contact information', 'personal information',
    'email', 'phone', 'address', 'linkedin', 'github'
]


def extract_contact_section(text: str, max_lines: int = 10) -> str:
    """
    Extract the contact section from resume text (typically at the top).
    
    Args:
        text: Full resume text
        max_lines: Maximum number of lines to consider as contact section
        
    Returns:
        Contact section text
    """
    lines = text.split('\n')
    contact_section = '\n'.join(lines[:max_lines])
    return contact_section


def is_in_contact_header(location_text: str, text: str, context_chars: int = 200) -> bool:
    """
    Determines if a location mention is in the contact header section.
    
    Args:
        location_text: The detected location text
        text: Full resume text
        context_chars: Number of characters to consider as contact header
        
    Returns:
        True if location is in contact header, False otherwise
        
    Validates:
        - Requirements 8.4: Contact header exemption logic
    """
    # Get the position of the location in the text
    location_pos = text.lower().find(location_text.lower())
    
    if location_pos == -1:
        return False
    
    # Check if it's in the first portion of the text (contact header)
    if location_pos > context_chars:
        return False
    
    # Get the context around the location
    context_start = max(0, location_pos - 100)
    context_end = min(len(text), location_pos + 100)
    context = text[context_start:context_end].lower()
    
    # Check if contact keywords are nearby
    for keyword in CONTACT_KEYWORDS:
        if keyword in context:
            return True
    
    return False


def is_acceptable_location(location_text: str, location_type: str, section: str) -> bool:
    """
    Determines if a location mention is acceptable (e.g., city/state in header).
    
    Args:
        location_text: The detected location text
        location_type: Type of location (address, city, state, zip)
        section: Section where location was found
        
    Returns:
        True if location is acceptable, False if it's a privacy concern
        
    Validates:
        - Requirements 8.4: Contact header exemption logic
    """
    # Full addresses are never acceptable
    if location_type == "address":
        return False
    
    # Zip codes are never acceptable (too specific)
    if location_type == "zip":
        return False
    
    # City/state in contact header is acceptable
    if section == "contact_header" and location_type in ["city", "state", "gpe"]:
        return True
    
    # Everything else is a privacy concern
    return False


def detect_zip_codes(text: str) -> List[Dict]:
    """
    Detect zip codes in text using regex.
    
    Args:
        text: Text to search
        
    Returns:
        List of detected zip code dictionaries
        
    Validates:
        - Requirements 8.3: Zip code detection
    """
    zip_codes = []
    
    for match in re.finditer(ZIP_CODE_PATTERN, text):
        zip_codes.append({
            'text': match.group(),
            'type': 'zip',
            'start': match.start(),
            'end': match.end()
        })
    
    return zip_codes


def detect_street_addresses(text: str) -> List[Dict]:
    """
    Detect street addresses in text using regex.
    
    Args:
        text: Text to search
        
    Returns:
        List of detected address dictionaries
        
    Validates:
        - Requirements 8.1: Address detection using regex patterns
    """
    addresses = []
    
    for match in re.finditer(STREET_ADDRESS_PATTERN, text, re.IGNORECASE):
        addresses.append({
            'text': match.group(),
            'type': 'address',
            'start': match.start(),
            'end': match.end()
        })
    
    return addresses


def detect_locations_with_ner(text: str, nlp: spacy.Language) -> List[Dict]:
    """
    Detect locations using spaCy Named Entity Recognition.
    
    Args:
        text: Text to analyze
        nlp: Loaded spaCy model
        
    Returns:
        List of detected location dictionaries
        
    Validates:
        - Requirements 8.1: Address detection using spaCy NER (GPE, LOC tags)
        - Requirements 8.2: City and state detection
    """
    locations = []
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Extract GPE (Geopolitical Entity) and LOC (Location) entities
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            locations.append({
                'text': ent.text,
                'type': ent.label_.lower(),
                'start': ent.start_char,
                'end': ent.end_char
            })
    
    return locations


def determine_section(text: str, location_start: int) -> str:
    """
    Determine which section of the resume a location appears in.
    
    Args:
        text: Full resume text
        location_start: Character position where location starts
        
    Returns:
        Section name (contact_header, experience, education, other)
    """
    # Check if in contact header (first 200 characters)
    if location_start < 200:
        return "contact_header"
    
    # Get context around location
    context_start = max(0, location_start - 200)
    context_end = min(len(text), location_start + 200)
    context = text[context_start:context_end].lower()
    
    # Check for section keywords
    if any(keyword in context for keyword in ['experience', 'work history', 'employment']):
        return "experience"
    elif any(keyword in context for keyword in ['education', 'academic', 'university', 'college']):
        return "education"
    else:
        return "other"


def assess_privacy_risk(detected_locations: List[Dict]) -> str:
    """
    Assess the overall privacy risk level based on detected locations.
    
    Args:
        detected_locations: List of detected location dictionaries
        
    Returns:
        Risk level: "high", "medium", "low", or "none"
        
    Validates:
        - Requirements 8.5: Privacy risk assessment
    """
    if not detected_locations:
        return "none"
    
    has_address = any(loc['type'] == 'address' for loc in detected_locations)
    has_zip = any(loc['type'] == 'zip' for loc in detected_locations)
    has_multiple_locations = len(detected_locations) > 3
    
    # High risk: Full address or zip code
    if has_address or has_zip:
        return "high"
    
    # Medium risk: Multiple location mentions
    if has_multiple_locations:
        return "medium"
    
    # Low risk: Few location mentions
    return "low"


def generate_privacy_recommendations(detected_locations: List[Dict]) -> List[str]:
    """
    Generate specific recommendations for location privacy.
    
    Args:
        detected_locations: List of detected location dictionaries
        
    Returns:
        List of recommendation strings
        
    Validates:
        - Requirements 8.5: Location removal recommendations
    """
    recommendations = []
    
    if not detected_locations:
        recommendations.append("✅ No privacy concerns detected. Your resume doesn't contain detailed location information.")
        return recommendations
    
    # Check for addresses
    addresses = [loc for loc in detected_locations if loc['type'] == 'address']
    if addresses:
        recommendations.append(
            "🔴 Remove full street addresses from your resume. "
            "ATS systems don't need this information, and it poses a privacy risk."
        )
        for addr in addresses[:3]:  # Show up to 3 examples
            recommendations.append(f"  • Found: '{addr['text']}' in {addr['section']}")
    
    # Check for zip codes
    zip_codes = [loc for loc in detected_locations if loc['type'] == 'zip']
    if zip_codes:
        recommendations.append(
            "🔴 Remove zip codes from your resume. "
            "This level of detail is unnecessary and can be used to identify your location."
        )
        for zip_code in zip_codes[:3]:
            recommendations.append(f"  • Found: '{zip_code['text']}' in {zip_code['section']}")
    
    # Check for excessive location mentions
    non_header_locations = [
        loc for loc in detected_locations 
        if loc['section'] != 'contact_header' and loc['type'] in ['gpe', 'loc']
    ]
    
    if len(non_header_locations) > 3:
        recommendations.append(
            "🟡 Consider reducing location mentions throughout your resume. "
            "City/state in the contact header is sufficient."
        )
    
    # General recommendation
    if addresses or zip_codes:
        recommendations.append(
            "\n💡 Best Practice: Include only 'City, State' in your contact header. "
            "Remove all other location details."
        )
    
    return recommendations


def calculate_location_penalty(detected_locations: List[Dict], privacy_risk: str) -> float:
    """
    Calculate privacy penalty for ATS compatibility score.
    
    Args:
        detected_locations: List of detected location dictionaries
        privacy_risk: Risk level from assess_privacy_risk
        
    Returns:
        Penalty value (0-5 points)
        
    Validates:
        - Requirements 8.6: Privacy penalty calculation (3-5 points)
    """
    if privacy_risk == "none":
        return 0.0
    
    # Count problematic locations
    has_address = any(loc['type'] == 'address' for loc in detected_locations)
    has_zip = any(loc['type'] == 'zip' for loc in detected_locations)
    
    # High penalty for addresses or zip codes
    if has_address and has_zip:
        return 5.0
    elif has_address or has_zip:
        return 4.0
    
    # Medium penalty for multiple locations
    if privacy_risk == "medium":
        return 3.0
    
    # Low penalty for few locations
    if privacy_risk == "low":
        return 2.0
    
    return 0.0


def _perform_location_detection(text: str, nlp: spacy.Language) -> Dict:
    """
    Internal function to perform location detection.
    
    Args:
        text: Resume text to analyze
        nlp: spaCy model
        
    Returns:
        Dictionary containing location detection results
    """
    all_locations = []
    
    # Detect using NER (GPE and LOC entities)
    ner_locations = detect_locations_with_ner(text, nlp)
    all_locations.extend(ner_locations)
    
    # Detect street addresses using regex
    addresses = detect_street_addresses(text)
    all_locations.extend(addresses)
    
    # Detect zip codes using regex
    zip_codes = detect_zip_codes(text)
    all_locations.extend(zip_codes)
    
    # Determine section for each location
    for location in all_locations:
        location['section'] = determine_section(text, location['start'])
    
    # Filter out acceptable locations (city/state in contact header)
    problematic_locations = []
    for location in all_locations:
        if not is_acceptable_location(location['text'], location['type'], location['section']):
            problematic_locations.append(location)
    
    # Assess privacy risk
    privacy_risk = assess_privacy_risk(problematic_locations)
    
    # Generate recommendations
    recommendations = generate_privacy_recommendations(problematic_locations)
    
    # Calculate penalty
    penalty = calculate_location_penalty(problematic_locations, privacy_risk)
    
    return {
        "location_found": len(problematic_locations) > 0,
        "detected_locations": problematic_locations,
        "privacy_risk": privacy_risk,
        "recommendations": recommendations,
        "penalty_applied": penalty
    }


# Import streamlit for caching decorator
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_location_detection(text_hash: str, text: str, _nlp) -> Dict:
    """
    Cached version of location detection.
    
    Args:
        text_hash: Hash of text content for cache key
        text: Resume text to analyze
        _nlp: spaCy model (excluded from hash)
        
    Returns:
        Dictionary containing location detection results
        
    Validates:
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    return _perform_location_detection(text, _nlp)


def detect_location_info(text: str, nlp: spacy.Language = None, use_cache: bool = True) -> Dict:
    """
    Detects addresses, cities, states, zip codes in resume text.
    
    Args:
        text: Resume text to analyze
        nlp: Optional pre-loaded spaCy model
        use_cache: Whether to use caching for results (default: True)
        
    Returns:
        Dictionary containing:
        {
            "location_found": bool,
            "detected_locations": [{"text": "...", "type": "...", "section": "..."}],
            "privacy_risk": "high" | "medium" | "low" | "none",
            "recommendations": ["..."],
            "penalty_applied": float (0-5)
        }
        
    Validates:
        - Requirements 8.1: Address detection using spaCy NER and regex
        - Requirements 8.2: City and state detection
        - Requirements 8.3: Zip code detection
        - Requirements 8.4: Contact header exemption logic
        - Requirements 8.5: Privacy risk assessment and recommendations
        - Requirements 8.6: Privacy penalty calculation
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    # Load spaCy model if not provided
    if nlp is None:
        from utils.model_loader import load_spacy_model
        nlp = load_spacy_model()
    
    if use_cache:
        # Generate hash for caching
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_location_detection(text_hash, text, nlp)
    else:
        return _perform_location_detection(text, nlp)


def generate_location_feedback(location_results: Dict) -> List[str]:
    """
    Generate user-friendly feedback messages based on location detection results.
    
    Args:
        location_results: Results from detect_location_info()
        
    Returns:
        List of feedback messages
    """
    feedback = []
    
    privacy_risk = location_results['privacy_risk']
    penalty = location_results['penalty_applied']
    detected_count = len(location_results['detected_locations'])
    
    # Overall summary
    if privacy_risk == "none":
        feedback.append("✅ Excellent! No privacy concerns detected in your resume.")
    elif privacy_risk == "low":
        feedback.append(
            f"🟢 Low privacy risk detected. {detected_count} location mention(s) found, "
            "but they appear acceptable."
        )
    elif privacy_risk == "medium":
        feedback.append(
            f"🟡 Medium privacy risk. {detected_count} location mention(s) found. "
            "Consider simplifying location information."
        )
    else:  # high
        feedback.append(
            f"🔴 High privacy risk! {detected_count} detailed location(s) found. "
            "Remove sensitive location information immediately."
        )
    
    # Penalty information
    if penalty > 0:
        feedback.append(
            f"⚠️ Location privacy issues resulted in a {penalty:.1f} point penalty "
            f"on your ATS compatibility score."
        )
    
    # Add recommendations
    feedback.extend(location_results['recommendations'])
    
    return feedback
