"""
Detector Helpers Module
Low-level helper functions for location detection — used by detector.py.

📌 TEACHING NOTE — Why split detector.py into two files?
    detector.py handles the HIGH-LEVEL flow:
        - Which detection methods to call?
        - How to combine results?
        - How to cache?
        - What to return to the UI?

    THIS file handles the LOW-LEVEL details:
        - What does the regex pattern for a ZIP code look like?
        - How do we decide if a location is "acceptable"?
        - How do we calculate the privacy penalty number?

    This split keeps each file focused and manageable.
    A developer fixing a regex bug only needs to look here.
    A developer changing the scoring logic only needs to look here.
    detector.py stays clean and readable.

    This is the same philosophy as utils files — helper functions
    that do one specific thing, kept separate from orchestration logic.
"""

import streamlit as st
import spacy
import re
from typing import Dict, List, Tuple


# ============================================================
# 📌 TEACHING NOTE — Module-Level Constants (Compiled Regex Patterns)
#
#   We define regex patterns as constants at the TOP of the file.
#   Benefits:
#   1. They're compiled ONCE when the module loads (faster than
#      compiling inside a loop on every call)
#   2. They're easy to find, read, and modify in one place
#   3. Named constants are self-documenting (ZIP_CODE_PATTERN vs the raw string)
#
#   Raw string notation r'...' is used so backslashes don't need escaping.
#   Without r: '\\b\\d{5}' (ugly)
#   With r:    r'\b\d{5}'  (clean)
#
#   Regex components explained for students:
#   \b       → word boundary (ensures "12345" doesn't match inside "123456789")
#   \d{5}    → exactly 5 digits
#   (?:-\d{4})? → optionally followed by a hyphen and 4 more digits (ZIP+4 format)
# ============================================================

# Matches US ZIP codes: "90210" or "10001-2345"
ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'

# Matches street addresses: "123 MG Road", "456 Park Avenue"
# \d+           → house number
# [A-Z][a-z]+   → capitalized word (street name)
# (?:Street|St|...) → common street type suffixes
STREET_ADDRESS_PATTERN = (
    r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+'
    r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b'
)

# Matches US state abbreviations: CA, NY, TX, etc.
# (?:...) → non-capturing group (groups without creating a backreference)
# \b       → word boundary on both sides so "CA" doesn't match inside "CANADA"
STATE_ABBREV_PATTERN = (
    r'\b(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|'
    r'MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|'
    r'TX|UT|VT|VA|WA|WV|WI|WY)\b'
)

# Keywords that indicate we're in the contact/header section of the resume
CONTACT_KEYWORDS = [
    'contact', 'contact information', 'personal information',
    'phone', 'email', 'address', 'location'
]


def extract_contact_section(text: str, max_lines: int = 10) -> str:
    """
    Extract the first few lines of the resume (likely the contact section).

    📌 TEACHING NOTE — Why look at first N lines?
        Contact information is almost always at the TOP of a resume.
        By extracting just the first 10 lines, we can quickly check
        if a location appears in the contact header specifically.

        max_lines=10 is a reasonable default — most contact sections
        fit within 5-7 lines (name, title, email, phone, location, LinkedIn).
        We use 10 to be safe.

    Args:
        text: Full resume text
        max_lines: Number of lines to extract from the top

    Returns:
        String containing only the first max_lines lines
    """
    lines = text.split('\n')
    contact_section = '\n'.join(lines[:max_lines])
    return contact_section


def is_in_contact_header(
    location_text: str,
    text: str,
    context_chars: int = 200
) -> bool:
    """
    Check whether a detected location appears in the contact/header area.

    📌 TEACHING NOTE — Position-based heuristics:
        We use TWO signals to determine if a location is in the contact header:

        1. Position check: Is the location within the first 200 characters?
           Most resumes have contact info in the first 150-200 characters.
           If a location appears after character 200, it's probably NOT in the header.

        2. Context check: Do contact keywords appear nearby?
           We look at 100 chars before and after the location.
           If "email", "phone", or "address" appears nearby, it's contact section.

        Using TWO signals reduces false positives. This is a common pattern
        in heuristic-based systems — one signal might be wrong, two are better.

    Args:
        location_text: The location string to look for (e.g., "Bengaluru")
        text: Full resume text to search in
        context_chars: Max character position to be considered "in header"

    Returns:
        True if the location appears to be in the contact header
    """
    # Find where this location text appears in the full document
    location_pos = text.lower().find(location_text.lower())

    if location_pos == -1:
        return False  # Location text not found at all

    # Signal 1: Position check — is it near the start?
    if location_pos > context_chars:
        return False  # Too far into the document to be in the header

    # Signal 2: Context check — are contact keywords nearby?
    context_start = max(0, location_pos - 100)
    context_end   = min(len(text), location_pos + 100)
    context       = text[context_start:context_end].lower()

    for keyword in CONTACT_KEYWORDS:
        if keyword in context:
            return True  # Contact keyword found nearby → it's in the header

    return False


