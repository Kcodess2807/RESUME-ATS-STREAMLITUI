@echo off
REM Installation script for ATS Resume Scorer (Windows)
REM Run this script after activating your virtual environment

echo ==========================================
echo ATS Resume Scorer - Dependency Installation
echo ==========================================

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing Python packages...
pip install -r requirements.txt

REM Download spaCy model
echo.
echo Downloading spaCy model (en_core_web_md)...
python -m spacy download en_core_web_md
if errorlevel 1 (
    echo Failed to download en_core_web_md, trying smaller model...
    python -m spacy download en_core_web_sm
)

REM Download NLTK data
echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

echo.
echo ==========================================
echo Installation complete!
echo ==========================================
echo.
echo To run the application:
echo   streamlit run Home.py
echo.
pause
