# Modules 05-11 - Quick Reference Guide

This document provides a quick overview of the remaining modules. For detailed scripts, refer to `MODULES_OVERVIEW.md` and the existing code in the repository.

---

## Module 05 - Document Parser Part 3 (Skills & Experience)
**Duration**: 25 minutes

### Files to Modify:
- `backend/parser.py` - Add section detection, skills, experience parsing
- `backend/data/skills_database.json` - Create skills database

### Key Functions to Implement:
```python
def detect_sections(text: str) -> Dict[str, str]
def extract_skills(text: str, skills_db: List[str]) -> List[str]
def parse_experience(text: str) -> List[Dict]
def parse_education(text: str) -> List[Dict]
def structure_resume(parsed_data: Dict) -> Dict  # Final output
```

### What to Build:
1. Section detection using regex patterns from config
2. Skills extraction (match against 200+ skills from TECH_SKILLS)
3. Experience parsing (extract titles, companies, dates, descriptions)
4. Education parsing (extract degrees, institutions, dates)
5. Complete structured resume output

### Config to Use:
- `SECTION_PATTERNS` - Regex for section headers
- `TECH_SKILLS` - 200+ technical skills list

---

## Module 06 - Job Description Parser
**Duration**: 20 minutes

### Files to Create:
- `backend/jd_parser.py` - Complete JD parser

### Key Functions to Implement:
```python
def parse_job_description(jd_text: str) -> Dict
def extract_required_skills(jd_text: str) -> List[str]
def extract_experience_requirements(jd_text: str) -> Dict
def extract_education_requirements(jd_text: str) -> Dict
```

### What to Build:
1. Parse JD text
2. Extract required vs preferred skills
3. Extract experience requirements (years, level)
4. Extract education requirements
5. Structure JD data for matching

### Testing:
```bash
python -c "from backend.jd_parser import parse_job_description; print(parse_job_description('...'))"
```

---

## Module 07 - AI Matching with BERT (Core ML)
**Duration**: 30 minutes ⭐

### Files to Create:
- `backend/matcher.py` - Complete BERT matching engine

### Key Functions to Implement:
```python
def _load_model() -> SentenceTransformer
def create_resume_embedding(parsed_resume: Dict) -> np.ndarray
def create_jd_embedding(jd_text: str) -> np.ndarray
def calculate_overall_similarity(resume_emb, jd_emb) -> float
def semantic_skill_matching(resume_skills, jd_skills) -> Tuple
def calculate_experience_score(resume, jd_req) -> Dict
def calculate_education_score(resume, jd_edu) -> float
def match_resume_to_job(resume: Dict, jd: Dict) -> Dict
```

### What to Build:
1. Load BERT model (fine-tuned or base)
2. Generate 768-dim embeddings
3. Calculate cosine similarity
4. Semantic skill matching (React = ReactJS)
5. Experience relevance scoring
6. Education matching
7. Overall match score (0-100%)

### Config to Use:
- `SENTENCE_BERT_MODEL` - Base model name
- `FINETUNED_MODEL_PATH` - Fine-tuned model path
- `SKILL_MATCH_THRESHOLD` - 0.50 (50% similarity)
- `DEFAULT_WEIGHTS` - Scoring weights

### Key Concepts to Explain:
- What are embeddings? (768-dimensional vectors)
- Cosine similarity (how similar are two vectors?)
- Why BERT? (understands meaning, not just keywords)
- Fine-tuned vs base model (85% vs 70% accuracy)

---

## Module 08 - Quality Analysis & Scoring
**Duration**: 25 minutes

### Files to Create:
- `backend/resume_quality_checker.py` - Quality analysis
- `backend/strict_scoring.py` - Scoring algorithms
- `backend/ranker.py` - Ranking logic

### Key Functions to Implement:
```python
def analyze_resume_quality(parsed_resume: Dict) -> Dict
def score_section(section_data: Dict, section_type: str) -> float
def detect_career_level(experience: List) -> str  # Entry/Mid/Senior
def classify_domain(skills: List, experience: List) -> str
def generate_feedback(scores: Dict) -> List[str]
def calculate_overall_score(component_scores: Dict) -> float
```

### What to Build:
1. Section-wise scoring (Education: 0-100, Experience: 0-100, etc.)
2. Overall quality score
3. Career level detection (0-2 years = Entry, 2-5 = Mid, 5+ = Senior)
4. Domain classification (Software, Data Science, DevOps, etc.)
5. Actionable feedback generation
6. Improvement suggestions

