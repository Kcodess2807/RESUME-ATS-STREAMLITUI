# Module 05: Skills & Experience Analysis (25 min)

## Objective
Analyze the quality of experience descriptions and validate skill claims.

## Files to Create
- `app/core/analyzer.py`
- `data/industry_keywords.json`

## Script

### Part 1: Why Quality Matters (3 min)

"Two resumes can have the same skills listed, but very different quality.

**Resume A:**
```
- Worked with Python
- Did some projects
- Helped the team
```

**Resume B:**
```
- Developed Python microservices serving 1M+ requests/day
- Led migration project reducing costs by 40%
- Mentored 3 junior developers
```

**What makes B better?**
- Action verbs (Developed, Led, Mentored)
- Quantification (1M+, 40%, 3)
- Specificity (microservices, migration, costs)

We'll teach the system to recognize quality."

### Part 2: Action Verb Detection (6 min)

**Create app/core/analyzer.py:**

```python
"""
Experience Analyzer Module
Analyzes quality of experience descriptions
"""

import re
import json
from typing import Dict, List, Tuple
from pathlib import Path


def load_action_verbs() -> set:
    """
    Load action verbs from database
    
    Why action verbs matter:
    - 'Developed' > 'Worked on'
    - 'Led' > 'Helped with'
    - 'Achieved' > 'Did'
    
    Strong verbs show impact and ownership
    """
    with open('data/action_verbs.json', 'r') as f:
        return set(json.load(f))


def detect_action_verbs(text: str, action_verbs: set) -> Dict:
    """
    Find action verbs in experience section
    
    Returns:
        - List of verbs found
        - Count of strong verbs
        - Percentage of sentences with action verbs
    """
    text_lower = text.lower()
    found_verbs = []
    
    # Find all action verbs
    for verb in action_verbs:
        # Match word boundaries
        pattern = r'\b' + re.escape(verb) + r'(ed|ing|s)?\b'
        matches = re.findall(pattern, text_lower)
        
        if matches:
            found_verbs.append(verb)
    
    # Count sentences
    sentences = re.split(r'[.!?\n]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Count sentences starting with action verbs
    strong_starts = 0
    for sentence in sentences:
        words = sentence.lower().split()
        if words and any(verb in words[0] for verb in action_verbs):
            strong_starts += 1
    
    # Calculate percentage
    percentage = (strong_starts / len(sentences) * 100) if sentences else 0
    
    return {
        'found_verbs': found_verbs,
        'count': len(found_verbs),
        'strong_starts': strong_starts,
        'total_sentences': len(sentences),
        'percentage': round(percentage, 1)
    }
```

**Explain:**
"The regex pattern `r'\b' + verb + r'(ed|ing|s)?\b'`:
- `\b`: Word boundary
- `(ed|ing|s)?`: Optional endings
- Matches: 'develop', 'developed', 'developing', 'develops'

Why count sentence starts?
- 'Developed X' is stronger than 'Was involved in developing X'
- First word sets the tone
- ATS systems weight sentence starts higher

The percentage tells us:
- 80%+ = Excellent (most sentences action-driven)
- 50-80% = Good
- <50% = Needs improvement"

### Part 3: Quantification Detection (7 min)

```python
def detect_quantification(text: str) -> Dict:
    """
    Find numbers and metrics in experience
    
    Why quantification matters:
    - 'Improved performance' (vague)
    - 'Improved performance by 40%' (specific)
    - Numbers prove impact
    """
    # Patterns for different number formats
    patterns = {
        'percentage': r'\d+%',
        'money': r'\$[\d,]+(?:\.\d{2})?[KMB]?',
        'large_numbers': r'\d+[KMB]\+?',
        'ranges': r'\d+-\d+',
        'plain_numbers': r'\b\d+\b'
    }
    
    metrics = {
        'percentages': [],
        'money': [],
        'large_numbers': [],
        'ranges': [],
        'plain_numbers': []
    }
    
    # Find all matches
    for metric_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        metrics[metric_type] = matches
    
    # Count total quantifications
    total = sum(len(v) for v in metrics.values())
    
    # Count sentences with numbers
    sentences = re.split(r'[.!?\n]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    quantified_sentences = sum(
        1 for s in sentences 
        if re.search(r'\d', s)
    )
    
    # Calculate percentage
    percentage = (quantified_sentences / len(sentences) * 100) if sentences else 0
    
    return {
        'metrics': metrics,
        'total_count': total,
        'quantified_sentences': quantified_sentences,
        'total_sentences': len(sentences),
        'percentage': round(percentage, 1)
    }
```

