import streamlit as st
import spacy
import re
from typing import Dict, List, Tuple

ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'
STREET_ADDRESS_PATTERN = r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b'
STATE_ABBREV_PATTERN = r'\b(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'

CONTACT_KEYWORDS = [
    'contact', 'contact information', 'personal information',
    'phone', 'email', 'address', 'location'
]


def extract_contact_section(text: str, max_lines: int=10) ->str:
    lines = text.split('\n')
    contact_section = '\n'.join(lines[:max_lines])
    return contact_section


def is_in_contact_header(location_text: str, text: str, context_chars: int=200
    ) ->bool:
    location_pos = text.lower().find(location_text.lower())
    if location_pos == -1:
        return False
    if location_pos > context_chars:
        return False
    context_start = max(0, location_pos - 100)
    context_end = min(len(text), location_pos + 100)
    context = text[context_start:context_end].lower()
    for keyword in CONTACT_KEYWORDS:
        if keyword in context:
            return True
    return False


def is_acceptable_location(location_text: str, location_type: str, section: str
    ) ->bool:
    if location_type == 'address':
        return False
    if location_type == 'zip':
        return False
    if section == 'contact_header' and location_type in ['city', 'state', 'gpe'
        ]:
        return True
    return False


def detect_zip_codes(text: str) ->List[Dict]:
    zip_codes = []
    for match in re.finditer(ZIP_CODE_PATTERN, text):
        zip_codes.append({'text': match.group(), 'type': 'zip', 'start':
            match.start(), 'end': match.end()})
    return zip_codes


def detect_street_addresses(text: str) ->List[Dict]:
    addresses = []
    for match in re.finditer(STREET_ADDRESS_PATTERN, text, re.IGNORECASE):
        addresses.append({'text': match.group(), 'type': 'address', 'start':
            match.start(), 'end': match.end()})
    return addresses


def detect_locations_with_ner(text: str, nlp: spacy.Language) ->List[Dict]:
    locations = []
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            locations.append({'text': ent.text, 'type': ent.label_.lower(),
                'start': ent.start_char, 'end': ent.end_char})
    return locations


def determine_section(text: str, location_start: int) ->str:
    if location_start < 200:
        return 'contact_header'
    context_start = max(0, location_start - 200)
    context_end = min(len(text), location_start + 200)
    context = text[context_start:context_end].lower()
    if any(keyword in context for keyword in ['experience', 'work history',
        'employment']):
        return 'experience'
    elif any(keyword in context for keyword in ['education', 'academic',
        'university', 'college']):
        return 'education'
    else:
        return 'other'


def assess_privacy_risk(detected_locations: List[Dict]) ->str:
    if not detected_locations:
        return 'none'
    has_address = any(loc['type'] == 'address' for loc in detected_locations)
    has_zip = any(loc['type'] == 'zip' for loc in detected_locations)
    has_multiple_locations = len(detected_locations) > 3
    if has_address or has_zip:
        return 'high'
    if has_multiple_locations:
        return 'medium'
    return 'low'


def generate_privacy_recommendations(detected_locations: List[Dict]) ->List[str
    ]:
    recommendations = []
    if not detected_locations:
        recommendations.append(
            "✅ No privacy concerns detected. Your resume doesn't contain detailed location information."
            )
        return recommendations
    addresses = [loc for loc in detected_locations if loc['type'] == 'address']
    if addresses:
        recommendations.append(
            "🔴 Remove full street addresses from your resume. ATS systems don't need this information, and it poses a privacy risk."
            )
        for addr in addresses[:3]:
            recommendations.append(
                f"  • Found: '{addr['text']}' in {addr['section']}")
    zip_codes = [loc for loc in detected_locations if loc['type'] == 'zip']
    if zip_codes:
        recommendations.append(
            '🔴 Remove zip codes from your resume. This level of detail is unnecessary and can be used to identify your location.'
            )
        for zip_code in zip_codes[:3]:
            recommendations.append(
                f"  • Found: '{zip_code['text']}' in {zip_code['section']}")
    non_header_locations = [loc for loc in detected_locations if loc[
        'section'] != 'contact_header' and loc['type'] in ['gpe', 'loc']]
    if len(non_header_locations) > 3:
        recommendations.append(
            '🟡 Consider reducing location mentions throughout your resume. City/state in the contact header is sufficient.'
            )
    if addresses or zip_codes:
        recommendations.append(
            """
💡 Best Practice: Include only 'City, State' in your contact header. Remove all other location details."""
            )
    return recommendations


def calculate_location_penalty(detected_locations: List[Dict], privacy_risk:
    str) ->float:
    if privacy_risk == 'none':
        return 0.0
    has_address = any(loc['type'] == 'address' for loc in detected_locations)
    has_zip = any(loc['type'] == 'zip' for loc in detected_locations)
    if has_address and has_zip:
        return 5.0
    elif has_address or has_zip:
        return 4.0
    if privacy_risk == 'medium':
        return 3.0
    if privacy_risk == 'low':
        return 2.0
    return 0.0
