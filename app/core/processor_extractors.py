"""
Resume Processor Extractors Module
Low-level NLP extraction functions — each extracts one type of information.

📌 TEACHING NOTE — What's in this file?
    Each function here extracts ONE specific type of information from resume text:

    extract_sections()     → splits text into named sections (experience, education...)
    extract_contact_info() → finds email, phone, LinkedIn, GitHub, portfolio URLs
    extract_skills()       → extracts skill names from the skills section + NLP
    extract_projects()     → parses project entries with titles/descriptions/tech
    extract_keywords()     → finds the most important terms (for ATS matching)
    detect_action_verbs()  → finds strong action verbs at the start of bullet lines
    extract_jd_keywords()  → extracts keywords from a job description (same logic)

📌 TEACHING NOTE — Module-level constants (compiled patterns):
    All regex patterns and keyword sets are defined AT THE TOP of the file,
    not inside functions. This is important because:
    1. Regex patterns are compiled ONCE (faster than compiling on every call)
    2. They're easy to find and update in one place
    3. Named constants are self-documenting

📌 TEACHING NOTE — Two complementary techniques used throughout:
    Regex         → fast, precise, rule-based (good for structured patterns like email)
    spaCy NLP     → slower, flexible, meaning-aware (good for flexible things like skills)
    Combined use  → get the benefits of both
"""

import re
import streamlit as st
import spacy
from typing import Dict, List, Optional, Tuple
from collections import Counter
import string


# ── Section Detection Patterns ─────────────────────────────────────────────────

# 📌 TEACHING NOTE — Dictionary of regex patterns per section:
#   SECTION_PATTERNS maps each section NAME to a list of patterns
#   that might appear as the section header in a real resume.
#
#   Why a list of patterns per section?
#   Candidates use different header names:
#   "Work Experience", "Professional Experience", "Employment History"
#   all mean the same thing → map to 'experience' section.
#
#   \b = word boundary (prevents "experienced" from matching "experience")
#   (?:...) = non-capturing group (groups without creating backreference)
#   \s+ = one or more whitespace chars ("work experience" with any spacing)
SECTION_PATTERNS = {
    'summary': [
        r'\b(professional\s+summary|summary|profile|objective|career\s+objective)\b',
    ],
    'experience': [
        r'\b(work\s+experience|professional\s+experience|experience|employment\s+history|work\s+history)\b',
    ],
    'education': [
        r'\b(education|academic\s+background|qualifications)\b',
    ],
    'skills': [
        r'\b(skills|technical\s+skills|core\s+competencies|competencies|expertise)\b',
    ],
    'projects': [
        r'\b(projects|personal\s+projects|key\s+projects|portfolio)\b',
    ]
}

# ── Contact Information Patterns ───────────────────────────────────────────────

# Email: standard format (user@domain.tld)
EMAIL_PATTERN    = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Phone: handles international formats (+1-800-555-1234, (800) 555-1234, etc.)
PHONE_PATTERN    = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

# URLs: LinkedIn, GitHub, and generic portfolio
LINKEDIN_PATTERN  = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
GITHUB_PATTERN    = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
PORTFOLIO_PATTERN = r'(?:https?://)?(?:www\.)?[\w-]+\.(?:com|net|org|io|dev|me)(?:/[\w-]*)?'

# ── Action Verbs Set ───────────────────────────────────────────────────────────

# 📌 TEACHING NOTE — Using a set for ACTION_VERBS:
#   Sets use O(1) lookup (vs O(n) for lists).
#   We check if words ARE IN this set on every line of the resume.
#   For 500+ resume lines × 50 verbs = potentially 25,000 comparisons.
#   O(1) set lookup makes this effectively instant vs O(n) list scan.
#
#   Also: sets automatically deduplicate — no risk of checking the same
#   verb twice if it appears multiple times in the data.
ACTION_VERBS = {
    'achieved', 'adapted', 'administered', 'analyzed', 'architected', 'automated',
    'built', 'collaborated', 'completed', 'conducted', 'configured', 'created',
    'delivered', 'demonstrated', 'designed', 'developed', 'directed', 'drove',
    'enhanced', 'established', 'executed', 'expanded', 'facilitated', 'generated',
    'implemented', 'improved', 'increased', 'initiated', 'integrated', 'launched',
    'led', 'maintained', 'managed', 'optimized', 'organized', 'performed',
    'planned', 'produced', 'programmed', 'reduced', 'resolved', 'streamlined',
    'strengthened', 'supervised', 'supported', 'trained', 'transformed', 'upgraded'
}

