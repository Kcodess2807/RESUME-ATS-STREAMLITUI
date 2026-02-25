# Module 06: JD Parser & Comparison (20 min)

## Objective
Parse job descriptions and compare them with resumes to identify gaps and matches.

## Files to Create
- `app/core/comparator.py` (Part 1 - JD parsing)

## Script

### Part 1: Why JD Comparison Matters (2 min)

"A resume isn't good or bad in isolation. It's good or bad for a specific job.

**The Problem:**
- Job description asks for: Python, AWS, Docker, Kubernetes
- Resume mentions: Python, Azure, Docker
- Gap: AWS, Kubernetes
- Mismatch: Azure (not requested)

**Our Solution:**
- Extract keywords from JD
- Compare with resume keywords
- Calculate match percentage
- Identify missing critical skills
- Suggest additions

This is the most actionable feedback we can give."

### Part 2: JD Keyword Extraction (6 min)

**Create app/core/comparator.py:**

```python
"""
Job Description Comparator Module
Compares resumes with job descriptions
"""

import re
from typing import Dict, List, Set, Tuple
from collections import Counter


def extract_jd_keywords(jd_text: str, nlp) -> Dict:
    """
    Extract keywords from job description
    
    What we extract:
    - Required skills (MUST have)
    - Preferred skills (NICE to have)
    - Technologies mentioned
    - Responsibilities
    - Qualifications
    """
    # Clean text
    jd_text = jd_text.strip()
    
    # Detect required vs preferred
    required_section = ""
    preferred_section = ""
    
    # Split by common section headers
    required_patterns = [
        r'required\s+(?:skills|qualifications)',
        r'must\s+have',
        r'requirements',
        r'minimum\s+qualifications'
    ]
    
    preferred_patterns = [
        r'preferred\s+(?:skills|qualifications)',
        r'nice\s+to\s+have',
        r'bonus',
        r'plus'
    ]
    
    # Find required section
    for pattern in required_patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            start = match.start()
            # Find next section or end
            end = len(jd_text)
            for pref_pattern in preferred_patterns:
                pref_match = re.search(pref_pattern, jd_text[start:], re.IGNORECASE)
                if pref_match:
                    end = start + pref_match.start()
                    break
            required_section = jd_text[start:end]
            break
    
    # Find preferred section
    for pattern in preferred_patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            preferred_section = jd_text[match.start():]
            break
    
    # If no sections found, treat all as required
    if not required_section and not preferred_section:
        required_section = jd_text
    
    # Extract keywords using spaCy
    required_keywords = _extract_keywords_from_text(required_section, nlp)
    preferred_keywords = _extract_keywords_from_text(preferred_section, nlp)
    
    # Extract all keywords for general matching
    all_keywords = _extract_keywords_from_text(jd_text, nlp)
    
    return {
        'required': required_keywords,
        'preferred': preferred_keywords,
        'all': all_keywords,
        'required_text': required_section,
        'preferred_text': preferred_section
    }


def _extract_keywords_from_text(text: str, nlp) -> List[str]:
    """
    Helper function to extract keywords from text
    
    Focus on:
    - Technical terms (nouns)
    - Skills (proper nouns)
    - Tools and technologies
    """
    if not text:
        return []
    
    doc = nlp(text)
    keywords = []
    
    for token in doc:
        # Skip short words and stop words
        if len(token.text) < 3 or token.is_stop:
            continue
        
        # Extract nouns and proper nouns
        if token.pos_ in ['NOUN', 'PROPN']:
            keywords.append(token.lemma_.lower())
    
    # Also extract multi-word technical terms
    # e.g., "machine learning", "cloud computing"
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:
            keywords.append(chunk.text.lower())
    
    return keywords
```

**Explain:**
"JD structure typically has:
- **Required**: Must-have skills (deal breakers)
- **Preferred**: Nice-to-have skills (bonus points)

