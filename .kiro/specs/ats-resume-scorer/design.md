# Design Document

## Overview

The ATS Resume Scorer is a Streamlit-based web application that provides comprehensive resume analysis using locally-running AI models. The system architecture follows a modular design with clear separation between presentation (Streamlit UI), business logic (analysis engines), and data processing (NLP pipeline). All AI operations run locally using spaCy, Sentence-Transformers, and LanguageTool, ensuring user privacy and eliminating external API dependencies.

The application supports two analysis modes: General ATS scoring (resume only) and Job Description comparison (resume + JD). The scoring algorithm evaluates five key dimensions: formatting (20%), keywords & skills (25%), content quality (25%), skill validation (15%), and ATS compatibility (15%).

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Home.py     │  │ ATS Scorer   │  │   History    │      │
│  │ (Landing)    │  │    Page      │  │    Page      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Authentication Layer                       │
│              (streamlit-authenticator / OAuth)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Scoring    │  │     Skill    │  │   Grammar    │      │
│  │   Engine     │  │  Validator   │  │   Checker    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Location   │  │   Keyword    │  │    Report    │      │
│  │   Detector   │  │   Analyzer   │  │  Generator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    NLP Processing Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    spaCy     │  │  Sentence-   │  │  Language-   │      │
│  │   (NER,      │  │ Transformers │  │    Tool      │      │
│  │  Keywords)   │  │ (Embeddings) │  │  (Grammar)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   File Processing Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  pdfplumber  │  │ python-docx  │  │     NLTK     │      │
│  │ (PDF Parse)  │  │ (DOC Parse)  │  │(Preprocessing)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User uploads resume** → File Processing Layer validates and extracts text
2. **Text extraction** → NLP Processing Layer analyzes structure and content
3. **NLP results** → Business Logic Layer performs specialized analysis
4. **Analysis results** → Scoring Engine calculates final scores
5. **Scores and feedback** → Streamlit Frontend renders results dashboard

### Technology Stack

- **Frontend**: Streamlit 1.28.0+
- **Authentication**: streamlit-authenticator or streamlit-oauth
- **PDF Parsing**: pdfplumber (primary), PyPDF2 (fallback)
- **DOC Parsing**: python-docx
- **NLP**: spaCy (en_core_web_sm or en_core_web_md)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Grammar**: language-tool-python with LanguageTool
- **ML**: scikit-learn for similarity calculations
- **Text Processing**: NLTK for preprocessing

## Components and Interfaces

### 1. File Parser Module (`utils/file_parser.py`)

**Responsibility**: Extract text from uploaded files and validate file integrity.

**Key Functions**:
```python
def validate_file(file: UploadedFile) -> tuple[bool, str]:
    """
    Validates file type, size, and basic integrity.
    Returns: (is_valid, error_message)
    """

def extract_text(file: UploadedFile, file_type: str) -> str:
    """
    Extracts text from PDF, DOC, or DOCX files.
    Uses pdfplumber for PDFs with PyPDF2 fallback.
    Returns: extracted text string
    """

def extract_text_from_pdf(file: UploadedFile) -> str:
    """PDF-specific extraction with error handling"""

def extract_text_from_docx(file: UploadedFile) -> str:
    """DOCX-specific extraction"""
```

**Interface Contract**:
- Input: Streamlit UploadedFile object
- Output: Plain text string or error message
- Exceptions: Raises custom `FileParsingError` on failure

### 2. Text Processor Module (`utils/text_processor.py`)

**Responsibility**: Extract structured information from resume text using NLP.

**Key Functions**:
```python
def extract_sections(text: str, nlp: spacy.Language) -> dict[str, str]:
    """
    Identifies and extracts resume sections.
    Returns: {"summary": "...", "experience": "...", "education": "...", 
              "skills": "...", "projects": "..."}
    """

def extract_contact_info(text: str, nlp: spacy.Language) -> dict:
    """
    Extracts email, phone, LinkedIn, GitHub, portfolio.
    Returns: {"email": "...", "phone": "...", "linkedin": "...", ...}
    """

def extract_skills(text: str, skills_section: str, nlp: spacy.Language) -> list[str]:
    """
    Extracts technical and soft skills from skills section.
    Uses custom skill database and NER.
    """

def extract_projects(text: str, projects_section: str, nlp: spacy.Language) -> list[dict]:
    """
    Extracts project descriptions with titles and details.
    Returns: [{"title": "...", "description": "...", "technologies": [...]}, ...]
    """

def extract_keywords(text: str, nlp: spacy.Language, top_n: int = 20) -> list[str]:
    """
    Extracts key terms using spaCy NER and frequency analysis.
    """

def detect_action_verbs(text: str, nlp: spacy.Language) -> list[str]:
    """
    Identifies action verbs at the start of bullet points.
    """
```

