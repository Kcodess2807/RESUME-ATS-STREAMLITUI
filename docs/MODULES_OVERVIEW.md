# Resume ATS Bootcamp - Modules Overview

## Complete Module Breakdown with Files

---

## Module 00 - Introduction & Project Demo (15 min)

**Type**: Introduction  
**Files**: None (just demo)

**What to Show**:
- Complete working application demo
- Problem statement explanation
- Course overview

---

## Module 01 - System Architecture & Tech Stack (25 min)

**Type**: System Design  
**Files to Reference**:
- `backend/config.py` - Show configuration
- `README.md` - Project overview
- Architecture diagrams (create during video)

**What to Cover**:
- System architecture layers
- Data flow pipeline
- Technology stack decisions
- Project folder structure

---

## Module 02 - Environment Setup & Dependencies (20 min)

**Type**: Setup  
**Files to Cover**:
- `requirements.txt` - All dependencies
- `.env.example` → `.env` - Environment variables
- `backend/config.py` - Model settings

**What to Build**:
- Virtual environment
- Install all packages
- Download spaCy model
- Download fine-tuned BERT model
- Verification script

---

## Module 03 - Document Parser Part 1 (25 min)

**Type**: Backend Development  
**Files to Create**:
- `backend/utils.py` - Utility functions
- `backend/parser.py` (Part 1) - PDF/DOCX/TXT parsing
- `test_parser.py` - CLI test script

**What to Build**:
- PDF parser (PyMuPDF)
- DOCX parser (python-docx)
- TXT reader
- Text cleaning utilities
- File type detection

**Key Functions**:
- `parse_pdf()`
- `parse_docx()`
- `parse_txt()`
- `parse_resume()` - Main function
- `clean_text()`

---

## Module 04 - Document Parser Part 2 (25 min)

**Type**: NLP Development  
**Files to Modify**:
- `backend/parser.py` (Part 2) - Add NER and contact extraction
- `backend/utils.py` - Add regex patterns

**What to Build**:
- Email extraction (regex)
- Phone number extraction (regex)
- LinkedIn/GitHub URL extraction (regex)
- spaCy NER integration
- Name extraction
- Organization extraction
- Location extraction

**Key Functions**:
- `extract_contact_info()`
- `extract_email()`
- `extract_phone()`
- `extract_urls()`
- `extract_entities_with_spacy()`

**Config to Use**:
- `EMAIL_REGEX` from config.py
- `PHONE_REGEX` from config.py
- `LINKEDIN_REGEX` from config.py
- `GITHUB_REGEX` from config.py

---

## Module 05 - Document Parser Part 3 (25 min)

**Type**: Advanced Parsing  
**Files to Modify**:
- `backend/parser.py` (Part 3) - Section detection, skills, experience
- `backend/config.py` - Skills database
- `backend/data/skills_database.json` - Create skills DB

**What to Build**:
- Section detection (Education, Experience, Skills, Projects)
- Skills extraction (match against 200+ skills)
- Experience parsing (dates, titles, descriptions)
- Education parsing (degrees, institutions, dates)
- Complete resume structure

**Key Functions**:
- `detect_sections()`
- `extract_skills()`
- `parse_experience()`
- `parse_education()`
- `structure_resume()` - Final output

**Config to Use**:
- `TECH_SKILLS` from config.py
- `SECTION_PATTERNS` from config.py

---

## Module 06 - Job Description Parser (20 min)

**Type**: Backend Development  
**Files to Create**:
- `backend/jd_parser.py` - Complete JD parser

**What to Build**:
- JD text parsing
- Required skills extraction
- Preferred skills extraction
- Experience requirements
- Education requirements
- Responsibilities extraction

**Key Functions**:
- `parse_job_description()`
- `extract_required_skills()`
- `extract_experience_requirements()`
- `extract_education_requirements()`

---

## Module 07 - AI Matching with BERT (30 min)

**Type**: Machine Learning  
**Files to Create**:
- `backend/matcher.py` - Complete BERT matching engine

**What to Build**:
- Load BERT model (fine-tuned or base)
- Generate resume embeddings
- Generate JD embeddings
- Calculate cosine similarity
- Semantic skill matching
- Experience scoring
- Education scoring
- Overall match calculation

**Key Functions**:
- `_load_model()` - Load BERT
- `create_resume_embedding()`
- `create_jd_embedding()`
- `calculate_overall_similarity()`
- `semantic_skill_matching()`
- `calculate_experience_score()`
- `calculate_education_score()`
- `match_resume_to_job()` - Main function

**Config to Use**:
- `SENTENCE_BERT_MODEL` from config.py
- `FINETUNED_MODEL_PATH` from config.py
- `SKILL_MATCH_THRESHOLD` from config.py
- `DEFAULT_WEIGHTS` from config.py

---

## Module 08 - Quality Analysis & Scoring (25 min)

**Type**: Business Logic  
**Files to Create**:
- `backend/resume_quality_checker.py` - Quality analysis
- `backend/strict_scoring.py` - Scoring algorithms
- `backend/ranker.py` - Ranking logic

**What to Build**:
- Section-wise scoring
- Overall quality score
- Career level detection (Entry/Mid/Senior)
- Domain classification
- Feedback generation
- Improvement suggestions

**Key Functions**:
- `analyze_resume_quality()`
- `score_section()`
- `detect_career_level()`
- `classify_domain()`
- `generate_feedback()`
- `calculate_overall_score()`