def is_acceptable_location(
    location_text: str,
    location_type: str,
    section: str
) -> bool:
    """
    Decide whether a detected location is acceptable (OK to have in resume).

    📌 TEACHING NOTE — Decision Table:
        This function implements a simple decision table:

        Location Type | Section        | Acceptable?
        ─────────────────────────────────────────────
        'address'     | anywhere       | ❌ NEVER (full addresses are always bad)
        'zip'         | anywhere       | ❌ NEVER (ZIP codes reveal precise location)
        'city'/'state'| contact_header | ✅ OK (City, State is standard)
        'city'/'state'| elsewhere      | ❌ NOT OK (unnecessary detail in body)

        Decision tables are great for teaching because they make business
        rules explicit and easy to verify/modify.

    Args:
        location_text: The detected location string (used for future enhancements)
        location_type: 'address', 'zip', 'city', 'state', 'gpe', 'loc'
        section: 'contact_header', 'experience', 'education', 'other'

    Returns:
        True if the location is acceptable in this context, False otherwise
    """
    # Street addresses are NEVER acceptable — full address = privacy risk
    if location_type == 'address':
        return False

    # ZIP codes are NEVER acceptable — too precise, not needed by ATS
    if location_type == 'zip':
        return False

    # City or state in the contact header → this is the EXPECTED place for it
    if section == 'contact_header' and location_type in ['city', 'state', 'gpe']:
        return True

    # Everything else is not acceptable
    return False


def detect_zip_codes(text: str) -> List[Dict]:
    """
    Find all ZIP code patterns in the resume text using regex.

    📌 TEACHING NOTE — re.finditer() vs re.findall():
        re.findall(pattern, text) → returns list of matching strings
        re.finditer(pattern, text) → returns iterator of Match objects

        Match objects are richer — they have .start(), .end(), .group().
        We need the position (start, end) to know WHERE in the document
        the ZIP code was found, so re.finditer() is the right choice here.

    📌 TEACHING NOTE — Return format consistency:
        All three detect_*() functions return the same dict structure:
        {'text': ..., 'type': ..., 'start': ..., 'end': ...}

        This consistency means the caller (detector.py) can process all
        three types of locations with the same code. Consistent data
        structures are a hallmark of well-designed APIs.

    Args:
        text: Full resume text

    Returns:
        List of dicts, each with text, type='zip', start, end
    """
    zip_codes = []
    for match in re.finditer(ZIP_CODE_PATTERN, text):
        zip_codes.append({
            'text':  match.group(),   # The actual matched text ("90210")
            'type':  'zip',
            'start': match.start(),   # Character position where match begins
            'end':   match.end()      # Character position where match ends
        })
    return zip_codes


def detect_street_addresses(text: str) -> List[Dict]:
    """
    Find street address patterns in the resume text using regex.

    📌 TEACHING NOTE — Regex Limitations (good discussion point):
        The STREET_ADDRESS_PATTERN works for standard Western address formats.
        It WON'T catch:
        - Indian addresses: "Flat 4B, Sector 15, Noida 201301"
        - Informal formats: "near MG Metro Station, Bengaluru"
        - Addresses in non-English scripts

        This is a real limitation of regex-based detection. A more robust
        solution would use a trained NER model for addresses specifically,
        or a geocoding API to verify if text is a real address.

        Teaching point: Know your tool's limits. Regex is fast and simple
        but not universal. NER (spaCy) catches what regex misses and vice versa.

    Args:
        text: Full resume text

    Returns:
        List of dicts with text, type='address', start, end
    """
    addresses = []
    for match in re.finditer(STREET_ADDRESS_PATTERN, text, re.IGNORECASE):
        addresses.append({
            'text':  match.group(),
            'type':  'address',
            'start': match.start(),
            'end':   match.end()
        })
    return addresses