### 3. Skill Validator Module (`utils/skill_validator.py`)

**Responsibility**: Validate that claimed skills are demonstrated in projects/experience.

**Key Functions**:
```python
def validate_skills_with_projects(
    skills: list[str],
    projects: list[dict],
    experience: str,
    embedder: SentenceTransformer
) -> dict:
    """
    Validates each skill against projects and experience.
    Returns: {
        "validated_skills": [{"skill": "...", "projects": [...]}],
        "unvalidated_skills": ["..."],
        "validation_score": 0.0-1.0
    }
    """

def calculate_semantic_similarity(
    skill: str,
    text: str,
    embedder: SentenceTransformer
) -> float:
    """
    Calculates cosine similarity between skill and text embeddings.
    Threshold: 0.6 for validation
    """

def generate_validation_feedback(validation_results: dict) -> list[str]:
    """
    Generates user-friendly feedback messages for validated/unvalidated skills.
    """
```

### 4. Location Detector Module (`utils/location_detector.py`)

**Responsibility**: Detect sensitive location information for privacy recommendations.

**Key Functions**:
```python
def detect_location_info(text: str, nlp: spacy.Language) -> dict:
    """
    Detects addresses, cities, states, zip codes.
    Returns: {
        "location_found": bool,
        "locations": [{"text": "...", "type": "...", "section": "..."}],
        "privacy_risk": "high" | "medium" | "low"
    }
    """

def is_acceptable_location(location: str, section: str) -> bool:
    """
    Determines if location mention is acceptable (e.g., city/state in header).
    """

def generate_privacy_recommendations(locations: list[dict]) -> list[str]:
    """
    Generates specific recommendations for location privacy.
    """
```

### 5. Grammar Checker Module (`utils/grammar_checker.py`)

**Responsibility**: Detect grammar, spelling, and language quality issues.

**Key Functions**:
```python
def check_grammar_and_spelling(text: str, language_tool: LanguageTool) -> dict:
    """
    Performs comprehensive grammar and spelling check.
    Returns: {
        "total_errors": int,
        "critical_errors": [...],
        "moderate_errors": [...],
        "minor_errors": [...],
        "grammar_score": float
    }
    """

def categorize_error(error: Match) -> str:
    """
    Categorizes error as "critical", "moderate", or "minor".
    """

def calculate_grammar_penalty(errors: dict) -> float:
    """
    Calculates score penalty: 5 per critical, 2 per moderate, 0.5 per minor.
    Max penalty: 20 points
    """
```

### 6. Scoring Engine Module (`utils/scorer.py`)

**Responsibility**: Calculate overall ATS score and component scores.

**Key Functions**:
```python
def calculate_overall_score(
    text: str,
    sections: dict,
    skills_validation: dict,
    grammar_results: dict,
    location_results: dict,
    keywords: list[str],
    jd_text: str = None
) -> dict:
    """
    Calculates all component scores and overall score.
    Returns: {
        "overall_score": 0-100,
        "formatting_score": 0-20,
        "keywords_score": 0-25,
        "content_score": 0-25,
        "skill_validation_score": 0-15,
        "ats_compatibility_score": 0-15,
        "penalties": {...},
        "bonuses": {...}
    }
    """

def calculate_formatting_score(sections: dict, text: str) -> float:
    """
    Evaluates section presence, bullet points, structure.
    Max: 20 points
    """

def calculate_keywords_score(
    resume_keywords: list[str],
    jd_keywords: list[str],
    skills: list[str]
) -> float:
    """
    Evaluates keyword presence and matching.
    Max: 25 points
    """

def calculate_content_score(
    text: str,
    action_verbs: list[str],
    grammar_results: dict
) -> float:
    """
    Evaluates action verbs, achievements, grammar quality.
    Max: 25 points
    """

def calculate_skill_validation_score(validation_results: dict) -> float:
    """
    Score = (validated_skills / total_skills) * 15
    """

def calculate_ats_compatibility_score(
    text: str,
    location_results: dict,
    file_info: dict
) -> float:
    """
    Evaluates ATS-friendly formatting, no location issues.
    Max: 15 points
    """
```

