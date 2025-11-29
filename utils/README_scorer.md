# Scoring Engine Module

## Overview

The scoring engine calculates the overall ATS compatibility score and all component scores for resume analysis. It implements a comprehensive scoring algorithm with proper bounds checking and penalty/bonus application.

## Scoring Components

### 1. Formatting Score (0-20 points)
- **Section Presence (10 points)**: Awards points for having key sections
  - Experience: 3 points
  - Education: 2 points
  - Skills: 2 points
  - Summary: 1.5 points
  - Projects: 1.5 points
- **Bullet Point Usage (5 points)**: Based on number of bullet points
- **Structure and Organization (5 points)**: Based on number of well-organized sections

### 2. Keywords and Skills Score (0-25 points)
- **Base Keyword Count (10 points)**: Based on number of extracted keywords
- **Skills Count (10 points)**: Based on number of identified skills
- **Job Description Matching (5 points)**: Bonus for keyword overlap with JD (if provided)

### 3. Content Quality Score (0-25 points)
- **Action Verbs Usage (10 points)**: Based on number of action verbs detected
- **Quantifiable Achievements (5 points)**: Based on metrics, percentages, and numbers
- **Grammar Quality (10 points)**: Starts at 10, reduced by grammar penalty

### 4. Skill Validation Score (0-15 points)
- Formula: (validated_skills / total_skills) × 15
- Directly uses the validation score from skill validator module

### 5. ATS Compatibility Score (0-15 points)
- Starts at 15 points
- Deducts for location privacy issues (0-5 points)
- Deducts for ATS-unfriendly formatting elements
- Bonus for clean, parseable structure

## Overall Score Calculation

1. Sum all component scores (base score)
2. Apply bonuses:
   - Excellent skill validation (≥90%): +2 points
   - Good skill validation (≥80%): +1 point
   - Perfect grammar (0 errors): +2 points
3. Ensure final score is bounded between 0-100

## Score Interpretation

- **90-100**: Excellent - Highly optimized for ATS
- **80-89**: Great - Should perform well with most ATS
- **70-79**: Good - ATS-friendly with minor improvements needed
- **60-69**: Fair - Needs improvements for full ATS compatibility
- **50-59**: Below Average - Significant improvements needed
- **0-49**: Poor - Major revisions required

## Usage Example

```python
from utils.scorer import calculate_overall_score

# Calculate overall score
score_results = calculate_overall_score(
    text=resume_text,
    sections=extracted_sections,
    skills=extracted_skills,
    keywords=extracted_keywords,
    action_verbs=detected_action_verbs,
    skill_validation_results=validation_results,
    grammar_results=grammar_check_results,
    location_results=location_detection_results,
    jd_keywords=jd_keywords  # Optional
)

# Access results
print(f"Overall Score: {score_results['overall_score']}")
print(f"Interpretation: {score_results['overall_interpretation']}")
print(f"Formatting: {score_results['formatting_score']}/20")
print(f"Keywords: {score_results['keywords_score']}/25")
print(f"Content: {score_results['content_score']}/25")
print(f"Skill Validation: {score_results['skill_validation_score']}/15")
print(f"ATS Compatibility: {score_results['ats_compatibility_score']}/15")
```

## Helper Functions

### `generate_strengths()`
Generates a list of resume strengths based on high-performing components.

### `generate_critical_issues()`
Identifies critical issues that need immediate attention (grammar errors, privacy risks, very low scores).

### `generate_improvements()`
Suggests areas for improvement based on moderate scores.

### `generate_score_interpretation()`
Provides a human-readable interpretation of the overall score.

### `generate_score_breakdown_messages()`
Generates interpretation messages for each component score.

## Requirements Validation

This module validates the following requirements:
- **9.1**: Formatting score calculation (0-20 points)
- **9.2**: Keywords and skills score calculation (0-25 points)
- **9.3**: Content quality score calculation (0-25 points)
- **9.4**: Skill validation score calculation (0-15 points)
- **9.5**: ATS compatibility score calculation (0-15 points)
- **9.6**: Overall score aggregation
- **9.7**: Apply penalties and bonuses

## Notes

- All scores are bounded within their specified ranges
- The scoring algorithm is designed to be fair and comprehensive
- Penalties are applied for grammar errors and location privacy issues
- Bonuses reward excellent skill validation and perfect grammar
- The final score is always between 0 and 100
