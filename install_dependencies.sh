#!/bin/bash
# Installation script for ATS Resume Scorer
# Run this script after activating your virtual environment

echo "=========================================="
echo "ATS Resume Scorer - Dependency Installation"
echo "=========================================="

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing Python packages..."
pip install -r requirements.txt

# Download spaCy model
echo ""
echo "Downloading spaCy model (en_core_web_md)..."
python -m spacy download en_core_web_md || {
    echo "Failed to download en_core_web_md, trying smaller model..."
    python -m spacy download en_core_web_sm
}

# Download NLTK data
echo ""
echo "Downloading NLTK data..."
python -c "
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']
for package in packages:
    try:
        nltk.download(package, quiet=False)
        print(f'✓ Downloaded {package}')
    except Exception as e:
        print(f'✗ Error downloading {package}: {e}')
"

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "To run the application:"
echo "  streamlit run Home.py"
echo ""