### 7. Report Generator Module (`utils/report_generator.py`)

**Responsibility**: Generate PDF reports and action item checklists.

**Key Functions**:
```python
def generate_pdf_report(analysis_results: dict, user_info: dict) -> bytes:
    """
    Creates comprehensive PDF report with all scores and recommendations.
    """

def generate_action_items(analysis_results: dict) -> list[dict]:
    """
    Creates prioritized action items list.
    Returns: [{"priority": "critical", "item": "...", "impact": "..."}, ...]
    """
```

## Data Models

### ResumeAnalysis

```python
@dataclass
class ResumeAnalysis:
    """Complete analysis results for a resume"""
    
    # Metadata
    timestamp: datetime
    user_id: str
    filename: str
    
    # Extracted content
    text: str
    sections: dict[str, str]  # section_name -> content
    contact_info: dict
    skills: list[str]
    projects: list[dict]
    keywords: list[str]
    action_verbs: list[str]
    
    # Analysis results
    skill_validation: SkillValidation
    grammar_results: GrammarResults
    location_results: LocationResults
    keyword_analysis: KeywordAnalysis  # if JD provided
    
    # Scores
    overall_score: float  # 0-100
    formatting_score: float  # 0-20
    keywords_score: float  # 0-25
    content_score: float  # 0-25
    skill_validation_score: float  # 0-15
    ats_compatibility_score: float  # 0-15
    
    # Feedback
    strengths: list[str]
    critical_issues: list[str]
    improvements: list[str]
    recommendations: list[dict]
    action_items: list[dict]
```

### SkillValidation

```python
@dataclass
class SkillValidation:
    """Results of skill-project validation"""
    
    validated_skills: list[dict]  # [{"skill": "...", "projects": [...], "similarity": 0.0-1.0}]
    unvalidated_skills: list[str]
    validation_percentage: float  # 0.0-1.0
    skill_project_mapping: dict[str, list[str]]  # skill -> project names
    feedback_messages: list[str]
```

### GrammarResults

```python
@dataclass
class GrammarResults:
    """Grammar and spelling check results"""
    
    total_errors: int
    critical_errors: list[dict]  # [{"message": "...", "suggestion": "...", "context": "...", "line": int}]
    moderate_errors: list[dict]
    minor_errors: list[dict]
    grammar_score: float  # After penalties
    penalty_applied: float
```

### LocationResults

```python
@dataclass
class LocationResults:
    """Location privacy detection results"""
    
    location_found: bool
    detected_locations: list[dict]  # [{"text": "...", "type": "address|city|zip", "section": "..."}]
    privacy_risk: str  # "high" | "medium" | "low" | "none"
    recommendations: list[str]
    penalty_applied: float
```

### KeywordAnalysis

