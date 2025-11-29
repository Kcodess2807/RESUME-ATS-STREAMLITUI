#!/usr/bin/env python3
"""
Setup script for ATS Resume Scorer
Handles virtual environment setup, dependency installation, and model downloads
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during: {description}")
        print(f"Error: {e}")
        return False


def main():
    print("ATS Resume Scorer - Setup Script")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    ):
        sys.exit(1)
    
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies from requirements.txt"
    ):
        sys.exit(1)
    
    # Download spaCy model
    print("\n" + "="*60)
    print("Downloading spaCy English model (en_core_web_md)")
    print("="*60)
    if not run_command(
        f"{sys.executable} -m spacy download en_core_web_md",
        "Downloading spaCy model"
    ):
        print("Warning: spaCy model download failed. Trying smaller model...")
        if not run_command(
            f"{sys.executable} -m spacy download en_core_web_sm",
            "Downloading spaCy small model"
        ):
            print("Error: Could not download spaCy model")
            sys.exit(1)
    
    # Download NLTK data
    print("\n" + "="*60)
    print("Downloading NLTK data")
    print("="*60)
    
    nltk_script = """
import nltk
import ssl

# Handle SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required NLTK data
packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']
for package in packages:
    try:
        nltk.download(package, quiet=True)
        print(f"✓ Downloaded {package}")
    except Exception as e:
        print(f"✗ Error downloading {package}: {e}")
"""
    
    with open('_nltk_download.py', 'w') as f:
        f.write(nltk_script)
    
    if not run_command(
        f"{sys.executable} _nltk_download.py",
        "Downloading NLTK data packages"
    ):
        print("Warning: Some NLTK downloads may have failed")
    
    # Clean up temporary file
    if os.path.exists('_nltk_download.py'):
        os.remove('_nltk_download.py')
    
    # Create placeholder files in directories
    print("\n" + "="*60)
    print("Creating placeholder files")
    print("="*60)
    
    placeholders = [
        'pages/.gitkeep',
        'utils/.gitkeep',
        'data/.gitkeep',
        'assets/.gitkeep',
        'models/.gitkeep'
    ]
    
    for placeholder in placeholders:
        os.makedirs(os.path.dirname(placeholder), exist_ok=True)
        with open(placeholder, 'w') as f:
            f.write('')
        print(f"✓ Created {placeholder}")
    
    print("\n" + "="*60)
    print("Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run the application: streamlit run Home.py")
    print("2. Access the app at: http://localhost:8501")
    print("\nNote: First run may take longer as models are loaded and cached.")


if __name__ == "__main__":
    main()
