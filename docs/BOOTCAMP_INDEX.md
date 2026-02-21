# Resume ATS Analysis System - Video Bootcamp

## 🎥 Course Overview
Build a production-ready AI-powered Resume Analysis System from scratch using Python, Streamlit, and Machine Learning. This hands-on video bootcamp takes you through the complete development lifecycle with a focus on practical ML implementation.

**Total Duration**: ~4.75 hours | **Level**: Intermediate | **Format**: Video Tutorials + Code-Along

---

## 📹 Module Structure

### Module 00 - Introduction & Project Demo
**Video Duration**: ~15 minutes | **Type**: Introduction

**What You'll See**:
- Welcome and course overview
- **Complete Project Demo** - See the final application in action
  - Upload resume and get instant analysis
  - AI-powered job matching
  - Quality scoring and feedback
  - PDF report generation
  - User authentication and history
- **Problem Statement** - Why build this?
  - The ATS (Applicant Tracking System) challenge
  - How companies filter resumes automatically
  - Why 75% of resumes never reach human recruiters
  - Real-world relevance and use cases
- **What You'll Learn** - Course roadmap
- **Who This Is For** - Prerequisites and expectations

**Key Takeaways**:
- Understanding the end goal
- Real-world problem this solves
- Motivation for building this system

---

### Module 01 - System Architecture & Tech Stack
**Video Duration**: ~25 minutes | **Type**: System Design

**What You'll Learn**:
- **System Architecture Deep Dive**
  - High-level architecture diagram
  - Component interaction flow
  - Data flow pipeline (Upload → Parse → Analyze → Report)
  - ML pipeline architecture
  
**Architecture Overview**:
```
User Interface (Streamlit)
    ↓
Application Layer
    ↓
Backend Processing
    ├── Document Parser (PyMuPDF, python-docx)
    ├── NLP Layer (spaCy NER)
    ├── AI Matching (BERT)
    └── Quality Analyzer
    ↓
Storage (SQLite + File System)
```

**Tech Stack Decisions**:
- **Why Python?** - ML ecosystem, rapid development
- **Why Streamlit?** - Fast UI prototyping, Python-native
- **Why BERT?** - Semantic understanding vs keyword matching
- **Why spaCy?** - Production-ready NER, fast inference
- **Why SQLite?** - Lightweight, serverless, portable

**What You'll Build**:
- Understanding of complete system
- Technology choices and trade-offs
- Scalability considerations

**Diagrams Covered**:
- System architecture
- Data flow diagram
- Component interaction

---

### Module 02 - Environment Setup & Dependencies
**Video Duration**: ~20 minutes | **Type**: Setup

**What You'll Learn**:
- Setting up Python environment
- Installing all dependencies
- Downloading ML models (spaCy + Fine-tuned BERT)
- Project structure walkthrough
- Verification and testing

**What You'll Build**:
- Complete development environment
- Install packages and models
- Download fine-tuned BERT model
- Test basic imports

**Setup Steps**:

1. **Create Virtual Environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download spaCy Model**:
```bash
python -m spacy download en_core_web_sm
```

4. **Download Fine-Tuned BERT Model**:
```bash
# Download from: [INSTRUCTOR WILL PROVIDE LINK]
# Extract to: backend/models/finetuned-bert/
# 
# The model should have this structure:
# backend/models/finetuned-bert/
#   ├── model.safetensors
#   ├── config.json
#   ├── tokenizer.json
#   └── ... (other files)
```

5. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env if needed (OAuth credentials optional for now)
```

6. **Verify Installation**:
```bash
python -c "import spacy; import sentence_transformers; print('✅ All imports successful!')"
```

**Important Notes**:
- Fine-tuned model is ~100MB (one-time download)
- Without fine-tuned model, app will use base model (70% accuracy vs 85%)
- Model download link will be provided in course materials

**Key Files**:
- `requirements.txt`
- `.env.example`
- `backend/config.py`
- `backend/models/finetuned-bert/` (after download)

---

### Module 03 - Document Parser (PDF, DOCX & Text Extraction)
**Video Duration**: ~25 minutes | **Type**: Backend Development

**What You'll Learn**:
- Parsing PDF files with PyMuPDF
- Parsing DOCX files with python-docx
- Text extraction and cleaning
- Handling multiple file formats
- Error handling

**What You'll Build**:
- PDF parser function
- DOCX parser function
- Text preprocessing utilities
- CLI test script

**Key Files**:
- `backend/parser.py` (Part 1)
- `backend/utils.py`

---

### Module 04 - NLP: Contact Extraction & Named Entity Recognition
**Video Duration**: ~25 minutes | **Type**: NLP/ML

**What You'll Learn**:
- Regular expressions for pattern matching
- Extracting emails, phone, LinkedIn, GitHub
- spaCy NER for entity extraction
- Extracting names, companies, locations
- Section detection (Education, Experience, Skills)

**What You'll Build**:
- Contact info extractor (regex-based)
- spaCy NER integration
- Section detection algorithm
- Entity validation

**Key Files**:
- `backend/parser.py` (Part 2)

---

### Module 05 - Skills Extraction & Experience Parsing
**Video Duration**: ~25 minutes | **Type**: Backend Development

**What You'll Learn**:
- Building technical skills database
- Skills extraction and matching
- Work experience parsing with dates
- Education information extraction
- Complete resume structuring

**What You'll Build**:
- Skills database (200+ technical skills)
- Skills matching algorithm
- Experience parser
- Education parser
- Complete resume data structure

**Key Files**:
- `backend/parser.py` (Part 3)
- `backend/data/skills_database.json`

---

### Module 06 - Job Description Parser
**Video Duration**: ~20 minutes | **Type**: Backend Development

**What You'll Learn**:
- Parsing job descriptions
- Extracting requirements
- Identifying required vs preferred skills
- Experience level detection

**What You'll Build**:
- JD parser
- Requirements extractor
- Skills identifier
- Complete JD data structure

**Key Files**:
- `backend/jd_parser.py`

---

### Module 07 - AI Matching with BERT (Core ML)
**Video Duration**: ~30 minutes | **Type**: Machine Learning

**What You'll Learn**:
- Understanding BERT and transformers
- sentence-transformers library
- Generating text embeddings
- Calculating semantic similarity (cosine similarity)
- Building resume-JD matching algorithm
- Skills matching with confidence scores

**What You'll Build**:
- BERT model integration
- Embedding generator
- Similarity calculator
- Skills matching engine
- Overall match score algorithm

**Key Files**:
- `backend/matcher.py`
- `backend/config.py`

**This is the Core ML Module** 🎯

---

### Module 08 - Resume Quality Analysis & Scoring
**Video Duration**: ~25 minutes | **Type**: Business Logic

**What You'll Learn**:
- Building scoring algorithms
- Section-wise quality analysis
- Career level detection (Entry/Mid/Senior)
- Domain classification
- Generating actionable feedback

**What You'll Build**:
- Quality scoring system
- Feedback generator
- Career level detector
- Domain classifier
- Improvement suggestions

**Key Files**:
- `backend/resume_quality_checker.py`
- `backend/strict_scoring.py`
- `backend/ranker.py`

---

### Module 09 - Building the Streamlit UI
**Video Duration**: ~30 minutes | **Type**: Frontend Development

**What You'll Learn**:
- Streamlit fundamentals
- Multi-page application structure
- Session state management
- Custom CSS styling
- Integrating backend with UI
- File upload handling
- Displaying analysis results

**What You'll Build**:
- Main application (`streamlit_app.py`)
- Sidebar navigation
- Home page
- Upload & analysis page
- Results display with charts
- Custom theme

**Key Files**:
- `streamlit_app.py`
- `ui/sidebar.py`
- `ui/pages.py`
- `ui/theme.py`
- `.streamlit/config.toml`

---

### Module 10 - Database, Reports & Authentication
**Video Duration**: ~25 minutes | **Type**: Full Stack

**What You'll Learn**:
- SQLite database design
- Storing resume history
- PDF report generation with charts
- Google OAuth setup
- Guest mode implementation
- Deployment basics

**What You'll Build**:
- Database schema
- CRUD operations
- PDF report generator
- OAuth integration
- Profile history page
- Production configuration

**Key Files**:
- `backend/database.py`
- `backend/report_generator.py`
- `ui/auth.py`
- `resume_history.db`

---

### Module 11 - Testing & Deployment to AWS
**Video Duration**: ~30 minutes | **Type**: Production & Deployment

**What You'll Learn**:
- Testing the complete application locally
- Debugging common issues
- Preparing for production deployment
- **Deploying to AWS Elastic Beanstalk**
- Environment configuration for production
- Managing the fine-tuned model in production
- Monitoring and troubleshooting

**What You'll Build**:
- Complete working application
- Production-ready configuration
- AWS Elastic Beanstalk deployment
- Environment variables setup
- Health monitoring

**Deployment Steps**:

**1. Local Testing**:
```bash
# Test locally first
streamlit run streamlit_app.py

# Verify all features work:
# - Resume upload and parsing
# - Job description matching
# - Quality analysis
# - PDF report generation
# - Database operations
```

**2. Prepare for AWS Deployment**:

Create `requirements.txt` (production):
```txt
streamlit==1.28.0
sentence-transformers==2.2.2
spacy==3.7.2
PyMuPDF==1.23.8
python-docx==1.1.0
scikit-learn==1.3.2
reportlab==4.0.7
google-auth==2.23.4
google-auth-oauthlib==1.1.0
```

Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: streamlit_app:app
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8501
    STREAMLIT_SERVER_ADDRESS: 0.0.0.0
```

Create `Procfile`:
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**3. Handle Fine-Tuned Model**:

Option A: Include in deployment (if < 100MB)
```bash
# Model is already in backend/models/finetuned-bert/
# Will be deployed with application
```

Option B: Download from S3 on startup (recommended for larger models)
```python
# Add to streamlit_app.py startup
import boto3
import os

def download_model_from_s3():
    if not os.path.exists('backend/models/finetuned-bert/model.safetensors'):
        s3 = boto3.client('s3')
        s3.download_file('your-bucket', 'finetuned-bert.zip', '/tmp/model.zip')
        # Extract and move to backend/models/
```