### Config to Use:
- `RATING_THRESHOLDS` - A+, A, B, C, D thresholds
- `STATUS_THRESHOLDS` - Excellent, Good, Moderate
- `EXPERIENCE_LEVELS` - Entry, Mid, Senior, Lead ranges

---

## Module 09 - Streamlit UI
**Duration**: 30 minutes

### Files to Create:
- `streamlit_app.py` - Main application
- `ui/sidebar.py` - Navigation sidebar
- `ui/pages.py` - Page layouts (Home, Upload, Profile)
- `ui/theme.py` - Custom CSS styling
- `.streamlit/config.toml` - Streamlit configuration

### What to Build:
1. **Main App Structure**:
   - Session state management
   - Page routing
   - Import all backend modules

2. **Sidebar Navigation**:
   - Home, Upload & Analyze, My Profile
   - User info display
   - Navigation logic

3. **Home Page**:
   - Hero section
   - Feature highlights
   - Getting started guide

4. **Upload & Analyze Page**:
   - File uploader (PDF, DOCX, TXT)
   - Job description input (text area or file)
   - Analyze button
   - Progress indicators
   - Results display with tabs:
     - Overview (match score, quality score)
     - Skills Analysis (matched vs missing)
     - Experience Analysis
     - Education Analysis
     - Detailed Feedback
   - Resume preview (right column)
   - PDF report download button

5. **Profile Page**:
   - Resume history table
   - View past analyses
   - Delete history

6. **Custom Styling**:
   - Color scheme
   - Fonts
   - Button styles
   - Progress bars

### Key Streamlit Components:
```python
st.file_uploader()
st.text_area()
st.button()
st.progress()
st.tabs()
st.columns()
st.metric()
st.dataframe()
st.download_button()
st.session_state
```

### Integration:
```python
from backend.parser import parse_resume
from backend.jd_parser import parse_job_description
from backend.matcher import match_resume_to_job
from backend.resume_quality_checker import analyze_resume_quality
from backend.database import save_analysis, get_user_history
from backend.report_generator import generate_pdf_report
```

---

## Module 10 - Database, Reports & Authentication
**Duration**: 25 minutes

### Files to Create:
- `backend/database.py` - SQLite operations
- `backend/report_generator.py` - PDF report generation
- `ui/auth.py` - Google OAuth integration

### 1. Database (backend/database.py):

**Schema**:
```sql
CREATE TABLE resume_analyses (
    id INTEGER PRIMARY KEY,
    user_email TEXT,
    resume_name TEXT,
    upload_date TIMESTAMP,
    overall_score REAL,
    match_score REAL,
    quality_score REAL,
    analysis_data TEXT  -- JSON
)
```

**Functions**:
```python
def init_database()
def save_analysis(user_email, resume_name, scores, analysis_data)
def get_user_history(user_email) -> List[Dict]
def delete_analysis(analysis_id)
```

### 2. PDF Reports (backend/report_generator.py):

**Functions**:
```python
def generate_pdf_report(analysis_data: Dict, output_path: str)
def create_header(canvas, resume_name)
def create_score_section(canvas, scores)
def create_skills_section(canvas, skills_data)
def create_feedback_section(canvas, feedback)
def add_charts(canvas, data)  # Progress bars, pie charts
```

**Libraries**: ReportLab

### 3. Authentication (ui/auth.py):

**Functions**:
```python
def init_oauth()
def authenticate_user() -> Dict  # Returns user info
def guest_mode() -> Dict  # Guest user
def logout()
```

**OAuth Flow**:
1. User clicks "Sign in with Google"
2. Redirect to Google OAuth
3. Get authorization code
4. Exchange for access token
5. Get user info
6. Store in session_state

**Guest Mode**:
- No authentication required
- Limited features (no history)
- For testing/demo

---

## Module 11 - Testing & AWS Deployment
**Duration**: 30 minutes

### Files to Create:
- `Procfile` - Process file for deployment
- `.ebextensions/python.config` - Elastic Beanstalk configuration

### Part 1: Local Testing (10 min)

**Test Checklist**:
```bash
# 1. Test parser
python test_parser.py uploads/sample_resume.pdf

# 2. Test matcher
python -c "from backend.matcher import _load_model; print(_load_model())"

# 3. Test complete app
streamlit run streamlit_app.py

# 4. Test all features:
- Upload resume
- Add job description
- View analysis
- Generate PDF report
- Check profile history
- Test OAuth (if configured)
- Test guest mode
```