# ── Technical Skills Keywords Set ─────────────────────────────────────────────

# 📌 TEACHING NOTE — TECHNICAL_SKILLS_KEYWORDS used as a filter:
#   When spaCy extracts noun phrases or entities, many are NOT skills.
#   ("the company", "recent years", "various clients")
#   We use this set to FILTER: only keep extracted text that contains
#   at least one technical keyword.
#
#   Pattern: extract broadly (spaCy gets lots of things), then filter narrowly
#   (keep only what contains a known tech term).
TECHNICAL_SKILLS_KEYWORDS = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
    'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'express',
    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
    'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'devops'
}


def extract_sections(text: str, nlp: spacy.Language) -> Dict[str, str]:
    """
    Split the resume text into named sections (experience, education, etc.)

    📌 TEACHING NOTE — State Machine Parsing (same pattern as analyzer.py):
        We iterate lines and track "which section are we currently in?"
        using the current_section variable.

        States:
        - current_section = None → not yet inside any section
        - current_section = 'experience' → collecting experience lines

        Transitions:
        - Line matches a section pattern → start that section (save previous)
        - Normal line while in a section → add to section content
        - Blank line while in a section → preserve it in content

    📌 TEACHING NOTE — len(line_stripped) < 100 guard:
        We only consider a line to be a SECTION HEADER if it's short.
        A line with 100+ characters is probably content, not a header.
        Real resume section headers are typically 1-5 words.
        Without this guard, a bullet point mentioning "experience" in a
        long sentence would incorrectly trigger a section change.

    📌 TEACHING NOTE — break after finding section:
        Once we find a matching pattern for a line, we set section_found = True
        and break out of both inner loops (patterns and sections).
        This prevents checking remaining sections after a match is found.
        Efficiency: skip unnecessary comparisons.

    Args:
        text: Full resume text
        nlp: spaCy language model (not used directly here — passed for API consistency)

    Returns:
        Dict mapping section names to their text content
    """
    # Initialize all sections to empty strings
    sections = {'summary': '', 'experience': '', 'education': '', 'skills': '', 'projects': ''}

    lines           = text.split('\n')
    current_section = None    # Which section we're currently collecting
    section_content = []      # Lines accumulated for current section

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower    = line_stripped.lower()

        # Blank lines are preserved inside sections (maintain paragraph structure)
        if not line_stripped:
            if current_section and section_content:
                section_content.append(line)
            continue

        section_found = False

        # Check if this line is a section header
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    # Only treat it as a header if the line is short enough
                    if len(line_stripped) < 100:
                        # Save the current section before starting the new one
                        if current_section and section_content:
                            sections[current_section] = '\n'.join(section_content).strip()
                        # Start the new section
                        current_section = section_name
                        section_content = []
                        section_found   = True
                        break   # Stop checking patterns for this section
            if section_found:
                break   # Stop checking other section names

        # If not a header and we're inside a section, add to current section's content
        if not section_found and current_section:
            section_content.append(line)

    # Don't forget to save the LAST section after the loop ends
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content).strip()

    return sections


def extract_contact_info(text: str, nlp: spacy.Language) -> Dict[str, Optional[str]]:
    """
    Extract contact details (email, phone, LinkedIn, GitHub, portfolio) from resume.

    📌 TEACHING NOTE — re.search() vs re.findall() vs re.finditer():
        re.search(pattern, text) → finds FIRST match, returns Match object or None
        re.findall(pattern, text) → returns list of all matches as strings
        re.finditer(pattern, text) → returns iterator of Match objects

        For contact info, we use re.search() — we only want the FIRST email,
        FIRST phone number, etc. Most resumes have exactly one of each.

    📌 TEACHING NOTE — Portfolio URL filtering:
        The PORTFOLIO_PATTERN is broad — it matches many URLs.
        But we don't want to mistake the LinkedIn or GitHub URL for the portfolio.
        So we iterate portfolio matches and SKIP any that contain 'linkedin' or 'github':

        for match in portfolio_matches:
            url = match.group(0)
            if 'linkedin' not in url.lower() and 'github' not in url.lower():
                contact_info['portfolio'] = url
                break   # Take only the first non-LinkedIn, non-GitHub URL

        This is a filter inside a loop — a common pattern for "find first match
        that satisfies an extra condition."

    📌 TEACHING NOTE — contact_info initialized with None values:
        {'email': None, 'phone': None, ...}
        We initialize ALL expected keys to None.
        This guarantees callers can access any key without KeyError,
        even if that contact detail wasn't found in the resume.
        if match: sets it to the found value.

    Args:
        text: Full resume text
        nlp: spaCy model (not used here — passed for API consistency)

    Returns:
        Dict with email, phone, linkedin, github, portfolio — each string or None
    """
    contact_info = {
        'email':     None,
        'phone':     None,
        'linkedin':  None,
        'github':    None,
        'portfolio': None
    }

    # Each pattern: search and extract first match
    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        contact_info['email'] = email_match.group(0)

    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        contact_info['phone'] = phone_match.group(0)

    linkedin_match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group(0)

    github_match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = github_match.group(0)

    # Portfolio: find first URL that isn't LinkedIn or GitHub
    portfolio_matches = re.finditer(PORTFOLIO_PATTERN, text, re.IGNORECASE)
    for match in portfolio_matches:
        url = match.group(0)
        if 'linkedin' not in url.lower() and 'github' not in url.lower():
            contact_info['portfolio'] = url
            break   # Take only the first qualifying URL

    return contact_info


