#!/usr/bin/env python3
"""
Verification script to check if all dependencies and models are properly installed
"""

import sys


def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False


def check_spacy_model(model_name):
    """Check if a spaCy model is installed"""
    try:
        import spacy
        spacy.load(model_name)
        print(f"✓ spaCy model '{model_name}' is installed")
        return True
    except OSError:
        print(f"✗ spaCy model '{model_name}' is NOT installed")
        return False
    except ImportError:
        print(f"✗ spaCy is not installed, cannot check model")
        return False


def check_nltk_data(package_name):
    """Check if NLTK data package is downloaded"""
    try:
        import nltk
        nltk.data.find(f'tokenizers/{package_name}')
        print(f"✓ NLTK data '{package_name}' is downloaded")
        return True
    except LookupError:
        print(f"✗ NLTK data '{package_name}' is NOT downloaded")
        return False
    except ImportError:
        print(f"✗ NLTK is not installed, cannot check data")
        return False


def main():
    print("="*60)
    print("ATS Resume Scorer - Setup Verification")
    print("="*60)
    print(f"\nPython version: {sys.version}")
    print()
    
    all_ok = True
    
    # Check core packages
    print("Checking core packages:")
    print("-" * 60)
    packages = [
        ('streamlit', 'streamlit'),
        ('streamlit-authenticator', 'streamlit_authenticator'),
        ('pdfplumber', 'pdfplumber'),
        ('PyPDF2', 'PyPDF2'),
        ('python-docx', 'docx'),
        ('spacy', 'spacy'),
        ('nltk', 'nltk'),
        ('sentence-transformers', 'sentence_transformers'),
        ('language-tool-python', 'language_tool_python'),
        ('scikit-learn', 'sklearn'),
        ('fpdf2', 'fpdf'),
        ('reportlab', 'reportlab'),
    ]
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_ok = False
    
    # Check spaCy models
    print("\nChecking spaCy models:")
    print("-" * 60)
    spacy_models = ['en_core_web_md', 'en_core_web_sm']
    spacy_ok = False
    for model in spacy_models:
        if check_spacy_model(model):
            spacy_ok = True
            break
    
    if not spacy_ok:
        print("⚠ Warning: No spaCy model found. At least one is required.")
        all_ok = False
    
    # Check NLTK data
    print("\nChecking NLTK data:")
    print("-" * 60)
    nltk_packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']
    for package in nltk_packages:
        if not check_nltk_data(package):
            all_ok = False
    
    # Summary
    print("\n" + "="*60)
    if all_ok:
        print("✓ All dependencies and models are properly installed!")
        print("="*60)
        print("\nYou can now run the application:")
        print("  streamlit run Home.py")
        return 0
    else:
        print("✗ Some dependencies or models are missing")
        print("="*60)
        print("\nPlease run the installation script:")
        print("  Linux/Mac: ./install_dependencies.sh")
        print("  Windows: install_dependencies.bat")
        print("\nOr install manually:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