### Part 2: AWS Elastic Beanstalk Deployment (20 min)

**1. Prepare Files**:

`Procfile`:
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

`.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: streamlit_app:app
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8501
    STREAMLIT_SERVER_ADDRESS: 0.0.0.0
```

**2. Install EB CLI**:
```bash
pip install awsebcli
```

**3. Initialize EB Application**:
```bash
eb init -p python-3.9 resume-ats-app --region us-east-1
```

**4. Create Environment**:
```bash
eb create resume-ats-production
```

**5. Deploy**:
```bash
eb deploy
```

**6. Configure Environment Variables**:
```bash
eb setenv BERT_MODEL=all-MiniLM-L6-v2
eb setenv GOOGLE_CLIENT_ID=your_client_id
eb setenv GOOGLE_CLIENT_SECRET=your_client_secret
```

**7. Open Application**:
```bash
eb open
```

**8. Monitor**:
```bash
eb logs      # View logs
eb health    # Check health
eb ssh       # SSH into instance
```

### Handling Fine-Tuned Model:

**Option A**: Include in deployment (if < 100MB)
- Model is in `backend/models/finetuned-bert/`
- Will be deployed with application

**Option B**: Download from S3 on startup
```python
# Add to streamlit_app.py
import boto3
import os

if not os.path.exists('backend/models/finetuned-bert/model.safetensors'):
    s3 = boto3.client('s3')
    s3.download_file('your-bucket', 'finetuned-bert.zip', '/tmp/model.zip')
    # Extract and move
```

### Production Checklist:
- [ ] All dependencies in requirements.txt
- [ ] Environment variables configured
- [ ] OAuth redirect URLs updated
- [ ] Database path configured
- [ ] Error logging enabled
- [ ] Health check working
- [ ] Model accessible
- [ ] Test all features on production

### Alternative Deployment Options:
- **Streamlit Cloud**: Easiest, free tier, git-based
- **Heroku**: Simple, git push deployment
- **AWS EC2**: More control, manual setup
- **Docker + ECS**: Containerized, scalable

---

## 🎯 Complete File List

By the end of all modules, students will have created:

### Backend (8 files):
1. `backend/utils.py`
2. `backend/parser.py`
3. `backend/jd_parser.py`
4. `backend/matcher.py`
5. `backend/resume_quality_checker.py`
6. `backend/strict_scoring.py`
7. `backend/ranker.py`
8. `backend/database.py`
9. `backend/report_generator.py`

### Frontend (5 files):
10. `streamlit_app.py`
11. `ui/sidebar.py`
12. `ui/pages.py`
13. `ui/theme.py`
14. `ui/auth.py`

### Configuration (3 files):
15. `.streamlit/config.toml`
16. `Procfile`
17. `.ebextensions/python.config`

### Data (1 file):
18. `backend/data/skills_database.json`

### Testing (1 file):
19. `test_parser.py`

**Total**: ~20 files, ~2,500 lines of Python code

---

## 📚 Additional Resources

For detailed implementation of each module:
1. Check the actual code in the repository
2. Refer to `MODULES_OVERVIEW.md` for function signatures
3. Use the existing codebase as reference
4. Test each module independently

---

## 🎓 Teaching Tips

### Module 05-06 (Parser completion):
- Show before/after of unstructured vs structured data
- Use real resume examples
- Demonstrate skills matching

### Module 07 (BERT - Most Important):
- Spend extra time explaining embeddings
- Show similarity scores for different skill pairs
- Demonstrate "React" matching "ReactJS"
- Explain fine-tuned vs base model

### Module 08 (Quality):
- Show how scores change with different resumes
- Demonstrate feedback generation
- Explain career level detection logic

### Module 09 (UI):
- Show Streamlit components in action
- Build incrementally (one page at a time)
- Test frequently in browser

### Module 10 (Database & Auth):
- Show database schema
- Demonstrate OAuth flow
- Test guest mode

### Module 11 (Deployment):
- Show live deployment process
- Demonstrate monitoring
- Celebrate the final product!

---

## ✅ Success Criteria

Students should be able to:
- [ ] Parse resumes from multiple formats
- [ ] Extract structured information
- [ ] Match resumes to job descriptions using AI
- [ ] Generate quality scores and feedback
- [ ] Build interactive UI
- [ ] Store data in database
- [ ] Generate PDF reports
- [ ] Implement authentication
- [ ] Deploy to AWS
- [ ] Explain the complete system

---

**For detailed code examples, refer to the existing codebase in the repository!**