**Config to Use**:
- `RATING_THRESHOLDS` from config.py
- `STATUS_THRESHOLDS` from config.py
- `EXPERIENCE_LEVELS` from config.py

---

## Module 09 - Streamlit UI (30 min)

**Type**: Frontend Development  
**Files to Create**:
- `streamlit_app.py` - Main application
- `ui/sidebar.py` - Navigation
- `ui/pages.py` - Page layouts
- `ui/theme.py` - Custom CSS
- `.streamlit/config.toml` - Streamlit config

**What to Build**:
- Main app structure
- Sidebar navigation
- Home page
- Upload & analyze page
- Results display
- File upload handling
- Progress indicators
- Charts and visualizations
- Integration with backend

**Key Components**:
- Session state management
- File uploader
- Text input for JD
- Results display with tabs
- PDF download button
- Custom CSS styling

---

## Module 10 - Database, Reports & Auth (25 min)

**Type**: Full Stack  
**Files to Create**:
- `backend/database.py` - SQLite operations
- `backend/report_generator.py` - PDF reports
- `ui/auth.py` - Google OAuth

**What to Build**:
- SQLite database schema
- CRUD operations
- Resume history storage
- PDF report generation
- Charts in PDF
- Google OAuth integration
- Guest mode
- Profile history page

**Key Functions**:
- `init_database()`
- `save_analysis()`
- `get_user_history()`
- `generate_pdf_report()`
- `authenticate_user()`
- `guest_mode()`

---

## Module 11 - Testing & AWS Deployment (30 min)

**Type**: Production & Deployment  
**Files to Create**:
- `Procfile` - Process file for deployment
- `.ebextensions/python.config` - EB configuration
- Deployment scripts

**What to Cover**:
- Local testing
- Production configuration
- AWS Elastic Beanstalk setup
- Environment variables
- Model hosting (S3 or included)
- Deployment commands
- Monitoring and logs
- Troubleshooting

**Commands to Cover**:
```bash
eb init
eb create
eb deploy
eb setenv
eb logs
eb health
```

---

## File Creation Timeline

### After Module 02:
- Virtual environment
- .env file

### After Module 03:
- backend/utils.py
- backend/parser.py (basic)
- test_parser.py

### After Module 04:
- backend/parser.py (with NER)

### After Module 05:
- backend/parser.py (complete)
- backend/data/skills_database.json

### After Module 06:
- backend/jd_parser.py

### After Module 07:
- backend/matcher.py

### After Module 08:
- backend/resume_quality_checker.py
- backend/strict_scoring.py
- backend/ranker.py

### After Module 09:
- streamlit_app.py
- ui/sidebar.py
- ui/pages.py
- ui/theme.py
- .streamlit/config.toml

### After Module 10:
- backend/database.py
- backend/report_generator.py
- ui/auth.py
- resume_history.db (auto-created)

### After Module 11:
- Procfile
- .ebextensions/python.config
- Deployed application on AWS

---

## Testing Strategy

### Module 03-05: Parser Testing
```bash
python test_parser.py uploads/sample_resume.pdf
```

### Module 06: JD Parser Testing
```bash
python -c "from backend.jd_parser import parse_job_description; print(parse_job_description('...'))"
```

### Module 07: Matcher Testing
```bash
python backend/matcher.py  # Has __main__ test
```

### Module 08: Quality Checker Testing
```bash
python backend/resume_quality_checker.py  # Has __main__ test
```

### Module 09-10: Full App Testing
```bash
streamlit run streamlit_app.py
```

### Module 11: Production Testing
```bash
eb open  # Test on AWS
```

---

## Key Configuration Files

**Always Reference**:
- `backend/config.py` - All constants, settings, skills database
- `requirements.txt` - Dependencies
- `.env` - Environment variables
- `README.md` - Documentation

---

## Code Reuse

**Modules that import from others**:
- Module 04-05: Import from Module 03 (parser.py)
- Module 07: Import from Module 03-06 (parser, jd_parser)
- Module 08: Import from Module 07 (matcher)
- Module 09: Import from all backend modules
- Module 10: Import from all modules

**Progressive Building**:
- Each module builds on previous
- Test after each module
- Incremental functionality
- Working code at each step

---

## Sample Resumes Needed

**For Testing** (provide in uploads/ folder):
- `sample_resume_software_engineer.pdf`
- `sample_resume_data_scientist.pdf`
- `sample_resume_entry_level.pdf`
- `sample_jd_ml_engineer.txt`
- `sample_jd_full_stack.txt`

---

## Total Lines of Code

**Approximate**:
- backend/parser.py: ~500 lines
- backend/jd_parser.py: ~200 lines
- backend/matcher.py: ~400 lines
- backend/resume_quality_checker.py: ~300 lines
- backend/database.py: ~200 lines
- backend/report_generator.py: ~250 lines
- streamlit_app.py: ~300 lines
- ui/*.py: ~400 lines
- **Total: ~2,500 lines of Python**

---

## Recommended Teaching Order

1. ✅ Show the end result (Module 00)
2. ✅ Explain the architecture (Module 01)
3. ✅ Set up environment (Module 02)
4. ✅ Build backend first (Modules 03-08)
5. ✅ Add UI (Module 09)
6. ✅ Add persistence (Module 10)
7. ✅ Deploy (Module 11)

This order ensures students understand the core logic before wrapping it in UI!