```python
@dataclass
class KeywordAnalysis:
    """Job description comparison results (optional)"""
    
    jd_keywords: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    match_percentage: float
    semantic_similarity: float  # 0.0-1.0
    skills_gap: list[str]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Authentication and Session Management

**Property 1: Unauthenticated access protection**
*For any* protected page URL, when accessed without valid authentication, the system should redirect to the login page.
**Validates: Requirements 2.1**

**Property 2: Valid credential acceptance**
*For any* valid user credentials, authentication should create a session and grant access to protected pages.
**Validates: Requirements 2.2**

**Property 3: Session information display**
*For any* active user session, the sidebar should display the user's information.
**Validates: Requirements 2.3**

**Property 4: Logout session termination**
*For any* authenticated user, clicking logout should terminate the session and redirect to the landing page.
**Validates: Requirements 2.4**

**Property 5: Expired session re-authentication**
*For any* expired session, accessing protected pages should require re-authentication.
**Validates: Requirements 2.5**

### File Upload and Validation

**Property 6: File type validation**
*For any* uploaded file, the system should accept only PDF, DOC, or DOCX file types and reject all others.
**Validates: Requirements 3.1**

**Property 7: File size limit enforcement**
*For any* uploaded file exceeding 5MB, the system should reject the file and display an error message.
**Validates: Requirements 3.2**

**Property 8: Text extraction from valid files**
*For any* valid PDF, DOC, or DOCX file, the system should successfully extract text content.
**Validates: Requirements 3.3, 3.4**

**Property 9: Extraction failure error handling**
*For any* file where extraction fails, the system should display a specific error message with corrective action suggestions.
**Validates: Requirements 3.5**

### Progress Indication

**Property 10: Progress initialization**
*For any* file processing operation, the progress indicator should start at 0% when processing begins.
**Validates: Requirements 4.1**

**Property 11: Progress monotonicity**
*For any* processing operation, the progress indicator should increase monotonically through all stages, never decreasing.
**Validates: Requirements 4.2**

**Property 12: Progress completion**
*For any* successfully completed processing operation, the progress indicator should reach 100%.
**Validates: Requirements 4.3**

**Property 13: Stage identification**
*For any* active processing stage, the system should display both the stage name and an associated emoji.
**Validates: Requirements 4.4**

### Resume Section Extraction

**Property 14: Comprehensive section extraction**
*For any* resume text, the system should attempt to identify and extract all standard sections (summary, experience, education, skills, projects) and contact information.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**

### Skill Validation

**Property 15: Exact skill matching**
*For any* skill and project description pair, if the skill text appears exactly in the project description, the system should recognize it as a match.
**Validates: Requirements 6.1**

**Property 16: Semantic similarity calculation**
*For any* skill and project description pair, the system should calculate a semantic similarity score between 0 and 1.
**Validates: Requirements 6.2**

**Property 17: Similarity threshold validation**
*For any* skill-project pair with semantic similarity exceeding 0.6, the system should mark the skill as validated.
**Validates: Requirements 6.3**

**Property 18: Unmatched skill detection**
*For any* skill that appears in no project or experience descriptions (with similarity below threshold), the system should mark it as unvalidated.
**Validates: Requirements 6.4**

**Property 19: Skill-project mapping completeness**
*For any* set of skills and projects, the system should generate a complete mapping showing which projects demonstrate each skill.
**Validates: Requirements 6.5**

**Property 20: Skill validation score formula**
*For any* skill validation results, the score should equal (validated_skills / total_skills) × 15, bounded between 0 and 15.
**Validates: Requirements 6.6**

### Grammar and Spelling

**Property 21: Comprehensive error detection**
*For any* resume text, the system should detect all spelling errors, grammar mistakes, punctuation errors, and tense inconsistencies.
**Validates: Requirements 7.1, 7.2, 7.3**

**Property 22: Error categorization completeness**
*For any* detected error, the system should assign it to exactly one category: critical, moderate, or minor.
**Validates: Requirements 7.4**

**Property 23: Error correction suggestions**
*For any* detected error, the system should provide at least one correction suggestion.
**Validates: Requirements 7.5**

**Property 24: Grammar penalty calculation**
*For any* set of grammar errors, the penalty should equal (5 × critical_errors + 2 × moderate_errors + 0.5 × minor_errors), capped at a maximum of 20 points.
**Validates: Requirements 7.6**

### Location Privacy Detection

**Property 25: Address detection**
*For any* resume text containing street addresses, city-state combinations, or zip codes, the system should detect them using NER and regex patterns.
**Validates: Requirements 8.1, 8.2, 8.3**

**Property 26: Contact header exemption**
*For any* city and state appearing in the contact section header only, the system should exempt it from privacy warnings.
**Validates: Requirements 8.4**

**Property 27: Location recommendation generation**
*For any* detected full address or detailed location information, the system should generate recommendations to remove or simplify it.
**Validates: Requirements 8.5**

**Property 28: Location privacy penalty**
*For any* resume with detected full address, the ATS compatibility score should include a penalty between 3 and 5 points.
**Validates: Requirements 8.6**

### Scoring System

**Property 29: Component score bounds**
*For any* resume analysis, each component score should be within its defined range: formatting (0-20), keywords (0-25), content (0-25), skill validation (0-15), ATS compatibility (0-15).
**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

**Property 30: Overall score aggregation**
*For any* resume analysis, the overall score should equal the sum of all component scores (after penalties and bonuses) and be bounded between 0 and 100.
**Validates: Requirements 9.6, 9.7**

### Job Description Comparison

**Property 31: Bidirectional keyword extraction**
*For any* resume and job description pair, the system should extract keywords from both documents.
**Validates: Requirements 10.1**

**Property 32: Semantic similarity bounds**
*For any* resume and job description pair, the calculated semantic similarity should be between 0 and 1.
**Validates: Requirements 10.2**

**Property 33: Keyword intersection identification**
*For any* resume and job description pair, the system should correctly identify keywords present in both documents.
**Validates: Requirements 10.3**

**Property 34: Missing keyword identification**
*For any* resume and job description pair, the system should correctly identify keywords present in the JD but missing from the resume.
**Validates: Requirements 10.4**

**Property 35: Match percentage bounds**
*For any* resume and job description pair, the calculated match percentage should be between 0 and 100.
**Validates: Requirements 10.5**

### Results Display

**Property 36: Score color coding**
*For any* overall score, the display color should be red for scores < 60, yellow for scores 60-79, and green for scores ≥ 80.
**Validates: Requirements 11.1**

**Property 37: Component score display completeness**
*For any* analysis results, all five component scores should be displayed with both progress bars and numerical values.
**Validates: Requirements 11.2**

**Property 38: Skill validation display**
*For any* analysis with validated skills, the display should show each validated skill with its associated project names.
**Validates: Requirements 11.3**

**Property 39: Unvalidated skill warnings**
*For any* analysis with unvalidated skills, the display should show warning indicators for each unvalidated skill.
**Validates: Requirements 11.4**

**Property 40: Grammar error display**
*For any* analysis with grammar errors, all errors should be displayed categorized by severity with correction suggestions.
**Validates: Requirements 11.5**

**Property 41: Privacy alert display**
*For any* analysis with detected location information, the system should display a privacy alert with the detected locations and removal recommendations.
**Validates: Requirements 11.6**

**Property 42: JD comparison display**
*For any* analysis with a job description, the system should display matched keywords, missing keywords, and skills gap analysis.
**Validates: Requirements 11.7**

**Property 43: Action item prioritization display**
*For any* analysis, the system should display action items categorized as critical, high, or medium priority.
**Validates: Requirements 11.8**

### Recommendations

**Property 44: Issue-specific recommendation generation**
*For any* detected issue (unvalidated skills, grammar errors, location privacy, missing keywords, or formatting problems), the system should generate specific recommendations to address that issue.
**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

**Property 45: Recommendation prioritization**
*For any* set of recommendations, they should be ordered by their impact on the overall score, with highest impact first.
**Validates: Requirements 12.6**

### Report Generation

**Property 46: PDF report completeness**
*For any* analysis results, the generated PDF report should contain the overall score, all component breakdowns, and all recommendations.
**Validates: Requirements 13.1, 13.2**

**Property 47: PDF visualization inclusion**
*For any* generated PDF report, it should include visualizations of score distributions and keyword analysis (if JD provided).
**Validates: Requirements 13.3**

**Property 48: Action items checklist generation**
*For any* analysis results, the system should generate a checklist document with recommendations prioritized by impact.
**Validates: Requirements 13.4**

### Local Model Usage

**Property 49: Local model initialization**
*For any* application startup, all AI models (spaCy, Sentence-Transformers, LanguageTool) should be loaded from local storage without external downloads.
**Validates: Requirements 14.1, 14.2, 14.3**

**Property 50: Model caching**
*For any* sequence of multiple analyses, models should be loaded once and reused for all subsequent analyses without reloading.
**Validates: Requirements 14.4**

**Property 51: No external API calls**
*For any* resume processing operation, all NLP operations should complete using only locally loaded models without making external API calls.
**Validates: Requirements 14.5**

### Error Handling

**Property 52: Validation error clarity**
*For any* file upload validation failure, the error message should explain the specific validation failure and list supported formats.
**Validates: Requirements 15.1**

**Property 53: Extraction fallback attempts**
*For any* text extraction failure, the system should attempt at least one alternative extraction method before displaying an error.
**Validates: Requirements 15.2**

**Property 54: Graceful component degradation**
*For any* processing component failure, the system should continue with remaining components and include a note about the failure in results.
**Validates: Requirements 15.3**

**Property 55: User-friendly error messages**
*For any* unexpected error, the displayed message should be user-friendly and not contain technical stack traces.
**Validates: Requirements 15.4**

**Property 56: Model load error guidance**
*For any* model loading failure, the error message should include specific troubleshooting steps.
**Validates: Requirements 15.5**

### Performance

**Property 57: Result caching**
*For any* identical resume processed twice, the second analysis should reuse cached results and complete faster than the first.
**Validates: Requirements 16.1, 16.2**

**Property 58: Processing time bound**
*For any* resume file under 5MB, the complete analysis should finish within 30 seconds.
**Validates: Requirements 16.3**

**Property 59: Progress feedback during processing**
*For any* text processing operation, the system should update progress indicators to provide user feedback.
**Validates: Requirements 16.5**



## Error Handling

### Error Categories

1. **File Upload Errors**
   - Invalid file type: Display supported formats (PDF, DOC, DOCX)
   - File too large: Show size limit (5MB) and actual file size
   - Corrupted file: Suggest re-uploading or converting to different format
   - Empty file: Prompt user to check file content

2. **Parsing Errors**
   - PDF parsing failure: Attempt PyPDF2 fallback, then inform user
   - Text extraction failure: Suggest OCR or manual text input
   - Encoding issues: Try multiple encodings (UTF-8, Latin-1, CP1252)
   - Malformed document: Provide specific error details

3. **Processing Errors**
   - Model loading failure: Display helpful error with restart suggestion
   - Grammar checker timeout: Skip grammar check, continue with other analysis
   - Out of memory: Suggest smaller file or contact support
   - NLP processing failure: Continue with available results, note failure

4. **Authentication Errors**
   - Invalid credentials: Clear message with retry option
   - Session expired: Redirect to login with explanation
   - OAuth failure: Provide alternative authentication method

### Error Handling Strategy

- **Never expose stack traces** to end users
- **Always provide actionable error messages** with next steps
- **Log all errors** for debugging (with user consent)
- **Implement graceful degradation**: Continue analysis even if one component fails
- **Provide retry mechanisms** where appropriate
- **Show progress** even when errors occur to maintain user confidence

### Fallback Mechanisms

1. **PDF Parsing**: pdfplumber → PyPDF2 → Error message
2. **Grammar Checking**: LanguageTool → Skip if timeout → Continue analysis
3. **Section Detection**: spaCy NER → Regex patterns → Manual keywords
4. **Model Loading**: Local cache → Re-download → Error message

## Testing Strategy

### Unit Testing

Unit tests verify specific examples, edge cases, and error conditions for individual components.

**Test Coverage Areas**:

1. **File Parsing**
   - Test PDF extraction with various PDF versions
   - Test DOCX extraction with different formatting
   - Test file validation with invalid types
   - Test size limit enforcement at boundary (exactly 5MB, 5MB + 1 byte)
   - Test corrupted file handling

2. **Text Processing**
   - Test section detection with various resume formats
   - Test contact info extraction with different formats (phone, email, URLs)
   - Test skill extraction with technical and soft skills
   - Test keyword extraction accuracy

3. **Skill Validation**
   - Test exact matching with skills appearing in projects
   - Test semantic similarity calculation with known similar/dissimilar pairs
   - Test threshold boundary (similarity = 0.59, 0.6, 0.61)
   - Test unvalidated skill detection

4. **Grammar Checking**
   - Test error detection with known spelling errors
   - Test error categorization (critical vs moderate vs minor)
   - Test penalty calculation with various error counts
   - Test maximum penalty cap (20 points)

5. **Location Detection**
   - Test address detection with various formats
   - Test zip code detection (5-digit, 9-digit)
   - Test exemption logic for contact header
   - Test penalty application

6. **Scoring**
   - Test each component score calculation
   - Test overall score aggregation
   - Test penalty and bonus application
   - Test score bounds (0-100)

7. **Authentication**
   - Test login with valid/invalid credentials
   - Test session creation and persistence
   - Test logout functionality
   - Test session expiration

**Unit Test Framework**: pytest with pytest-cov for coverage reporting

**Test Organization**: Co-locate tests with source files using `test_*.py` naming convention

### Property-Based Testing

Property-based tests verify universal properties that should hold across all inputs using randomized test data generation.

**PBT Framework**: Hypothesis (Python property-based testing library)

**Configuration**: Each property test should run a minimum of 100 iterations to ensure thorough coverage of the input space.

**Property Test Coverage**:

Each correctness property from the design document should be implemented as a property-based test. Tests should be tagged with comments explicitly referencing the property they implement using this format:

```python
# Feature: ats-resume-scorer, Property 6: File type validation
@given(st.binary(), st.text())
def test_file_type_validation(file_content, file_extension):
    """Property: For any uploaded file, only PDF, DOC, DOCX should be accepted"""
    # Test implementation
