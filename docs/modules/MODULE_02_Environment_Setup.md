# Module 02 - Environment Setup & Dependencies

**Duration**: 20 minutes  
**Type**: Setup & Installation

---

## 🎯 Learning Objectives
- Set up Python development environment
- Install all required dependencies
- Download ML models (spaCy, BERT)
- Verify installation
- Understand project dependencies

---

## 📁 Files to Cover

**Primary Files**:
- `requirements.txt` - All Python dependencies
- `.env.example` - Environment variables template
- `backend/config.py` - Configuration settings

**Files to Create**:
- `.env` - Local environment configuration
- `venv/` - Virtual environment (auto-created)

---

## 📋 Video Script Outline

### Part 1: Prerequisites Check (2 minutes)

**Check Python Installation**:
```bash
# Check Python version
python --version
# or
python3 --version

# Should be Python 3.8 or higher
```

**If Python not installed**:
- Windows: Download from python.org
- Mac: `brew install python3`
- Linux: `sudo apt-get install python3`

**Check pip**:
```bash
pip --version
# or
pip3 --version
```

### Part 2: Create Virtual Environment (3 minutes)

**Why Virtual Environment?**:
- Isolates project dependencies
- Avoids conflicts with other projects
- Easy to reproduce environment
- Clean uninstall (just delete folder)

**Create venv**:
```bash
# Navigate to project directory
cd RESUME_ATS_STREAMLITUI

# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**Verify Activation**:
```bash
which python
# Should point to venv/bin/python
```

### Part 3: Install Dependencies (5 minutes)

**Show requirements.txt**:
```bash
# Open and explain requirements.txt
cat requirements.txt
```

**Key Dependencies**:
```txt
streamlit==1.28.0              # UI framework
sentence-transformers==2.2.2   # BERT models
spacy==3.7.2                   # NLP/NER
PyMuPDF==1.23.8               # PDF parsing
python-docx==1.1.0            # DOCX parsing
scikit-learn==1.3.2           # ML utilities
reportlab==4.0.7              # PDF generation
google-auth==2.23.4           # OAuth
google-auth-oauthlib==1.1.0   # OAuth
```

**Install All Dependencies**:
```bash
# Install from requirements.txt
pip install -r requirements.txt

# This will take 2-3 minutes
# Watch the installation progress
```

**Common Issues**:
- If error with PyMuPDF: `pip install --upgrade pip`
- If error with spaCy: Install build tools
- If slow: Use `pip install --upgrade pip setuptools wheel`

### Part 4: Download spaCy Model (3 minutes)

**What is spaCy Model?**:
- Pre-trained NLP model
- Used for Named Entity Recognition (NER)
- Extracts names, dates, organizations
- Size: ~12MB

**Download**:
```bash
# Download English model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy model loaded!')"
```

### Part 5: Download Fine-Tuned BERT Model (5 minutes)

**What is the Fine-Tuned Model?**:
- Custom BERT model trained on resume-JD pairs
- 85% accuracy vs 70% base model
- Size: ~100MB
- Trained in notebooks (Module 07 will explain)

**Download Options**:

**Option A: Download from provided link**:
```bash
# Download from Google Drive/Dropbox (link provided by instructor)
wget "INSTRUCTOR_PROVIDED_LINK" -O finetuned-bert.zip

# Or use curl
curl -L "INSTRUCTOR_PROVIDED_LINK" -o finetuned-bert.zip

# Extract
unzip finetuned-bert.zip -d backend/models/

# Verify
ls backend/models/finetuned-bert/
# Should see: model.safetensors, config.json, tokenizer.json, etc.
```

**Option B: Use base model (fallback)**:
```bash
# If download fails, app will auto-download base model
# Just note: 70% accuracy instead of 85%
# Base model downloads automatically on first run
```

**Verify Model**:
```bash
python -c "
import os
path = 'backend/models/finetuned-bert/model.safetensors'
if os.path.exists(path):
    print('✅ Fine-tuned model found!')
    print(f'📊 Size: {os.path.getsize(path) / 1024 / 1024:.1f} MB')
else:
    print('⚠️  Fine-tuned model not found, will use base model')
"
```

### Part 6: Configure Environment Variables (2 minutes)

**Create .env file**:
```bash
# Copy example file
cp .env.example .env

# Open in editor
nano .env
# or
code .env
```

**Edit .env**:
```bash
# For now, just set these (OAuth optional for later)
BERT_MODEL=all-MiniLM-L6-v2
SPACY_MODEL=en_core_web_sm