def detect_locations_with_ner(text: str, nlp: spacy.Language) -> List[Dict]:
    """
    Use spaCy Named Entity Recognition to find location mentions.

    📌 TEACHING NOTE — What is NER?
        Named Entity Recognition (NER) is a subtask of NLP that identifies
        and classifies named entities in text into predefined categories.

        spaCy's entity types we use:
        - GPE (Geopolitical Entity): countries, cities, states
          Examples: "India", "Bengaluru", "Karnataka"
        - LOC (Location): non-GPE locations, geographic features
          Examples: "Silicon Valley", "the Bay Area"

        doc.ents → list of all identified entities in the processed text
        ent.label_ → the entity type ("GPE", "LOC", "PERSON", etc.)
        ent.start_char / ent.end_char → character positions in original text

    📌 TEACHING NOTE — nlp(text) creates a "Doc" object:
        When you call nlp(text), spaCy runs its full pipeline:
        tokenizer → tagger → parser → NER → ...
        The result is a Doc object with all annotations.
        This is the expensive step that we cache at a higher level.

    Args:
        text: Full resume text
        nlp: Loaded spaCy language model

    Returns:
        List of dicts with text, type (lowercased label), start_char, end_char
    """
    locations = []
    doc = nlp(text)  # Run full spaCy NLP pipeline

    for ent in doc.ents:
        # Filter to only location-type entities
        if ent.label_ in ['GPE', 'LOC']:
            locations.append({
                'text':  ent.text,
                'type':  ent.label_.lower(),   # 'gpe' or 'loc'
                'start': ent.start_char,        # Character position of start
                'end':   ent.end_char           # Character position of end
            })
    return locations


def determine_section(text: str, location_start: int) -> str:
    """
    Determine which section of the resume a location appears in.

    📌 TEACHING NOTE — Heuristic section detection:
        We don't have a perfect parser that knows the resume's structure.
        Instead we use HEURISTICS — educated guesses based on:
        1. Character position (first 200 chars = likely contact header)
        2. Keywords near the location (experience/education/etc.)

        Heuristics are imperfect by nature — they work "most of the time"
        but can be wrong. This is a deliberate trade-off between accuracy
        and implementation complexity.

    📌 TEACHING NOTE — Context window:
        We look at 200 characters BEFORE and AFTER the location.
        context_start = max(0, location_start - 200)
        The max(0, ...) prevents negative index if location is near the start.
        The min(len(text), ...) prevents going past the end.

        This 200-char window is called a "context window" — a common concept
        in NLP to look at surrounding text for disambiguation.

    Args:
        text: Full resume text
        location_start: Character position of the location in the text

    Returns:
        Section name: 'contact_header', 'experience', 'education', or 'other'
    """
    # Position-based check: first 200 chars = almost certainly contact header
    if location_start < 200:
        return 'contact_header'

    # Keyword-based check in surrounding text
    context_start = max(0, location_start - 200)
    context_end   = min(len(text), location_start + 200)
    context       = text[context_start:context_end].lower()

    if any(keyword in context for keyword in ['experience', 'work history', 'employment']):
        return 'experience'
    elif any(keyword in context for keyword in ['education', 'academic', 'university', 'college']):
        return 'education'
    else:
        return 'other'


def assess_privacy_risk(detected_locations: List[Dict]) -> str:
    """
    Classify the overall privacy risk level based on what was detected.

    📌 TEACHING NOTE — Risk Scoring Logic:
        Risk levels are determined by presence of specific location types:

        any address OR zip code  → 'high'   (precise, personally identifying info)
        more than 3 locations    → 'medium' (too much location detail throughout)
        any other locations      → 'low'    (location mentions but not dangerous)
        nothing found            → 'none'   (clean resume)

        Notice: HIGH overrides MEDIUM overrides LOW.
        The worst type of finding determines the overall risk level.
        This is like a "watermark" system — the worst condition dominates.

    Args:
        detected_locations: List of problematic location dicts

    Returns:
        Risk string: 'none', 'low', 'medium', or 'high'
    """
    if not detected_locations:
        return 'none'

    # Check for the most dangerous types first
    has_address  = any(loc['type'] == 'address' for loc in detected_locations)
    has_zip      = any(loc['type'] == 'zip'     for loc in detected_locations)
    has_multiple = len(detected_locations) > 3

    # Addresses and ZIP codes = HIGH risk (precise personally-identifying info)
    if has_address or has_zip:
        return 'high'

    # Many location mentions throughout the resume = MEDIUM risk
    if has_multiple:
        return 'medium'

    # Some locations found but not dangerous = LOW risk
    return 'low'


