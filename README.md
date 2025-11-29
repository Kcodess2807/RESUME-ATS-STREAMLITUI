# ATS Resume Scorer

A comprehensive web application that analyzes resumes for Applicant Tracking System (ATS) compatibility using local AI models.

## Features

- **Resume Analysis**: Upload PDF, DOC, or DOCX files for comprehensive analysis
- **Skill Validation**: Verify that claimed skills are demonstrated in projects
- **Grammar Checking**: Detect spelling, grammar, and language quality issues
- **Privacy Recommendations**: Identify sensitive location information
- **Job Description Comparison**: Compare resume against specific job postings
- **Actionable Feedback**: Receive prioritized recommendations for improvement
- **Local AI Models**: All processing runs locally for privacy and offline capability

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Run the setup script**:
   ```bash
   python setup.py
   ```

   This will:
   - Install all required dependencies
   - Download spaCy language model (en_core_web_md)
   - Download NLTK data packages
   - Set up the project structure

### Manual Setup (Alternative)

If the setup script fails, you can install dependencies manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
```

## Running the Application

1. **Activate your virtual environment** (if not already activated)

2. **Start the Streamlit app**:
   ```bash
   streamlit run Home.py
   ```

3. **Access the application**:
   - Open your browser and navigate to: `http://localhost:8501`

## Project Structure

```
ats-resume-scorer/
├── Home.py                 # Landing page
├── pages/                  # Additional pages
│   ├── 1_🎯_ATS_Scorer.py
│   ├── 2_📊_History.py
│   └── 3_📚_Resources.py
├── utils/                  # Core processing modules
│   ├── file_parser.py
│   ├── text_processor.py
│   ├── skill_validator.py
│   ├── grammar_checker.py
│   ├── location_detector.py
│   ├── scorer.py
│   └── report_generator.py
├── data/                   # Data files and databases
├── assets/                 # Static assets (CSS, images)
├── models/                 # Cached AI models
├── .streamlit/            # Streamlit configuration
│   └── config.toml
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Usage

1. **Navigate to the ATS Scorer page** from the landing page
2. **Upload your resume** (PDF, DOC, or DOCX format, max 5MB)
3. **Optionally upload a job description** for comparison
4. **Wait for analysis** (progress indicator shows current stage)
5. **Review results** including scores, recommendations, and action items
6. **Download reports** (PDF report or action items checklist)

## Technology Stack

- **Frontend**: Streamlit
- **NLP**: spaCy, NLTK
- **Embeddings**: Sentence-Transformers
- **Grammar**: LanguageTool
- **PDF Processing**: pdfplumber, PyPDF2
- **Document Processing**: python-docx
- **Report Generation**: fpdf2, ReportLab

## Privacy

All AI models run locally on your machine. No resume data is sent to external APIs or servers.

## Troubleshooting

### Model Download Issues

If spaCy model download fails:
```bash
python -m spacy download en_core_web_sm  # Smaller alternative
```

### NLTK Data Issues

If NLTK data download fails:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### Port Already in Use

If port 8501 is already in use:
```bash
streamlit run Home.py --server.port 8502
```

## License

[Add your license information here]

## Support

[Add support contact information here]