def extract_skills(text: str, skills_section: str, nlp: spacy.Language) -> List[str]:
    """
    Extract a list of skills using both the skills section and NLP entity detection.

    📌 TEACHING NOTE — Two-Source Extraction Strategy:
        Source 1: Parse the skills SECTION directly
            Many resumes have a dedicated "Skills:" section formatted as:
            "Python | React | AWS | Docker | Kubernetes"
            We split on common delimiters (•, |, ;, ,) and take each item.

        Source 2: spaCy NLP on the full text
            Not all skills appear in the skills section — some are mentioned
            in the experience/projects sections.
            spaCy identifies PRODUCT, ORG, and LANGUAGE entities AND
            noun chunks that contain known tech keywords.

        Combining both sources maximizes coverage.

    📌 TEACHING NOTE — Using a set for deduplication:
        skills = set()
        We use a set throughout to automatically deduplicate.
        "Python" might appear in the skills section AND as a spaCy entity.
        The set ensures it's only counted once.
        At the end: sorted(list(skills)) converts to a sorted list.

    📌 TEACHING NOTE — skill_clean = skill.strip(string.punctuation + string.whitespace):
        string.punctuation → '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        string.whitespace  → ' \t\n\r\x0b\x0c'
        .strip() on both removes them from start AND end of the string.

        Example: "  Python.  " → "Python"
        Without this, "Python." and "Python" would be treated as different skills.

    📌 TEACHING NOTE — text[:10000] truncation:
        NLP processing is O(n) in text length. For very long resumes,
        running spaCy on the full text could take several seconds.
        The first 10,000 characters covers the entire skills section
        and most of the experience section for typical resumes.

    Args:
        text: Full resume text
        skills_section: Text of just the skills section (from extract_sections)
        nlp: Loaded spaCy model

    Returns:
        Sorted list of unique skill strings
    """
    skills = set()  # Set automatically deduplicates

    # ── Source 1: Parse the skills section ───────────────────────────────
    if skills_section:
        # Replace common delimiters with commas, then split on commas
        skill_text = (skills_section
            .replace('•', ',')
            .replace('|', ',')
            .replace(';', ',')
        )
        potential_skills = [s.strip() for s in skill_text.split(',')]

        for skill in potential_skills:
            # Reject too-short (single chars) or too-long (sentences) strings
            if skill and len(skill) > 1 and len(skill) < 50:
                skill_clean = skill.strip(string.punctuation + string.whitespace)
                if skill_clean:
                    skills.add(skill_clean)

    # ── Source 2: spaCy NER on full text (truncated for performance) ──────
    doc = nlp(text[:10000])   # Only first 10K chars

    # Named Entity Recognition: PRODUCT, ORG, LANGUAGE often = tech skills
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
            skill_text = ent.text.strip()
            if len(skill_text) > 1 and len(skill_text) < 50:
                # Only add if it contains a known technical keyword (filter noise)
                if any(tech in skill_text.lower() for tech in TECHNICAL_SKILLS_KEYWORDS):
                    skills.add(skill_text)

    # Noun chunks that contain technical keywords
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        if any(tech in chunk_text for tech in TECHNICAL_SKILLS_KEYWORDS):
            skills.add(chunk.text.strip())   # Add original case (not lowercased)

    return sorted(list(skills))   # Sort for consistent, predictable ordering


