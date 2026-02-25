# Module 02: Project and ENV Setup (20 min)

## Objective
Students set up their development environment and understand the project structure.

## Prerequisites
- Python 3.10+ installed
- Git installed
- Code editor (VS Code recommended)
- Terminal access

## Script

### Part 1: Project Structure (5 min)

"Let's create our project structure. Every file has a purpose."

```bash
# Create project directory
mkdir ats-resume-scorer
cd ats-resume-scorer

# Create directory structure
mkdir -p app/{core,ai,ui,utils,config,pages,views}
mkdir -p data
mkdir -p models
mkdir -p assets
mkdir -p docs
mkdir -p tests
mkdir -p .streamlit
mkdir -p config
```

**Explain each directory:**

```
ats-resume-scorer/
├── app/                    # Main application code
│   ├── core/              # Core business logic
│   │   ├── parser.py      # File parsing (PDF/DOCX)
│   │   ├── processor.py   # Text processing with spaCy
│   │   ├── analyzer.py    # Experience analysis
│   │   ├── scorer.py      # Score calculation
│   │   ├── comparator.py  # JD comparison
│   │   └── generator.py   # PDF report generation
│   ├── ai/                # ML/AI components
│   │   └── validator.py   # Skill validation with BERT
│   ├── ui/                # UI components
│   │   └── dashboard.py   # Results dashboard
│   ├── utils/             # Utilities
│   │   ├── progress.py    # Progress tracking
│   │   └── errors.py      # Error handling
│   ├── config/            # Configuration
│   │   ├── auth.py        # Authentication
│   │   └── database.py    # Database connection
│   ├── pages/             # Streamlit pages
│   │   ├── 1_ATS_Scorer.py
│   │   ├── 2_History.py
│   │   └── 3_Resources.py
│   └── app.py             # Main entry point
├── data/                  # Data files
│   ├── skills_database.json
│   ├── action_verbs.json
│   └── industry_keywords.json
├── models/                # Cached ML models
├── assets/                # Static assets
│   └── styles.css
├── config/                # Config files
│   └── google_oauth.json
├── .streamlit/            # Streamlit config
│   ├── config.toml
│   └── secrets.toml
├── docs/                  # Documentation
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

"Why this structure?
- **Separation of concerns**: Each module has one job
- **Scalability**: Easy to add new features
- **Testability**: Can test each component independently
- **Maintainability**: Clear where to find things"

### Part 2: Virtual Environment (3 min)

```bash
# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

"Why virtual environment?
- Isolates dependencies
- Prevents version conflicts
- Reproducible setup
- Clean uninstall (just delete folder)"

### Part 3: Dependencies (7 min)

**Create requirements.txt:**

```txt
# Core Framework
streamlit>=1.35.0

# NLP & AI
spacy>=3.7.4
sentence-transformers>=2.2.2
torch>=2.1.0
nltk==3.8.1

# File Processing
pdfplumber==0.9.0
python-docx==1.0.1
PyPDF2>=3.0.0

# Database
supabase>=2.0.0
pyarrow>=14.0.0

# Authentication
streamlit-google-auth>=0.1.0
Authlib>=1.3.2

# Utilities
scikit-learn==1.2.0
fpdf2==2.7.0
language-tool-python>=2.7.1
python-magic==0.4.27
```

**Install dependencies:**

```bash
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md
```

"Let's understand key dependencies:

**streamlit**: Our entire UI framework
**spacy**: NLP processing - tokenization, NER, POS tagging
**sentence-transformers**: BERT embeddings for semantic similarity
**torch**: PyTorch backend for transformers
**pdfplumber**: Best PDF text extraction
**python-docx**: Word document parsing
**supabase**: PostgreSQL database client
**fpdf2**: PDF report generation

Why these specific versions?
- Tested compatibility
- Known stable releases
- Security patches included"

### Part 4: Environment Variables (3 min)

**Create .env file:**

```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501
```

**Create .gitignore:**

```
# Python
__pycache__/
*.pyc
venv/
.env

# Streamlit
.streamlit/secrets.toml

# Models
models/*.bin
models/*.pkl

# Data
data/uploads/
*.pdf
*.docx

# IDE
.vscode/
.idea/
```

"Why .env?
- Keeps secrets out of code
- Different configs for dev/prod
- Easy to change without code changes

Why .gitignore?
- Never commit secrets
- Don't bloat repo with models
- Keep it clean and secure"

### Part 5: Streamlit Configuration (2 min)

**Create .streamlit/config.toml:**

```toml
[theme]
primaryColor = "#4F46E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

"This configures:
- App theme (colors, fonts)
- Server settings (port, security)
- Privacy (no usage stats)"

## Live Coding: Create First File

**Create app/app.py:**

```python
import streamlit as st

st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 ATS Resume Scorer")
st.write("Welcome! Let's build this together.")
```

**Run it:**

```bash
streamlit run app/app.py
```

"You should see a basic page. This proves:
- Python is working
- Streamlit is installed
- Port 8501 is available
- We're ready to build!"

## Checkpoint
Students should have:
- [ ] Project structure created
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] spaCy model downloaded
- [ ] .env file created
- [ ] Basic Streamlit app running

## Common Issues & Solutions

**Issue**: "spacy model not found"
**Solution**: `python -m spacy download en_core_web_md`

**Issue**: "Port 8501 already in use"
**Solution**: `streamlit run app/app.py --server.port 8502`

**Issue**: "Module not found"
**Solution**: Check virtual environment is activated

## Transition to Module 03
"Great! Our environment is ready. Now let's build the first real component: the document parser that extracts text from PDFs and Word documents."
