# Location Detector Module

## Overview

The Location Detector module identifies sensitive location information in resumes to provide privacy recommendations. It uses spaCy Named Entity Recognition (NER) and regex patterns to detect addresses, cities, states, and zip codes.

## Features

- **Address Detection**: Identifies full street addresses using regex patterns
- **City/State Detection**: Uses spaCy NER to detect GPE (Geopolitical Entity) and LOC (Location) entities
- **Zip Code Detection**: Detects 5-digit and 9-digit zip codes
- **Contact Header Exemption**: Allows city/state in contact header (acceptable practice)
- **Privacy Risk Assessment**: Categorizes risk as high, medium, low, or none
- **Recommendations**: Generates specific suggestions for improving privacy
- **Penalty Calculation**: Applies 3-5 point penalty for privacy issues

## Requirements Validation

This module validates the following requirements:

- **8.1**: Address detection using spaCy NER (GPE, LOC tags) and regex patterns
- **8.2**: City and state combination detection
- **8.3**: Zip code detection (5-digit and 9-digit)
- **8.4**: Contact header exemption logic
- **8.5**: Privacy risk assessment and location removal recommendations
- **8.6**: Privacy penalty calculation (3-5 points)

## Main Functions

### `detect_location_info(text: str, nlp: spacy.Language = None) -> Dict`

Main function that performs comprehensive location detection.

**Returns:**
```python
{
    "location_found": bool,
    "detected_locations": [
        {
            "text": "123 Main Street",
            "type": "address",  # or "zip", "gpe", "loc"
            "section": "contact_header",  # or "experience", "education", "other"
            "start": 45,
            "end": 60
        }
    ],
    "privacy_risk": "high",  # or "medium", "low", "none"
    "recommendations": ["Remove full street addresses...", ...],
    "penalty_applied": 4.0  # 0-5 points
}
```

### `detect_locations_with_ner(text: str, nlp: spacy.Language) -> List[Dict]`

Uses spaCy NER to detect GPE and LOC entities.

### `detect_street_addresses(text: str) -> List[Dict]`

Uses regex to detect street addresses with common suffixes (Street, Avenue, Road, etc.).

### `detect_zip_codes(text: str) -> List[Dict]`

Uses regex to detect 5-digit and 9-digit zip codes.

### `is_acceptable_location(location_text: str, location_type: str, section: str) -> bool`

Determines if a location mention is acceptable (e.g., city/state in contact header).

### `assess_privacy_risk(detected_locations: List[Dict]) -> str`

Assesses overall privacy risk level:
- **High**: Full address or zip code present
- **Medium**: Multiple location mentions
- **Low**: Few location mentions
- **None**: No problematic locations

### `calculate_location_penalty(detected_locations: List[Dict], privacy_risk: str) -> float`

Calculates penalty for ATS compatibility score:
- Address + Zip: 5 points
- Address OR Zip: 4 points
- Medium risk: 3 points
- Low risk: 2 points
- No risk: 0 points

### `generate_privacy_recommendations(detected_locations: List[Dict]) -> List[str]`

Generates specific recommendations for improving privacy.

### `generate_location_feedback(location_results: Dict) -> List[str]`

Generates user-friendly feedback messages.

## Usage Example

```python
from utils.location_detector import detect_location_info
from utils.model_loader import load_spacy_model

# Load spaCy model
nlp = load_spacy_model()

# Analyze resume text
resume_text = """
John Doe
123 Main Street, Apt 4B
Springfield, IL 62701
Email: john@example.com

EXPERIENCE
Software Engineer at Tech Corp
Chicago, IL
...
"""

# Detect location information
results = detect_location_info(resume_text, nlp)

print(f"Privacy Risk: {results['privacy_risk']}")
print(f"Penalty: {results['penalty_applied']} points")
print(f"Locations Found: {len(results['detected_locations'])}")

for recommendation in results['recommendations']:
    print(recommendation)
```

## Detection Patterns

### Street Address Pattern
```regex
\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b
```

Examples:
- "123 Main Street"
- "456 Oak Avenue"
- "789 Elm Road"

### Zip Code Pattern
```regex
\b\d{5}(?:-\d{4})?\b
```

Examples:
- "62701"
- "90210-1234"

### State Abbreviations
All 50 US state abbreviations (AL, AK, AZ, ..., WY)

## Privacy Best Practices

The module recommends:

1. **Contact Header**: Include only "City, State" (e.g., "Chicago, IL")
2. **Remove**: Full street addresses
3. **Remove**: Zip codes
4. **Remove**: Excessive location mentions in experience/education sections

## Contact Header Exemption

The module allows city/state combinations in the contact header (first 200 characters) as this is standard practice and provides necessary location context without compromising privacy.

## Integration with Scoring System

The location detector integrates with the ATS compatibility score:

- **No issues**: 0 point penalty
- **Low risk**: 2 point penalty
- **Medium risk**: 3 point penalty
- **High risk**: 4-5 point penalty

Maximum penalty: 5 points from the 15-point ATS compatibility component.

## Error Handling

- Gracefully handles missing spaCy model (loads via model_loader)
- Returns empty results if text is empty
- Handles regex matching errors
- Provides user-friendly error messages

## Testing

The module should be tested with:

- Resumes with full addresses
- Resumes with only city/state
- Resumes with zip codes
- Various address formats
- International addresses
- Edge cases (city names that are common words)

## Future Enhancements

- International address format support
- PO Box detection
- Apartment/suite number detection
- More sophisticated section detection
- Machine learning-based location classification
