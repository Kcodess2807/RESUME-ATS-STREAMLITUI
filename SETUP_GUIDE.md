# ATS Resume Scorer - Setup Guide

This guide will walk you through setting up the ATS Resume Scorer application.

## Prerequisites

- **Python 3.8 or higher** - Check your version: `python --version`
- **pip** - Python package manager (usually comes with Python)
- **Internet connection** - Required for downloading models (first time only)

## Step-by-Step Setup

### 1. Create Virtual Environment (Recommended)

A virtual environment keeps your project dependencies isolated.

**On Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when activated.

### 2. Install Dependencies and Download Models

**Option A: Using Installation Scripts (Recommended)**

**On Linux/Mac:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

**On Windows:**
```cmd
install_dependencies.bat
```

**Option B: Manual Installation**

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install Python packages
pip install -r requirements.txt

# Download spaCy model (choose one)
python -m spacy download en_core_web_md  # Recommended (larger, more accurate)
# OR
python -m spacy download en_core_web_sm  # Smaller, faster

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
```

### 3. Verify Installation

Run the verification script to ensure everything is installed correctly:

```bash
python verify_setup.py
```

This will check:
- All Python packages are installed
- spaCy model is available
- NLTK data is downloaded

### 4. Run the Application

```bash
streamlit run Home.py
```

The application will open in your default browser at `http://localhost:8501`

## Troubleshooting

### Issue: "Command not found: python"

Try using `python3` instead:
```bash
python3 -m venv venv
python3 verify_setup.py
```

### Issue: spaCy model download fails

**Solution 1:** Try the smaller model:
```bash
python -m spacy download en_core_web_sm
```

**Solution 2:** Download manually:
1. Visit: https://github.com/explosion/spacy-models/releases
2. Download `en_core_web_sm-3.7.0.tar.gz` (or latest version)
3. Install: `pip install /path/to/downloaded/file.tar.gz`

### Issue: NLTK download fails with SSL error

Add this to your Python script or run in Python console:
```python
import ssl
import nltk

ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
```

### Issue: LanguageTool is slow or fails

LanguageTool downloads a Java-based grammar checker on first use. This is normal and only happens once. If it fails:

1. Ensure you have Java installed: `java -version`
2. If not, install Java JRE 8 or higher
3. Restart the application

### Issue: Port 8501 already in use

Run on a different port:
```bash
streamlit run Home.py --server.port 8502
```

### Issue: Out of memory errors

The AI models require significant memory. Solutions:
1. Close other applications
2. Use the smaller spaCy model (`en_core_web_sm`)
3. Increase system swap space
4. Use a machine with more RAM (minimum 4GB recommended)

## Model Information

### spaCy Models

- **en_core_web_md** (Recommended): ~40MB, better accuracy
- **en_core_web_sm** (Alternative): ~12MB, faster but less accurate

### Sentence-Transformers

- **all-MiniLM-L6-v2**: ~80MB, downloads automatically on first use
- Cached in: `~/.cache/torch/sentence_transformers/`

### LanguageTool

- Downloads Java-based grammar checker (~200MB) on first use
- Cached in: `~/.cache/language_tool_python/`

## First Run

The first time you run the application:
1. Models will be loaded into memory (takes 10-30 seconds)
2. Streamlit will cache the models for faster subsequent runs
3. LanguageTool may download additional resources

## Updating Dependencies

To update all packages to their latest versions:

```bash
pip install --upgrade -r requirements.txt
```

## Deactivating Virtual Environment

When you're done working on the project:

```bash
deactivate
```

## Getting Help

If you encounter issues not covered here:
1. Check the error message carefully
2. Ensure all prerequisites are met
3. Try the verification script: `python verify_setup.py`
4. Check the main README.md for additional information

## Next Steps

Once setup is complete:
1. Read the main README.md for usage instructions
2. Explore the application features
3. Upload a test resume to see the analysis in action