def extract_projects(text: str, projects_section: str, nlp: spacy.Language) -> List[Dict[str, str]]:
    """
    Parse the projects section into individual project entries.

    📌 TEACHING NOTE — re.split() with alternation (|) and lookahead (?=):
        project_blocks = re.split(
            r'\n\s*\n|(?=\n\s*[•\-\*]\s)|(?=\n\s*\d+\.)',
            projects_section
        )

        This splits on THREE different patterns:
        1. '\n\s*\n'           → blank lines (paragraph break = new project)
        2. '(?=\n\s*[•\-\*]\s)' → before a bullet line (non-consuming)
        3. '(?=\n\s*\d+\.)'   → before a numbered line (non-consuming)

        (?=...) is a LOOKAHEAD — it matches at a position WITHOUT consuming
        the characters. This lets us split BEFORE the bullet/number,
        keeping it in the next block (not losing it in the split).

    📌 TEACHING NOTE — Project block structure assumption:
        We assume each project block follows this structure:
            Line 0: Project title
            Line 1+: Description

        This is a heuristic — most formatted project sections follow this
        convention, but some don't. The [:200] and [:1000] slices cap title
        and description length to prevent pathological inputs.

    📌 TEACHING NOTE — Technology extraction from project blocks:
        For each project, spaCy finds PRODUCT and ORG entities within the
        block text (limited to 1000 chars for performance).
        We filter them using TECHNICAL_SKILLS_KEYWORDS — only keep entities
        that are actual technologies.

        list(set(technologies)) deduplicates (same tech mentioned twice).

    Args:
        text: Full resume text (not used directly here)
        projects_section: Text of just the projects section
        nlp: spaCy model

    Returns:
        List of project dicts: [{title, description, technologies}, ...]
    """
    projects = []
    if not projects_section:
        return projects   # Guard clause: no projects section = empty list

    # Split the projects section into individual project blocks
    project_blocks = re.split(
        r'\n\s*\n|(?=\n\s*[•\-\*]\s)|(?=\n\s*\d+\.)',
        projects_section
    )

    for block in project_blocks:
        block = block.strip()
        # Skip empty or very short blocks (likely whitespace artifacts)
        if not block or len(block) < 20:
            continue

        lines = block.split('\n')

        # First line = project title (cleaned of bullet chars and numbers)
        title = lines[0].strip().strip('•-*0123456789. ')

        # Remaining lines = description
        description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else block

        # Extract technology mentions using spaCy NER
        technologies = []
        doc = nlp(block[:1000])   # Limit to 1000 chars for performance
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'ORG']:
                tech = ent.text.strip()
                if any(keyword in tech.lower() for keyword in TECHNICAL_SKILLS_KEYWORDS):
                    technologies.append(tech)

        projects.append({
            'title':        title[:200],               # Cap title length
            'description':  description[:1000],        # Cap description length
            'technologies': list(set(technologies))    # Deduplicate technologies
        })

    return projects


def extract_keywords(text: str, nlp: spacy.Language, top_n: int = 20) -> List[str]:
    """
    Extract the most important/frequent keywords from the resume text.

    📌 TEACHING NOTE — Three keyword extraction methods combined:
        Method 1: Named entities (PRODUCT, ORG, LANGUAGE, SKILL, GPE, NORP)
            spaCy identifies named things — Python, AWS, Stanford, India.
            Good for: proper nouns, technology names, organizations.

        Method 2: Noun chunks (2-4 word phrases)
            "machine learning", "full stack development", "REST API"
            Good for: multi-word concepts that single tokens miss.

        Method 3: Standalone nouns and proper nouns
            Any significant noun that isn't a stop word.
            Good for: remaining important individual words.

        All three contribute to a flat list, then we count frequency.

    📌 TEACHING NOTE — collections.Counter for frequency counting:
        keyword_counts = Counter(keywords)  → {'python': 5, 'aws': 3, ...}
        keyword_counts.most_common(top_n)   → [('python', 5), ('aws', 3), ...]
        [kw for kw, count in ...most_common(top_n)] → ['python', 'aws', ...]

        Counter is a dict subclass specifically for counting.
        .most_common(n) returns the n most frequent items — no manual sorting needed.

        Why frequency? Keywords that appear many times in a resume are
        likely the most important/relevant ones.

    📌 TEACHING NOTE — not token.is_stop:
        Stop words are common words with little meaning:
        "the", "a", "and", "is", "in", "of", "to", "for", "with"...
        Excluding them focuses the keyword list on meaningful content.
        spaCy has a built-in stop word list: token.is_stop → True/False.

    Args:
        text: Full resume text (truncated to 10K for performance)
        nlp: spaCy model
        top_n: Number of top keywords to return (default 20)

    Returns:
        List of top_n most frequent keywords (lowercase)
    """
    doc = nlp(text[:10000])
    keywords = []

    # Method 1: Named entities
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE', 'SKILL', 'GPE', 'NORP']:
            keywords.append(ent.text.lower())

    # Method 2: Noun chunks (multi-word phrases, 2-4 words only)
    for chunk in doc.noun_chunks:
        if 2 <= len(chunk.text.split()) <= 4:
            keywords.append(chunk.text.lower())

    # Method 3: Individual significant nouns
    for token in doc:
        if token.pos_ in ['PROPN', 'NOUN'] and not token.is_stop:
            if len(token.text) > 2:   # Skip very short tokens ("it", "is")
                keywords.append(token.text.lower())

    # Count frequency and return top N
    keyword_counts = Counter(keywords)
    top_keywords = [kw for kw, count in keyword_counts.most_common(top_n)]
    return top_keywords