**Explain:**
"Different number formats:
- **Percentage**: '40%', '2.5%'
- **Money**: '$100K', '$2.5M', '$50,000'
- **Large numbers**: '1M+', '500K', '10B'
- **Ranges**: '5-10', '100-200'
- **Plain**: '3', '15', '100'

Why detect all formats?
- Different industries use different formats
- Tech: '1M users', '99.9% uptime'
- Finance: '$2M revenue', '15% growth'
- All show measurable impact

The regex `\$[\d,]+(?:\.\d{2})?[KMB]?`:
- `\$`: Dollar sign
- `[\d,]+`: Digits and commas
- `(?:\.\d{2})?`: Optional cents
- `[KMB]?`: Optional K/M/B suffix"

### Part 4: Experience Quality Scoring (6 min)

```python
def analyze_experience_section(
    experience_text: str,
    action_verbs: set,
    full_text: str
) -> Dict:
    """
    Complete experience quality analysis
    
    Scores based on:
    1. Action verb usage (40%)
    2. Quantification (40%)
    3. Length and detail (20%)
    """
    # Detect action verbs
    verb_analysis = detect_action_verbs(experience_text, action_verbs)
    
    # Detect quantification
    quant_analysis = detect_quantification(experience_text)
    
    # Analyze length and detail
    word_count = len(experience_text.split())
    sentence_count = len(re.split(r'[.!?\n]', experience_text))
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    # Calculate component scores (0-100)
    
    # Action verb score
    verb_score = min(100, verb_analysis['percentage'] * 1.25)
    
    # Quantification score
    quant_score = min(100, quant_analysis['percentage'] * 1.25)
    
    # Length score (optimal: 200-500 words)
    if word_count < 100:
        length_score = word_count / 100 * 50
    elif word_count <= 500:
        length_score = 50 + ((word_count - 100) / 400 * 50)
    else:
        length_score = max(50, 100 - ((word_count - 500) / 500 * 50))
    
    # Overall experience score (weighted average)
    overall_score = (
        verb_score * 0.4 +
        quant_score * 0.4 +
        length_score * 0.2
    )
    
    return {
        'verb_analysis': verb_analysis,
        'quantification': quant_analysis,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_sentence_length': round(avg_sentence_length, 1),
        'scores': {
            'action_verbs': round(verb_score, 1),
            'quantification': round(quant_score, 1),
            'length': round(length_score, 1),
            'overall': round(overall_score, 1)
        }
    }
```

**Explain:**
"Scoring logic:

**Action Verb Score (40%)**:
- 80% sentences with action verbs = 100 points
- 40% sentences = 50 points
- Linear scaling

**Quantification Score (40%)**:
- Same logic as action verbs
- More numbers = higher score

**Length Score (20%)**:
- Too short (<100 words) = incomplete
- Sweet spot (200-500 words) = detailed but concise
- Too long (>500 words) = verbose, loses focus

Why these weights?
- Action verbs + quantification = 80% (most important)
- Length = 20% (supporting factor)
- Based on ATS research and recruiter feedback"

### Part 5: Skill Context Analysis (3 min)

