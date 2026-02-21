 # Module 01 - System Architecture & Tech Stack

**Duration**: 25 minutes  
**Type**: System Design

---

## 🎯 Learning Objectives
- Understand the complete system architecture
- Learn why specific technologies were chosen
- Understand data flow through the system
- Grasp the ML pipeline architecture

---

## 📁 Files to Reference

**Primary Files**:
- `backend/config.py` - Configuration and constants
- `README.md` - Project overview
- Architecture diagrams (create during video)

**Quick Peek** (don't code yet, just show structure):
- `streamlit_app.py` - Entry point
- `backend/` folder structure
- `ui/` folder structure

---

## 📋 Video Script Outline

### Part 1: High-Level Architecture (8 minutes)

**Draw/Show Architecture Diagram**:

```
┌─────────────────────────────────────────┐
│         User Interface Layer            │
│            (Streamlit)                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Authentication Layer               │
│    (Google OAuth / Guest Mode)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Application Layer                  │
│       (streamlit_app.py)                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Business Logic Layer               │
│         (backend/)                      │
│  ┌────────────────────────────────┐    │
│  │ Document Processing            │    │
│  │ - parser.py                    │    │
│  │ - jd_parser.py                 │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │ AI/ML Layer                    │    │
│  │ - matcher.py (BERT)            │    │
│  │ - spaCy NER                    │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │ Quality Analysis               │    │
│  │ - resume_quality_checker.py    │    │
│  │ - ranker.py                    │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │ Data Layer                     │    │
│  │ - database.py                  │    │
│  │ - report_generator.py          │    │
│  └────────────────────────────────┘    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Storage Layer                      │
│  - SQLite Database                      │
│  - File System (uploads, models)        │
└─────────────────────────────────────────┘
```

**Explain Each Layer**:
1. **UI Layer**: User interaction, file uploads, results display
2. **Auth Layer**: Security, user sessions
3. **Application Layer**: Orchestrates everything
4. **Business Logic**: Core functionality
5. **Storage**: Persistence

### Part 2: Data Flow Pipeline (7 minutes)

**Show Data Flow Diagram**:

```
Resume Upload (PDF/DOCX)
    ↓
File Validation
    ↓
Text Extraction (PyMuPDF/python-docx)
    ↓
Text Preprocessing
    ↓
Named Entity Recognition (spaCy)
    ├─→ Contact Info (email, phone, LinkedIn)
    ├─→ Names, Organizations
    └─→ Dates, Locations
    ↓
Section Detection
    ├─→ Education
    ├─→ Experience
    ├─→ Skills
    └─→ Projects
    ↓
Skills Extraction (200+ tech skills database)
    ↓
Experience Parsing (dates, titles, descriptions)
    ↓
Education Parsing (degrees, institutions)
    ↓
Structured Resume Data
    ↓
┌─────────────────────────────────────┐
│  If Job Description Provided:       │
│                                     │
│  JD Text → Parse Requirements       │
│         → Extract Skills            │
│         → Identify Experience Level │
│                                     │
│  Resume + JD → BERT Embeddings      │
│             → Cosine Similarity     │
│             → Match Score           │
└─────────────────────────────────────┘
    ↓
Quality Analysis
    ├─→ Section Scores
    ├─→ Career Level Detection
    ├─→ Domain Classification
    └─→ Improvement Suggestions
    ↓
Results Display + PDF Report
    ↓
Save to Database (history)
```

**Walk Through Example**:
- User uploads "john_doe_resume.pdf"
- System extracts text: "John Doe, Python Developer..."
- spaCy identifies: Name="John Doe", Skills=["Python", "React"]
- BERT compares with JD: 85% match
- Quality checker: "Good resume, add more projects"
- Save to database, generate report

### Part 3: Technology Stack Decisions (8 minutes)

**Frontend: Streamlit**
- ✅ Why: Rapid prototyping, Python-native, no HTML/CSS/JS needed
- ✅ Perfect for: Data apps, ML demos, internal tools
- ❌ Limitations: Less customization than React/Vue
- **Alternative**: Flask + React (more complex)

**Backend: Python 3.8+**
- ✅ Why: ML ecosystem, easy to learn, great libraries
- ✅ Libraries: sentence-transformers, spaCy, PyMuPDF
- **Alternative**: Node.js (but weaker ML support)

**ML/AI: BERT (sentence-transformers)**
- ✅ Why: Semantic understanding, not just keywords
- ✅ Example: Understands "React" = "ReactJS" = "React.js"
- ✅ Fine-tuned: 85% accuracy vs 70% base model
- **Alternative**: TF-IDF (simpler but less accurate)

**NLP: spaCy**
- ✅ Why: Production-ready, fast, pre-trained models
- ✅ Use: Named Entity Recognition (NER)
- ✅ Extracts: Names, dates, organizations, locations
- **Alternative**: NLTK (slower, more manual)

**Database: SQLite**
- ✅ Why: Lightweight, serverless, no setup needed
- ✅ Perfect for: Single-user apps, prototypes
- ❌ Limitations: Not for high-concurrency
- **Alternative**: PostgreSQL (for production scale)

**Document Processing**:
- **PyMuPDF (fitz)**: Fast PDF parsing
- **python-docx**: Word document parsing
- ✅ Why: Reliable, well-maintained, good performance

**Authentication: Google OAuth 2.0**
- ✅ Why: Secure, users trust Google, no password management
- ✅ Fallback: Guest mode for testing
- **Alternative**: Email/password (more work)

**Reports: ReportLab**
- ✅ Why: Professional PDFs, charts, custom layouts
- **Alternative**: WeasyPrint, FPDF

**Deployment: AWS Elastic Beanstalk**
- ✅ Why: Easy deployment, auto-scaling, managed service
- ✅ Handles: Load balancing, monitoring, updates
- **Alternatives**: Streamlit Cloud (easiest), Heroku, EC2

### Part 4: Scalability Considerations (2 minutes)

**Current Design**:
- Single-user focused
- SQLite database
- Local file storage
- Session-based state

**For Production Scale**:
- Switch to PostgreSQL
- Use S3 for file storage
- Add Redis for caching
- Implement job queues (Celery)
- Load balancer for multiple instances

---

## 📊 Diagrams to Create

**1. System Architecture Diagram** (shown above)

**2. Data Flow Diagram** (shown above)

**3. Component Interaction Diagram**:
```
User → Streamlit UI → streamlit_app.py
                           ↓
                    parser.parse_resume()
                           ↓
                    matcher.match_resume_to_job()
                           ↓
                    quality_checker.analyze()
                           ↓
                    database.save_analysis()
                           ↓
                    report_generator.create_pdf()
                           ↓
                    Display Results
```

**4. ML Pipeline**:
```
Text Input
    ↓
Tokenization (BERT Tokenizer)
    ↓
Embedding Generation (768-dim vectors)
    ↓
Cosine Similarity Calculation
    ↓
Match Score (0-100%)
```

---

## 💻 Code Walkthrough

### Show `backend/config.py` Structure

```python
# Open backend/config.py and explain:

# 1. Model Settings
SENTENCE_BERT_MODEL = 'all-MiniLM-L6-v2'  # Base model
FINETUNED_MODEL_PATH = 'backend/models/finetuned-bert'  # Our trained model
SPACY_MODEL = 'en_core_web_sm'  # NER model

# 2. Scoring Weights
DEFAULT_WEIGHTS = {
    'semantic': 0.30,      # BERT similarity
    'skills': 0.25,        # Skills match
    'experience': 0.35,    # Most important!
    'education': 0.10      # Least important
}

# 3. Skills Database
TECH_SKILLS = [
    "Python", "Java", "JavaScript", "React", "Django",
    # ... 200+ skills
]

# 4. Regex Patterns
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_REGEX = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

# 5. Degree Hierarchy
DEGREE_HIERARCHY = {
    'bachelor': 4,
    'master': 5,
    'phd': 6,
}
```

**Explain**:
- Centralized configuration
- Easy to modify settings
- Single source of truth

### Show Project Structure

```bash
# Show in terminal:
tree -L 2 -I '__pycache__|*.pyc'

# Explain folder structure:
.
├── streamlit_app.py          # Entry point
├── backend/
│   ├── parser.py            # Resume parsing
│   ├── jd_parser.py         # JD parsing
│   ├── matcher.py           # BERT matching
│   ├── resume_quality_checker.py
│   ├── database.py
│   ├── report_generator.py
│   ├── config.py
│   └── models/              # ML models
├── ui/
│   ├── auth.py
│   ├── sidebar.py
│   ├── pages.py
│   └── theme.py
├── requirements.txt
└── README.md
```

---

## 🎤 Key Talking Points

**Why This Architecture?**:
- Separation of concerns (UI, logic, data)
- Easy to test individual components
- Scalable and maintainable
- Clear data flow

**Design Principles**:
- Modularity: Each file has one responsibility
- Reusability: Functions can be used independently
- Testability: Easy to unit test
- Readability: Clear naming, good comments

**Trade-offs**:
- Simplicity vs Features: Chose simplicity
- Speed vs Accuracy: Balanced with fine-tuning
- Cost vs Performance: Free tier friendly

---

## ✅ Module Completion Checklist

Students should understand:
- [ ] Complete system architecture (all layers)
- [ ] Data flow from upload to results
- [ ] Why each technology was chosen
- [ ] Trade-offs and alternatives
- [ ] How components interact
- [ ] Project folder structure
- [ ] Configuration management

---

## 🔗 Next Module

**Module 02**: Environment Setup & Dependencies
- Install Python and dependencies
- Download ML models
- Set up development environment
- Verify installation