```

**Key Property Tests**:

1. **File Validation Properties** (Properties 6-9)
   - Generate random file types and verify only PDF/DOC/DOCX accepted
   - Generate files of various sizes and verify 5MB limit
   - Generate valid files and verify text extraction succeeds

2. **Progress Properties** (Properties 10-13)
   - Generate random files and verify progress starts at 0%
   - Verify progress increases monotonically
   - Verify progress reaches 100% on completion

3. **Section Extraction Properties** (Property 14)
   - Generate resumes with various section formats
   - Verify all standard sections are attempted for extraction

4. **Skill Validation Properties** (Properties 15-20)
   - Generate random skills and projects
   - Verify exact matching works correctly
   - Verify semantic similarity is between 0 and 1
   - Verify threshold (0.6) is applied correctly
   - Verify score formula: (validated / total) × 15

5. **Grammar Properties** (Properties 21-24)
   - Generate text with known errors
   - Verify all errors are detected
   - Verify each error gets a category
   - Verify penalty formula and 20-point cap

6. **Location Properties** (Properties 25-28)
   - Generate text with various address formats
   - Verify detection of addresses, cities, zip codes
   - Verify contact header exemption
   - Verify penalty is between 3-5 points

7. **Scoring Properties** (Properties 29-30)
   - Generate random analysis results
   - Verify each component score is within bounds
   - Verify overall score = sum of components
   - Verify overall score is between 0-100

8. **JD Comparison Properties** (Properties 31-35)
   - Generate random resume-JD pairs
   - Verify keywords extracted from both
   - Verify similarity is between 0-1
   - Verify match percentage is between 0-100

9. **Display Properties** (Properties 36-43)
   - Generate various scores and verify color coding
   - Verify all components are displayed
   - Verify warnings for unvalidated skills

10. **Recommendation Properties** (Properties 44-45)
    - Generate various issues
    - Verify recommendations are generated for each
    - Verify recommendations are prioritized

11. **Report Properties** (Properties 46-48)
    - Generate random analysis results
    - Verify PDF contains all required elements
    - Verify checklist is generated

12. **Model Properties** (Properties 49-51)
    - Verify models load from local storage
    - Verify models are cached and reused
    - Monitor network and verify no external API calls

13. **Error Handling Properties** (Properties 52-56)
    - Generate various error conditions
    - Verify error messages are user-friendly
    - Verify no stack traces in user messages

14. **Performance Properties** (Properties 57-59)
    - Process same resume twice, verify caching
    - Process files under 5MB, verify < 30 second completion
    - Verify progress updates occur

**Smart Generators**:

Create intelligent test data generators that produce realistic inputs:

```python
# Resume text generator
@st.composite
def resume_text(draw):
    """Generates realistic resume text with sections"""
    sections = {
        "summary": draw(st.text(min_size=50, max_size=200)),
        "experience": draw(st.lists(st.text(min_size=100), min_size=1, max_size=5)),
        "education": draw(st.text(min_size=50, max_size=150)),
        "skills": draw(st.lists(st.text(min_size=3, max_size=20), min_size=5, max_size=30)),
        "projects": draw(st.lists(st.text(min_size=100), min_size=0, max_size=5))
    }
    return format_resume(sections)

