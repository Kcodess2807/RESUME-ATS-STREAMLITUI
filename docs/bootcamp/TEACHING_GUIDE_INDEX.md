# ATS Resume Scorer - Bootcamp Teaching Guide

## Complete Module Index

### ✅ Module 00: Intro & Demo (15 min)
**File**: `MODULE_00_INTRO.md`
**Content**: Live demo walkthrough, problem statement, value proposition
**No Coding**: Just demonstration and explanation

### ✅ Module 01: Architecture & Tech Stack (25 min)
**File**: `MODULE_01_ARCHITECTURE.md`
**Content**: System architecture, technology choices, design decisions
**Diagrams**: Show all 4 Mermaid diagrams from `ARCHITECTURE_DIAGRAMS.md`

### ✅ Module 02: Project and ENV Setup (20 min)
**File**: `MODULE_02_SETUP.md`
**Content**: Project structure, dependencies, environment setup
**Code**: `requirements.txt`, `.env`, `app/app.py` (basic)

### ✅ Module 03: Document Parser (25 min)
**File**: `MODULE_03_PARSER.md`
**Content**: File validation, PDF/DOCX parsing, error handling
**Code**: `app/core/parser.py` (complete)

### 📝 Module 04: NLP & NER (25 min)
**File**: `MODULE_04_NLP.md`
**Content**: spaCy integration, text processing, section extraction
**Code**: `app/core/processor.py`
**Key Concepts**:
- Loading spaCy models
- Tokenization and POS tagging
- Named Entity Recognition
- Section detection (Experience, Education, Skills)
- Keyword extraction

### 📝 Module 05: Skills & Experience (25 min)
**File**: `MODULE_05_SKILLS.md`
**Content**: Skill extraction, experience analysis, action verb detection
**Code**: `app/core/analyzer.py`
**Key Concepts**:
- Skill database matching
- Action verb identification
- Quantification detection
- Experience quality scoring

### 📝 Module 06: JD Parser (20 min)
**File**: `MODULE_06_JD.md`
**Content**: Job description parsing, keyword extraction
**Code**: `app/core/comparator.py` (part 1)
**Key Concepts**:
- JD text processing
- Keyword extraction
- Industry term identification

### 📝 Module 07: BERT Matching - Core ML (30 min)
**File**: `MODULE_07_BERT.md`
**Content**: Sentence Transformers, semantic similarity, skill validation
**Code**: `app/ai/validator.py`
**Key Concepts**:
- Loading BERT models
- Generating embeddings
- Cosine similarity
- Skill-project matching
- Semantic vs keyword matching

### 📝 Module 08: Quality Analysis (25 min)
**File**: `MODULE_08_SCORING.md`
**Content**: Score calculation, component breakdown, feedback generation
**Code**: `app/core/scorer.py`
**Key Concepts**:
- 5-component scoring system
- Weight distribution
- Score aggregation
- Feedback generation

### 📝 Module 09: Streamlit UI (30 min)
**File**: `MODULE_09_UI.md`
**Content**: Building the interface, file upload, results dashboard
**Code**: `app/pages/1_ATS_Scorer.py`, `app/ui/dashboard.py`
**Key Concepts**:
- Streamlit components
- Session state management
- Progress indicators
- Results visualization

### 📝 Module 10: Database & Auth (25 min)
**File**: `MODULE_10_DB_AUTH.md`
**Content**: Supabase integration, Google OAuth, user management
**Code**: `app/config/database.py`, `app/config/auth.py`
**Key Concepts**:
- Supabase setup
- OAuth flow
- Session management
- Data persistence

### 📝 Module 11: Testing & Deployment (20 min)
**File**: `MODULE_11_DEPLOY.md`
**Content**: Testing strategies, AWS deployment, production considerations
**Code**: `tests/`, deployment configs
**Key Concepts**:
- Unit testing
- Integration testing
- AWS Elastic Beanstalk
- Environment variables
- Monitoring

## Teaching Flow

### Before Class
1. Set up demo environment
2. Prepare sample resumes (good and bad examples)
3. Test all code snippets
4. Have architecture diagrams ready
5. Set up Supabase project
6. Configure Google OAuth

### During Class
1. Start with demo (Module 00) - Get them excited
2. Explain architecture (Module 01) - Big picture
3. Set up together (Module 02) - Everyone on same page
4. Build incrementally (Modules 03-08) - Core functionality
5. Add UI (Module 09) - Make it real
6. Add production features (Modules 10-11) - Professional touch

### After Each Module
- **Checkpoint**: Verify everyone's code works
- **Q&A**: Answer questions
- **Break**: 5 min every 2 modules

### Code Repository Structure
```
bootcamp-code/
├── module-03-parser/
│   └── parser.py (completed)
├── module-04-nlp/
│   └── processor.py (completed)
├── module-05-skills/
│   └── analyzer.py (completed)
├── module-06-jd/
│   └── comparator.py (part 1)
├── module-07-bert/
│   └── validator.py (completed)
├── module-08-scoring/
│   └── scorer.py (completed)
├── module-09-ui/
│   ├── 1_ATS_Scorer.py
│   └── dashboard.py
├── module-10-db-auth/
│   ├── database.py
│   └── auth.py
└── final-project/
    └── (complete working app)
```

## Teaching Tips

### For Each Module:
1. **Explain Why** - Before showing code, explain the problem
2. **Show Code** - Live code, don't just paste
3. **Explain How** - Walk through the logic
4. **Test It** - Run it, show it works
5. **Debug Together** - If errors, fix them live

### Common Student Questions:
- "Why not use ChatGPT API?" → Privacy, cost, control
- "Can we use React instead?" → Yes, but Streamlit is faster for data apps
- "How accurate is the scoring?" → Based on ATS research, ~85% correlation
- "Can this handle non-English resumes?" → Would need different spaCy models

### Engagement Strategies:
- Ask students to predict what code will do
- Have them suggest improvements
- Pair programming for complex sections
- Code review sessions

### Time Management:
- Stick to module times
- If running over, skip optional sections
- Have "homework" modules if needed
- Prioritize core functionality over polish

## Assessment Ideas

### During Bootcamp:
- Quick quizzes after each module
- Code challenges
- Pair programming exercises

### Final Project:
- Add a new feature (e.g., cover letter analysis)
- Improve a component (e.g., better skill extraction)
- Deploy to production
- Present to class

## Resources for Students

### Documentation:
- spaCy: https://spacy.io/usage
- Sentence Transformers: https://www.sbert.net/
- Streamlit: https://docs.streamlit.io/
- Supabase: https://supabase.com/docs

### Further Learning:
- NLP Course: fast.ai
- ML Deployment: Full Stack Deep Learning
- System Design: System Design Primer

## Instructor Notes

### Prerequisites Students Should Have:
- Python basics (functions, classes, imports)
- Basic ML concepts (what is a model, training vs inference)
- Command line comfort
- Git basics

### What Students Will Learn:
- Production NLP pipeline
- ML model integration
- Web app development
- Database design
- Authentication patterns
- Deployment strategies

### Career Relevance:
- Resume analysis is a real market
- Skills transfer to other NLP projects
- Full-stack ML experience
- Portfolio project

## Next Steps

After completing all modules, students can:
1. Deploy their own version
2. Add features (cover letter analysis, LinkedIn optimization)
3. Monetize (SaaS model)
4. Open source contribution
5. Use as portfolio piece

---

**Total Time**: ~4.5 hours of instruction + breaks
**Difficulty**: Intermediate
**Outcome**: Working, deployable ML application