# OAuth (optional - can add in Module 10)
# GOOGLE_CLIENT_ID=your_client_id
# GOOGLE_CLIENT_SECRET=your_client_secret
```

**Explain**:
- Environment variables keep secrets safe
- Never commit .env to git
- .env.example shows what's needed

### Part 7: Verify Complete Installation (2 minutes)

**Create verification script**:
```bash
# Create verify_setup.py
cat > verify_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Installation Verification Script
Checks if all dependencies are installed correctly
"""

import sys

def check_import(module_name, package_name=None):
    """Try to import a module and report status"""
    package_name = package_name or module_name
    try:
        __import__(module_name)
        print(f"✅ {package_name} installed")
        return True
    except ImportError:
        print(f"❌ {package_name} NOT installed")
        return False

print("=" * 50)
print("Checking Installation...")
print("=" * 50)

# Check core dependencies
checks = [
    ("streamlit", "Streamlit"),
    ("sentence_transformers", "sentence-transformers"),
    ("spacy", "spaCy"),
    ("fitz", "PyMuPDF"),
    ("docx", "python-docx"),
    ("sklearn", "scikit-learn"),
    ("reportlab", "ReportLab"),
    ("google.auth", "google-auth"),
]

results = []
for module, name in checks:
    results.append(check_import(module, name))

# Check spaCy model
print("\nChecking spaCy model...")
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    print("✅ spaCy model (en_core_web_sm) loaded")
    results.append(True)
except:
    print("❌ spaCy model NOT found")
    results.append(False)

# Check BERT model
print("\nChecking BERT model...")
import os
if os.path.exists("backend/models/finetuned-bert/model.safetensors"):
    print("✅ Fine-tuned BERT model found")
    results.append(True)
else:
    print("⚠️  Fine-tuned model not found (will use base model)")
    results.append(True)  # Not critical

# Summary
print("\n" + "=" * 50)
if all(results):
    print("🎉 All checks passed! You're ready to go!")
    sys.exit(0)
else:
    print("⚠️  Some checks failed. Please review above.")
    sys.exit(1)
EOF

# Run verification
python verify_setup.py
```

**Expected Output**:
```
==================================================
Checking Installation...
==================================================
✅ Streamlit installed
✅ sentence-transformers installed
✅ spaCy installed
✅ PyMuPDF installed
✅ python-docx installed
✅ scikit-learn installed
✅ ReportLab installed
✅ google-auth installed

Checking spaCy model...
✅ spaCy model (en_core_web_sm) loaded

Checking BERT model...
✅ Fine-tuned BERT model found

==================================================
🎉 All checks passed! You're ready to go!
```

---

## 💻 Code Walkthrough

### Explain requirements.txt Structure

```txt
# UI Framework
streamlit==1.28.0

# Machine Learning
sentence-transformers==2.2.2  # BERT embeddings
scikit-learn==1.3.2          # Similarity calculations

# Natural Language Processing
spacy==3.7.2                 # NER

# Document Processing
PyMuPDF==1.23.8             # PDF parsing
python-docx==1.1.0          # Word docs

# PDF Generation
reportlab==4.0.7

# Authentication
google-auth==2.23.4
google-auth-oauthlib==1.1.0

# Utilities
numpy>=1.24.0
pandas>=2.0.0
```

### Show backend/config.py Model Settings

```python
# Open backend/config.py

# Model paths
SENTENCE_BERT_MODEL = 'all-MiniLM-L6-v2'  # Base model (auto-download)
FINETUNED_MODEL_PATH = 'backend/models/finetuned-bert'  # Our model
SPACY_MODEL = 'en_core_web_sm'  # NER model

# Explain:
# - Base model: Downloads from Hugging Face (first run)
# - Fine-tuned: We provide (better accuracy)
# - spaCy: Downloaded with python -m spacy download
```

---

## 🎤 Key Talking Points

**Why Virtual Environment?**:
- Keeps project dependencies isolated
- Easy to share (requirements.txt)
- Clean development environment
- Professional best practice

**Dependency Management**:
- requirements.txt is standard in Python
- Pin versions for reproducibility
- Update carefully (test after updates)

**Model Downloads**:
- spaCy: Small, fast download
- BERT base: Auto-downloads on first use
- Fine-tuned: Manual download (better accuracy)

**Environment Variables**:
- Keep secrets out of code
- Different configs for dev/prod
- .env for local, environment vars for production

---

## 🐛 Troubleshooting Guide

**Issue**: `pip: command not found`
```bash
# Solution: Install pip
python -m ensurepip --upgrade
```

**Issue**: Permission denied
```bash
# Solution: Don't use sudo, use venv
# Or: pip install --user
```

**Issue**: PyMuPDF installation fails
```bash
# Solution: Update pip and try again
pip install --upgrade pip setuptools wheel
pip install PyMuPDF
```

**Issue**: spaCy model download fails
```bash
# Solution: Download manually
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl
```

**Issue**: Fine-tuned model download fails
```bash
# Solution: Use base model (automatic fallback)
# Or: Download manually from browser and extract
```

---

## ✅ Module Completion Checklist

Students should have:
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (requirements.txt)
- [ ] spaCy model downloaded
- [ ] Fine-tuned BERT model downloaded (or noted fallback)
- [ ] .env file created
- [ ] Verification script passed
- [ ] Understanding of project dependencies

---

## 📝 Homework (Optional)

- Explore requirements.txt and research each library
- Try importing each library in Python REPL
- Read spaCy documentation
- Understand what BERT embeddings are

---

## 🔗 Next Module

**Module 03**: Document Parser - Part 1 (PDF & DOCX)
- Start building the resume parser
- Extract text from PDF and DOCX files
- Text preprocessing and cleaning
- First real code!