**4. Deploy to AWS Elastic Beanstalk**:

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.9 resume-ats-app --region us-east-1

# Create environment
eb create resume-ats-production

# Deploy
eb deploy

# Open in browser
eb open
```

**5. Configure Environment Variables**:
```bash
# Set environment variables in AWS console or via CLI
eb setenv BERT_MODEL=all-MiniLM-L6-v2
eb setenv GOOGLE_CLIENT_ID=your_client_id
eb setenv GOOGLE_CLIENT_SECRET=your_client_secret
```

**6. Monitor Application**:
```bash
# Check logs
eb logs

# Check health
eb health

# SSH into instance (if needed)
eb ssh
```

**Production Checklist**:
- ✅ All dependencies in requirements.txt
- ✅ Fine-tuned model accessible (local or S3)
- ✅ Environment variables configured
- ✅ Database path configured for persistent storage
- ✅ OAuth redirect URLs updated for production domain
- ✅ Error logging enabled
- ✅ Health check endpoint working

**Alternative Deployment Options**:
- **Streamlit Cloud**: Easiest, free tier available
- **Heroku**: Simple deployment with git push
- **AWS EC2**: More control, manual setup
- **Docker + AWS ECS**: Containerized deployment

**Key Files for Deployment**:
- `requirements.txt`
- `Procfile`
- `.ebextensions/python.config`
- `.streamlit/config.toml`
- `backend/config.py` (production settings)

**Troubleshooting**:
- Model loading issues → Check file paths and permissions
- Memory errors → Use lighter model or increase instance size
- Timeout errors → Increase request timeout in config
- OAuth errors → Verify redirect URLs match production domain

---

## 🎯 What You'll Have Built

By the end of this bootcamp, you'll have a complete application with:

✅ Multi-format resume parser (PDF, DOCX, TXT)  
✅ AI-powered job description matching using BERT  
✅ Resume quality analysis and scoring  
✅ Professional PDF report generation  
✅ User authentication with Google OAuth  
✅ Resume history tracking  
✅ Modern, responsive UI with Streamlit  
✅ Production-ready deployment  

---

## 📂 Project Structure

```
Resume-ATS-System/
├── streamlit_app.py          # Main application (Module 9)
├── backend/
│   ├── parser.py            # Resume parsing (Modules 3-5)
│   ├── jd_parser.py         # Job description parsing (Module 6)
│   ├── matcher.py           # AI matching (Module 7)
│   ├── resume_quality_checker.py  # Scoring (Module 8)
│   ├── database.py          # Data persistence (Module 10)
│   ├── report_generator.py  # PDF reports (Module 10)
│   └── config.py            # Configuration
├── ui/
│   ├── auth.py             # Authentication (Module 10)
│   ├── sidebar.py          # Navigation (Module 9)
│   ├── pages.py            # Page layouts (Module 9)
│   └── theme.py            # Styling (Module 9)
└── requirements.txt         # Dependencies (Module 2)
```

---

## 🎓 Learning Path

```
Module 00: Intro & Demo (15 min)
    ↓
Module 01: System Architecture (25 min)
    ↓
Module 02: Setup & Installation (20 min)
    ↓
Modules 03-05: Document Parser & NLP (75 min)
    ↓
Module 06: Job Description Parser (20 min)
    ↓
Module 07: BERT Matching - Core ML (30 min) 🎯
    ↓
Module 08: Quality Analysis (25 min)
    ↓
Module 09: Streamlit UI (30 min)
    ↓
Module 10: Database & Auth (25 min)
    ↓
Module 11: Testing & AWS Deployment (30 min)
```

**Total Time**: ~4.75 hours  
**Approach**: Problem → Design → Backend/ML → UI → Production → AWS Deployment

---

## 🛠️ Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **ML/AI**: BERT (sentence-transformers), spaCy NER
- **Document Processing**: PyMuPDF, python-docx
- **Database**: SQLite
- **Authentication**: Google OAuth 2.0
- **Reports**: ReportLab
- **Deployment**: AWS Elastic Beanstalk
- **Cloud Storage**: AWS S3 (for model hosting)

---

## 📋 Prerequisites

**Required**:
- Python 3.8 or higher
- Basic Python programming (functions, classes, modules)
- Command line familiarity

**Recommended**:
- Basic understanding of machine learning
- Experience with web applications
- Git basics
- AWS account (free tier sufficient for deployment)

---

## 🚀 How to Use This Course

1. **Start with Module 00** - Understand the problem and see the demo
2. **Follow in sequence** - Each module builds on the previous
3. **Code along** - Pause videos and implement as you go
4. **Test frequently** - Run code after each module
5. **Experiment** - Try modifications and improvements

---

## 💡 Real-World Applications

This system can be used for:
- Job seekers optimizing resumes for ATS
- Recruiters quickly screening candidates
- Career coaches providing feedback
- HR departments automating initial screening
- Educational institutions teaching resume best practices

---

## 📞 Support

- Check `README.md` for detailed documentation
- Review code comments in each file
- Test with sample resumes provided
- Refer to `requirements.txt` for dependencies


