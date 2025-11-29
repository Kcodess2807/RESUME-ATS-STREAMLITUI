# Project Structure

This document describes the organization of the ATS Resume Scorer project.

## Directory Structure

```
ats-resume-scorer/
│
├── .kiro/                          # Kiro specifications and configuration
│   └── specs/
│       └── ats-resume-scorer/
│           ├── requirements.md     # Feature requirements
│           ├── design.md          # Design document
│           └── tasks.md           # Implementation tasks
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                # Theme and server settings
│
├── pages/                          # Streamlit multi-page app pages
│   ├── 1_🎯_ATS_Scorer.py        # Main scoring page (to be created)
│   ├── 2_📊_History.py           # Analysis history (to be created)
│   └── 3_📚_Resources.py         # Resources and tips (to be created)
│
├── utils/                          # Core utility modules
│   ├── __init__.py                # Package initialization
│   ├── model_loader.py            # AI model loading and caching
│   ├── file_parser.py             # File upload and parsing (to be created)
│   ├── text_processor.py          # NLP text processing (to be created)
│   ├── skill_validator.py         # Skill validation logic (to be created)
│   ├── grammar_checker.py         # Grammar checking (to be created)
│   ├── location_detector.py       # Location privacy detection (to be created)
│   ├── scorer.py                  # Scoring engine (to be created)
│   └── report_generator.py        # PDF report generation (to be created)
│
├── data/                           # Data files and databases
│   ├── skills_database.json       # Technical and soft skills (to be created)
│   ├── action_verbs.json          # Common action verbs (to be created)
│   ├── industry_keywords.json     # Industry-specific terms (to be created)
│   └── common_locations.json      # Location patterns (to be created)
│
├── assets/                         # Static assets
│   ├── styles.css                 # Custom CSS (to be created)
│   └── images/                    # Icons and images (to be created)
│
├── models/                         # Cached AI models
│   └── .gitkeep                   # (Models downloaded at runtime)
│
├── Home.py                         # Landing page (to be created)
│
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
│
├── README.md                       # Main documentation
├── SETUP_GUIDE.md                 # Detailed setup instructions
├── PROJECT_STRUCTURE.md           # This file
│
├── setup.py                        # Automated setup script
├── install_dependencies.sh         # Linux/Mac installation script
├── install_dependencies.bat        # Windows installation script
└── verify_setup.py                # Setup verification script
```

## Module Responsibilities

### Frontend (Streamlit Pages)

- **Home.py**: Landing page with hero section, features, and navigation
- **pages/1_🎯_ATS_Scorer.py**: Main analysis page with file upload and results
- **pages/2_📊_History.py**: View past analyses and track progress
- **pages/3_📚_Resources.py**: Resume tips and ATS optimization guides

### Backend (Utils Modules)

- **model_loader.py**: Loads and caches AI models (spaCy, Sentence-Transformers, LanguageTool)
- **file_parser.py**: Validates and extracts text from PDF/DOC/DOCX files
- **text_processor.py**: Extracts sections, skills, keywords, and contact info using NLP
- **skill_validator.py**: Validates skills against projects using semantic similarity
- **grammar_checker.py**: Detects grammar, spelling, and language quality issues
- **location_detector.py**: Identifies sensitive location information for privacy
- **scorer.py**: Calculates overall ATS score and component scores
- **report_generator.py**: Generates PDF reports and action item checklists

### Data Files

- **skills_database.json**: Comprehensive list of technical and soft skills
- **action_verbs.json**: Action verbs for resume bullet points
- **industry_keywords.json**: Industry-specific terminology
- **common_locations.json**: Location patterns for privacy detection

## File Naming Conventions

- **Python files**: lowercase_with_underscores.py
- **Streamlit pages**: Numbered with emoji prefix (e.g., `1_🎯_ATS_Scorer.py`)
- **Data files**: lowercase_with_underscores.json
- **Documentation**: UPPERCASE_WITH_UNDERSCORES.md (for guides) or Title_Case.md

## Import Structure

```python
# Standard library imports
import os
import sys

# Third-party imports
import streamlit as st
import spacy
from sentence_transformers import SentenceTransformer

# Local imports
from utils.model_loader import get_models
from utils.file_parser import extract_text
from utils.scorer import calculate_overall_score
```

## Configuration Files

- **.streamlit/config.toml**: Streamlit theme, server, and browser settings
- **requirements.txt**: Python package dependencies with version constraints
- **.gitignore**: Excludes virtual environments, cached models, and sensitive data

## Development Workflow

1. **Setup**: Run installation scripts to set up environment
2. **Verify**: Use `verify_setup.py` to check all dependencies
3. **Develop**: Implement features according to tasks.md
4. **Test**: Write and run tests for each module
5. **Run**: Launch with `streamlit run Home.py`

## Model Storage

AI models are cached in the following locations:

- **spaCy models**: `venv/lib/python3.x/site-packages/spacy/data/`
- **Sentence-Transformers**: `~/.cache/torch/sentence_transformers/`
- **LanguageTool**: `~/.cache/language_tool_python/`

These are automatically managed and don't need to be committed to version control.

## Next Steps

Refer to `tasks.md` in `.kiro/specs/ats-resume-scorer/` for the implementation plan.