# Skill-project pair generator
@st.composite
def skill_with_project(draw, should_match=True):
    """Generates skill and project where skill appears in project"""
    skill = draw(st.sampled_from(["Python", "JavaScript", "React", "Docker", "AWS"]))
    if should_match:
        project = f"Built application using {skill} and other technologies"
    else:
        project = draw(st.text(min_size=50, max_size=200))
    return skill, project
```

### Integration Testing

Integration tests verify that components work together correctly:

1. **End-to-End Analysis Flow**
   - Upload file → Extract text → Process → Score → Display results
   - Test with 10+ real resume samples

2. **Authentication + Analysis**
   - Login → Upload → Analyze → View results → Logout

3. **JD Comparison Flow**
   - Upload resume → Upload JD → Compare → View keyword analysis

4. **Report Generation**
   - Complete analysis → Generate PDF → Verify PDF content

### Test Data

**Sample Resumes**: Create 20+ test resumes covering:
- Various formats (PDF, DOCX)
- Different experience levels (entry, mid, senior)
- Different industries (tech, finance, healthcare)
- Various quality levels (poor to excellent)
- Edge cases (minimal content, very long, unusual formatting)

**Sample Job Descriptions**: Create 10+ test JDs for different roles

### Testing Tools

- **pytest**: Main testing framework
- **pytest-cov**: Coverage reporting
- **Hypothesis**: Property-based testing
- **pytest-mock**: Mocking for unit tests
- **pytest-timeout**: Timeout handling for long tests
- **Streamlit testing**: Use `st.testing` for UI component tests

### Coverage Goals

- **Unit test coverage**: 80%+ of code
- **Property test coverage**: 100% of correctness properties
- **Integration test coverage**: All major user flows
- **Edge case coverage**: All identified edge cases tested

## Deployment Considerations

### Configuration

**Streamlit Configuration** (`.streamlit/config.toml`):
```toml
[theme]
primaryColor = "#3B82F6"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 5
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