def detect_action_verbs(text: str, nlp: spacy.Language) -> List[str]:
    """
    Find strong action verbs at the start of bullet point lines.

    📌 TEACHING NOTE — Why only check the FIRST word of bullet lines?
        ATS systems and career coaches recommend starting bullet points
        with action verbs: "Led a team of 5...", "Built an API that..."
        The POSITION matters — it's specifically the FIRST word of
        a bullet line that signals good resume writing.

        We don't care about action verbs mid-sentence ("I was led by...")
        because those don't indicate the candidate's own contribution.

    📌 TEACHING NOTE — Two-step verb detection:
        Step 1: Dictionary lookup
            if first_word in ACTION_VERBS → instant O(1) match
            Fast for known action verbs.

        Step 2: spaCy POS tagging fallback
            if doc[0].pos_ == 'VERB' → spaCy identifies it as a verb
            Catches verbs not in our ACTION_VERBS set.
            Slower but catches variations we didn't hardcode.

        Dictionary first (fast), spaCy only if dict misses (slower but broader).

    📌 TEACHING NOTE — Stripping bullet characters:
        re.sub('^\\s*[•\\-\\*\\◦]\\s+', '', line)
        Removes the bullet character (•, -, *, ◦) and surrounding whitespace
        from the start of the line, so we can check what comes AFTER the bullet.
        "• Led a team" → "Led a team" → first word = "led"

    📌 TEACHING NOTE — Using a set for detected_verbs:
        Like ACTION_VERBS, detected_verbs is a set to deduplicate.
        If "led" appears in 5 bullet points, it should only be counted once.
        We return sorted(list(detected_verbs)) — a sorted unique list.

    Args:
        text: Full resume text
        nlp: spaCy model (used for POS tagging fallback)

    Returns:
        Sorted list of unique action verbs detected in the resume
    """
    detected_verbs = set()
    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        # Remove bullet character if present
        if re.match(r'^\s*[•\-\*\◦]\s+', line):
            line = re.sub(r'^\s*[•\-\*\◦]\s+', '', line)

        words = line.split()
        if not words:
            continue

        # Check the FIRST word only — action verbs should start the bullet
        first_word = words[0].lower().strip(string.punctuation)

        # Step 1: Fast dictionary lookup
        if first_word in ACTION_VERBS:
            detected_verbs.add(first_word)
        else:
            # Step 2: spaCy POS tagging fallback (only if dict lookup missed)
            doc = nlp(first_word)
            if doc and doc[0].pos_ == 'VERB':
                detected_verbs.add(first_word)

    return sorted(list(detected_verbs))


def extract_jd_keywords(jd_text: str, nlp: spacy.Language, top_n: int = 30) -> List[str]:
    """
    Extract keywords from a job description.

    📌 TEACHING NOTE — Code reuse (DRY principle):
        This function is just a thin wrapper around extract_keywords().
        It uses the SAME extraction logic, just with top_n=30 instead of 20
        (we want more keywords from JDs since they're used for gap analysis).

        This is good DRY practice: don't duplicate the extraction logic.
        Instead, parameterize the existing function and call it.

        An even simpler approach would be:
            extract_jd_keywords = lambda jd_text, nlp, top_n=30: extract_keywords(jd_text, nlp, top_n)
        But the function form is more readable and allows adding docstrings.

    Args:
        jd_text: Full job description text
        nlp: spaCy model
        top_n: Number of keywords to return (default 30 — more than resume keywords)

    Returns:
        List of top keywords from the job description
    """
    return extract_keywords(jd_text, nlp, top_n)