```python
def analyze_skill_context(skill: str, text: str) -> Dict:
    """
    Analyze how a skill is mentioned
    
    Context matters:
    - 'Expert in Python' > 'Familiar with Python'
    - 'Led Python projects' > 'Used Python'
    """
    text_lower = text.lower()
    skill_lower = skill.lower()
    
    # Find sentences mentioning the skill
    sentences = re.split(r'[.!?\n]', text)
    relevant_sentences = [
        s for s in sentences 
        if skill_lower in s.lower()
    ]
    
    # Check for proficiency indicators
    proficiency_keywords = {
        'expert': ['expert', 'advanced', 'proficient', 'mastery'],
        'intermediate': ['experienced', 'skilled', 'competent'],
        'beginner': ['familiar', 'basic', 'learning', 'exposure']
    }
    
    proficiency_level = 'not_specified'
    for level, keywords in proficiency_keywords.items():
        for keyword in keywords:
            if any(keyword in s.lower() for s in relevant_sentences):
                proficiency_level = level
                break
        if proficiency_level != 'not_specified':
            break
    
    # Check for action verbs with this skill
    action_verbs = load_action_verbs()
    actions_with_skill = []
    
    for sentence in relevant_sentences:
        for verb in action_verbs:
            if verb in sentence.lower():
                actions_with_skill.append(verb)
    
    return {
        'skill': skill,
        'mention_count': len(relevant_sentences),
        'proficiency_level': proficiency_level,
        'actions': list(set(actions_with_skill)),
        'context_sentences': relevant_sentences[:3]  # First 3
    }
```

**Explain:**
"Context analysis helps us understand:
- How often is the skill mentioned?
- What proficiency level is claimed?
- What actions were taken with this skill?

This feeds into skill validation (Module 07) where we check if claims are backed by project descriptions."

## Create Supporting Data

**Create data/industry_keywords.json:**

```json
{
  "software_engineering": [
    "agile", "scrum", "CI/CD", "microservices", "API", "REST",
    "scalability", "performance", "optimization", "architecture"
  ],
  "data_science": [
    "machine learning", "deep learning", "neural networks", "model",
    "training", "prediction", "accuracy", "dataset", "feature engineering"
  ],
  "product_management": [
    "roadmap", "stakeholder", "requirements", "user stories", "sprint",
    "backlog", "prioritization", "metrics", "KPI"
  ]
}
```

## Testing the Analyzer

**Create test script:**

```python
# test_analyzer.py
from app.core.analyzer import (
    load_action_verbs,
    analyze_experience_section
)

sample_experience = """
Developed Python microservices handling 1M+ requests daily.
Led team of 5 engineers in migration project.
Reduced infrastructure costs by 40% through optimization.
Implemented CI/CD pipeline improving deployment speed by 3x.
"""

action_verbs = load_action_verbs()
result = analyze_experience_section(sample_experience, action_verbs, "")

print("Action Verb Score:", result['scores']['action_verbs'])
print("Quantification Score:", result['scores']['quantification'])
print("Overall Score:", result['scores']['overall'])
print("\nVerbs found:", result['verb_analysis']['found_verbs'])
print("Metrics found:", result['quantification']['total_count'])
```

## Key Concepts to Emphasize

1. **Action Verbs** - Show ownership and impact
2. **Quantification** - Prove results with numbers
3. **Context** - How skills are described matters
4. **Scoring Logic** - Weighted components
5. **Quality > Quantity** - Better to have 3 strong bullets than 10 weak ones

## Common Issues

**Issue**: "All sentences detected as having action verbs"
**Solution**: Check word boundary regex, ensure matching first word

**Issue**: "Numbers in dates counted as metrics"
**Solution**: Filter out year patterns (2020-2023)

**Issue**: "Score too harsh/lenient"
**Solution**: Adjust weights and thresholds

## Checkpoint

Students should have:
- [ ] Action verb detection working
- [ ] Quantification detection working
- [ ] Experience scoring working
- [ ] Skill context analysis working
- [ ] Test script showing reasonable scores

## Transition to Module 06

"Now we can analyze resume quality. Next, we'll parse job descriptions and compare them with resumes to find gaps and matches."