**Secrets Management** (`.streamlit/secrets.toml`):
```toml
[auth]
cookie_name = "ats_scorer_auth"
cookie_key = "random_signature_key"
cookie_expiry_days = 30

[google_oauth]
client_id = "your_client_id"
client_secret = "your_client_secret"
redirect_uri = "your_redirect_uri"
```

### Environment Setup

**Required Environment Variables**:
- `STREAMLIT_SERVER_PORT`: Server port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: localhost)
- `MODEL_CACHE_DIR`: Directory for caching models (default: ./models)

**Model Pre-loading**:
```bash
# Download models before deployment
python -m spacy download en_core_web_sm
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
```

### Performance Optimization

1. **Model Caching**: Use `@st.cache_resource` for model loading
2. **Data Caching**: Use `@st.cache_data` for expensive computations
3. **Session State**: Store analysis results in `st.session_state`
4. **Lazy Loading**: Load components only when needed
5. **File Size Limits**: Enforce 5MB limit to prevent memory issues

### Security Considerations

1. **File Upload Security**
   - Validate file types using magic numbers, not just extensions
   - Scan for malicious content
   - Sanitize file names
   - Limit upload rate to prevent abuse

2. **Authentication Security**
   - Use HTTPS in production
   - Implement CSRF protection
   - Secure session tokens
   - Hash passwords with bcrypt (if using password auth)