def generate_privacy_recommendations(detected_locations: List[Dict]) -> List[str]:
    """
    Generate specific, actionable recommendations for each type of privacy issue.

    📌 TEACHING NOTE — Actionable vs vague feedback:
        Vague:     "You have location issues."
        Actionable: "Remove '123 MG Road' found in your experience section."

        We show the specific text that was found (up to 3 examples per type)
        so the user knows exactly what to look for and remove.
        Showing more than 3 would be overwhelming — [:3] caps it.

    📌 TEACHING NOTE — Conditional recommendation building:
        Each section (addresses, zip codes, non-header locations) is
        processed independently. Only relevant recommendations are added.
        An empty detected_locations list → only the "all clear" message is added.

    Args:
        detected_locations: List of problematic location dicts

    Returns:
        List of recommendation strings ordered by severity (worst first)
    """
    recommendations = []

    if not detected_locations:
        recommendations.append(
            "✅ No privacy concerns detected. Your resume doesn't contain detailed location information."
        )
        return recommendations

    # ── Street address recommendations ───────────────────────────────────
    addresses = [loc for loc in detected_locations if loc['type'] == 'address']
    if addresses:
        recommendations.append(
            "🔴 Remove full street addresses from your resume. ATS systems don't need "
            "this information, and it poses a privacy risk."
        )
        # Show up to 3 specific examples (avoid overwhelming the user)
        for addr in addresses[:3]:
            recommendations.append(
                f"  • Found: '{addr['text']}' in {addr['section']}"
            )

    # ── ZIP code recommendations ──────────────────────────────────────────
    zip_codes = [loc for loc in detected_locations if loc['type'] == 'zip']
    if zip_codes:
        recommendations.append(
            '🔴 Remove zip codes from your resume. This level of detail is unnecessary '
            'and can be used to identify your location.'
        )
        for zip_code in zip_codes[:3]:
            recommendations.append(
                f"  • Found: '{zip_code['text']}' in {zip_code['section']}"
            )

    # ── Excessive location mentions throughout resume ─────────────────────
    non_header_locations = [
        loc for loc in detected_locations
        if loc['section'] != 'contact_header' and loc['type'] in ['gpe', 'loc']
    ]
    if len(non_header_locations) > 3:
        recommendations.append(
            '🟡 Consider reducing location mentions throughout your resume. '
            'City/State in the contact header is sufficient.'
        )

    # ── General best practice (shown when serious issues exist) ──────────
    if addresses or zip_codes:
        recommendations.append(
            "\n💡 Best Practice: Include only 'City, State' in your contact header. "
            "Remove all other location details."
        )

    return recommendations


def calculate_location_penalty(
    detected_locations: List[Dict],
    privacy_risk: str
) -> float:
    """
    Calculate the score penalty for location privacy issues.

    📌 TEACHING NOTE — Penalty Design (business logic):
        Penalty is applied to the ATS Compatibility score (max 15 pts).

        No risk                → 0.0 pts penalty
        Low risk only          → 2.0 pts penalty
        Medium risk            → 3.0 pts penalty
        Address OR ZIP         → 4.0 pts penalty
        Address AND ZIP        → 5.0 pts penalty (worst case)

        The maximum penalty is 5 points — about 1/3 of the ATS compatibility
        score (15 pts). Severe but not catastrophic — location issues shouldn't
        completely dominate the overall score.

    📌 TEACHING NOTE — Why check location types again?
        assess_privacy_risk() already classified the risk level.
        But for the PENALTY calculation, we need more granularity:
        - address AND zip = worse than just one of them
        - So we check for both types again here.

        An alternative design: calculate the penalty inside assess_privacy_risk()
        and return both risk level and penalty together. Trade-off: simpler call
        site vs more complex assess_privacy_risk() function.

    Args:
        detected_locations: List of problematic location dicts
        privacy_risk: Risk string from assess_privacy_risk()

    Returns:
        Float penalty between 0.0 and 5.0
    """
    if privacy_risk == 'none':
        return 0.0  # No issues → no penalty

    has_address = any(loc['type'] == 'address' for loc in detected_locations)
    has_zip     = any(loc['type'] == 'zip'     for loc in detected_locations)

    # Worst case: both an address AND a ZIP code found
    if has_address and has_zip:
        return 5.0

    # Either an address OR a ZIP code (but not both)
    elif has_address or has_zip:
        return 4.0

    # Medium risk: many location mentions but no address/ZIP
    if privacy_risk == 'medium':
        return 3.0

    # Low risk: some location mentions, not dangerous
    if privacy_risk == 'low':
        return 2.0

    return 0.0  # Fallback (should not be reached)