Why separate them?
- Missing required skill = major gap
- Missing preferred skill = minor gap
- Different weights in scoring

Noun chunks:
- Single words: 'Python', 'AWS'
- Multi-word: 'machine learning', 'cloud computing'
- Both are important technical terms"

### Part 3: Resume-JD Matching (7 min)

```python
def compare_resume_with_jd(
    resume_text: str,
    resume_keywords: List[str],
    resume_skills: List[str],
    jd_text: str,
    jd_keywords: Dict,
    embedder,
    nlp
) -> Dict:
    """
    Compare resume with job description
    
    Returns:
    - Match percentage
    - Missing keywords
    - Matched keywords
    - Recommendations
    """
    # Get all resume terms (keywords + skills)
    resume_terms = set(resume_keywords + [s.lower() for s in resume_skills])
    
    # Get JD terms
    jd_required = set(jd_keywords['required'])
    jd_preferred = set(jd_keywords['preferred'])
    jd_all = set(jd_keywords['all'])
    
    # Find matches and gaps
    required_matches = resume_terms & jd_required
    required_missing = jd_required - resume_terms
    
    preferred_matches = resume_terms & jd_preferred
    preferred_missing = jd_preferred - resume_terms
    
    # Calculate match percentages
    required_match_pct = (
        len(required_matches) / len(jd_required) * 100
        if jd_required else 100
    )
    
    preferred_match_pct = (
        len(preferred_matches) / len(jd_preferred) * 100
        if jd_preferred else 100
    )
    
    # Overall match (weighted: required 70%, preferred 30%)
    overall_match_pct = (
        required_match_pct * 0.7 +
        preferred_match_pct * 0.3
    )
    
    # Identify critical missing skills
    # (required skills mentioned multiple times in JD)
    jd_text_lower = jd_text.lower()
    critical_missing = []
    
    for skill in required_missing:
        count = jd_text_lower.count(skill)
        if count >= 2:  # Mentioned 2+ times = critical
            critical_missing.append({
                'skill': skill,
                'mentions': count
            })
    
    # Sort by mention count
    critical_missing.sort(key=lambda x: x['mentions'], reverse=True)
    
    return {
        'match_percentage': round(overall_match_pct, 1),
        'required_match': round(required_match_pct, 1),
        'preferred_match': round(preferred_match_pct, 1),
        'matched_required': list(required_matches),
        'missing_required': list(required_missing),
        'matched_preferred': list(preferred_matches),
        'missing_preferred': list(preferred_missing),
        'critical_missing': critical_missing[:5]  # Top 5
    }
```

**Explain:**
"Matching logic:

**Set Operations:**
- `resume_terms & jd_required`: Intersection (what's in both)
- `jd_required - resume_terms`: Difference (what's missing)

**Weighted Scoring:**
- Required skills: 70% weight (more important)
- Preferred skills: 30% weight (nice to have)

**Critical Missing:**
- If a skill is mentioned 2+ times in JD = very important
- 'Python' mentioned 5 times = critical
- 'Git' mentioned once = less critical

**Why this matters:**
- 80%+ match = strong candidate
- 60-80% = good with some gaps
- <60% = significant gaps"

### Part 4: Generating Recommendations (5 min)

```python
def generate_jd_recommendations(comparison: Dict) -> List[str]:
    """
    Generate actionable recommendations based on comparison
    
    Returns list of specific actions to take
    """
    recommendations = []
    
    # Check overall match
    match_pct = comparison['match_percentage']
    
    if match_pct >= 80:
        recommendations.append(
            "✅ Strong match! Your resume aligns well with this job."
        )
    elif match_pct >= 60:
        recommendations.append(
            "⚠️ Good match with some gaps. Address missing skills below."
        )
    else:
        recommendations.append(
            "❌ Significant gaps. Consider if this role is a good fit."
        )
    
    # Critical missing skills
    if comparison['critical_missing']:
        recommendations.append(
            "\n🔴 Critical Missing Skills (mentioned multiple times):"
        )
        for item in comparison['critical_missing']:
            skill = item['skill']
            mentions = item['mentions']
            recommendations.append(
                f"  • {skill.title()} (mentioned {mentions}x) - "
                f"Add this to your skills section and mention in experience"
            )
    
    # Required missing skills
    if comparison['missing_required']:
        recommendations.append(
            "\n⚠️ Missing Required Skills:"
        )
        for skill in comparison['missing_required'][:5]:
            recommendations.append(
                f"  • {skill.title()} - Add if you have experience with this"
            )
    
    # Preferred missing skills
    if comparison['missing_preferred']:
        recommendations.append(
            "\n💡 Missing Preferred Skills (bonus points):"
        )
        for skill in comparison['missing_preferred'][:3]:
            recommendations.append(
                f"  • {skill.title()} - Consider adding if applicable"
            )
    
    # Matched skills
    if comparison['matched_required']:
        recommendations.append(
            f"\n✅ You match {len(comparison['matched_required'])} "
            f"required skills - great!"
        )
    
    return recommendations
```

**Explain:**
"Recommendation tiers:

**Critical (🔴):**
- Skills mentioned 2+ times
- Highest priority to add
- Can make or break application

**Required (⚠️):**
- Listed in requirements section
- Important but not critical
- Add if you have them

**Preferred (💡):**
- Nice-to-have skills
- Bonus points
- Lower priority

**Actionable format:**
- Not just 'missing Python'
- But 'Add Python to skills section and mention in experience'
- Tells user exactly what to do"

## Testing the Comparator

**Create test script:**

```python
# test_comparator.py
from app.core.comparator import (
    extract_jd_keywords,
    compare_resume_with_jd,
    generate_jd_recommendations
)
from app.core.processor import load_spacy_model

nlp = load_spacy_model()

# Sample JD
jd_text = """
Required Skills:
- Python, Django, PostgreSQL
- AWS, Docker, Kubernetes
- 3+ years experience

Preferred Skills:
- React, TypeScript
- CI/CD experience
"""

# Sample resume data
resume_keywords = ['python', 'django', 'postgresql', 'docker', 'react']
resume_skills = ['Python', 'Django', 'PostgreSQL', 'Docker', 'React']

# Extract JD keywords
jd_keywords = extract_jd_keywords(jd_text, nlp)

# Compare
comparison = compare_resume_with_jd(
    resume_text="",
    resume_keywords=resume_keywords,
    resume_skills=resume_skills,
    jd_text=jd_text,
    jd_keywords=jd_keywords,
    embedder=None,
    nlp=nlp
)

print("Match Percentage:", comparison['match_percentage'])
print("Missing Required:", comparison['missing_required'])
print("Critical Missing:", comparison['critical_missing'])

# Generate recommendations
recs = generate_jd_recommendations(comparison)
for rec in recs:
    print(rec)
```

## Key Concepts to Emphasize

1. **Required vs Preferred** - Different weights
2. **Set Operations** - Efficient matching
3. **Frequency Analysis** - Critical skills mentioned multiple times
4. **Actionable Feedback** - Tell users what to do
5. **Weighted Scoring** - Not all matches are equal

## Common Issues

**Issue**: "All JD text treated as required"
**Solution**: Add more section header patterns

**Issue**: "Too many false positive matches"
**Solution**: Use lemmatization, check word boundaries

**Issue**: "Match percentage too low"
**Solution**: Check if skills are being extracted properly

## Checkpoint

Students should have:
- [ ] JD keyword extraction working
- [ ] Required/preferred separation working
- [ ] Resume-JD comparison working
- [ ] Match percentage calculating correctly
- [ ] Recommendations generating
- [ ] Test script showing reasonable results

## Transition to Module 07

"We can now match keywords. But 'Python developer' and 'Python programming' are the same thing, even though the words are different. Next, we'll use BERT embeddings for semantic matching - the ML core of our app."