3. **Data Privacy**
   - Don't store resume content without explicit consent
   - Clear temporary files after processing
   - Implement data retention policies
   - Comply with GDPR/privacy regulations

4. **Input Validation**
   - Sanitize all user inputs
   - Validate file content before processing
   - Prevent injection attacks

### Monitoring and Logging

1. **Application Logs**
   - Log all errors with context
   - Log authentication events
   - Log file processing metrics
   - Use structured logging (JSON format)

2. **Performance Metrics**
   - Track analysis completion times
   - Monitor model loading times
   - Track memory usage
   - Monitor concurrent users

3. **Error Tracking**
   - Implement error reporting (e.g., Sentry)
   - Track error rates by type
   - Alert on critical errors

### Scalability

1. **Horizontal Scaling**: Deploy multiple instances behind load balancer
2. **Model Sharing**: Share model cache across instances
3. **Session Management**: Use external session store (Redis) for multi-instance
4. **File Storage**: Use object storage (S3) for temporary files in production

## Future Enhancements

1. **Multi-language Support**: Extend to support resumes in Spanish, French, German
2. **Industry-Specific Analysis**: Tailor scoring for different industries
3. **Role-Specific Optimization**: Different criteria for different job roles
4. **Resume Templates**: Provide downloadable ATS-optimized templates
5. **Version Comparison**: Track improvements across multiple resume versions
6. **AI-Powered Insights**: Optional integration with Ollama for deeper analysis
7. **Collaborative Features**: Share results with career coaches or mentors
8. **Mobile App**: Native mobile application for on-the-go analysis
9. **Browser Extension**: Analyze job postings and suggest resume optimizations
10. **API Access**: Provide REST API for integration with other tools
