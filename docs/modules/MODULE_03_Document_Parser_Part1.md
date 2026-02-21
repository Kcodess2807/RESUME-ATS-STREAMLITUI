# Module 03 - Document Parser Part 1 (PDF & DOCX)

**Duration**: 25 minutes  
**Type**: Backend Development

---

## 🎯 Learning Objectives
- Parse PDF files with PyMuPDF
- Parse DOCX files with python-docx
- Extract and clean text
- Handle different file formats
- Error handling for corrupted files

---

## 📁 Files to Create/Modify

**Primary Files**:
- `backend/parser.py` - Main parser module (Part 1)
- `backend/utils.py` - Utility functions

**Test Files**:
- `test_parser.py` - CLI test script
- Sample resumes in `uploads/` folder

---

## 📋 Code to Write

### 1. backend/utils.py

```python
"""
Utility Functions for Resume Parser
"""

import re
from typing import List, Dict

def clean_text(text: str) -> str:
    """
    Clean extracted text
    - Remove extra whitespace
    - Fix line breaks
    - Remove special characters
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s@.,\-():/]', '', text)
    return text.strip()

def extract_text_from_lines(lines: List[str]) -> str:
    """Join lines into single text"""
    return ' '.join(line.strip() for line in lines if line.strip())
```

### 2. backend/parser.py (Part 1)

```python
"""
Resume Parser - Part 1: Document Processing
Handles PDF and DOCX file parsing
"""

import os
import logging
from typing import Dict, Optional

# PDF parsing
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# DOCX parsing
try:
    from docx import Document
except ImportError:
    Document = None

from backend.utils import clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF file using PyMuPDF
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    if fitz is None:
        raise ImportError("PyMuPDF not installed")
    
    try:
        # Open PDF
        doc = fitz.open(file_path)
        text_parts = []
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_parts.append(text)
        
        # Close document
        doc.close()
        
        # Combine all pages
        full_text = '\n'.join(text_parts)
        
        logger.info(f"Extracted {len(full_text)} characters from PDF")
        return full_text
        
    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        raise


def parse_docx(file_path: str) -> str:
    """
    Extract text from DOCX file using python-docx
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Extracted text as string
    """
    if Document is None:
        raise ImportError("python-docx not installed")
    
    try:
        # Open document
        doc = Document(file_path)
        text_parts = []
        
        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text)
        
        # Combine all text
        full_text = '\n'.join(text_parts)
        
        logger.info(f"Extracted {len(full_text)} characters from DOCX")
        return full_text
        
    except Exception as e:
        logger.error(f"Error parsing DOCX: {str(e)}")
        raise


def parse_txt(file_path: str) -> str:
    """
    Read text from TXT file
    
    Args:
        file_path: Path to TXT file
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"Read {len(text)} characters from TXT")
        return text
        
    except Exception as e:
        logger.error(f"Error reading TXT: {str(e)}")
        raise


def parse_resume(file_path: str) -> Dict:
    """
    Main parser function - detects file type and extracts text
    
    Args:
        file_path: Path to resume file
        
    Returns:
        Dict with parsed data
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Parse based on file type
    if ext == '.pdf':
        raw_text = parse_pdf(file_path)
    elif ext == '.docx':
        raw_text = parse_docx(file_path)
    elif ext == '.txt':
        raw_text = parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # Clean text
    cleaned_text = clean_text(raw_text)
    
    # Return structured data
    return {
        'raw_text': raw_text,
        'cleaned_text': cleaned_text,
        'file_path': file_path,
        'file_type': ext,
        'text_length': len(cleaned_text)
    }


# Test function
if __name__ == "__main__":
    print("Resume Parser - Test Mode")
    print("=" * 50)
    
    # Test with sample file
    test_file = "uploads/sample_resume.pdf"
    
    if os.path.exists(test_file):
        result = parse_resume(test_file)
        print(f"✅ Parsed: {result['file_path']}")
        print(f"📄 Type: {result['file_type']}")
        print(f"📊 Length: {result['text_length']} characters")
        print(f"\nFirst 200 characters:")
        print(result['cleaned_text'][:200])
    else:
        print(f"❌ Test file not found: {test_file}")
```

### 3. test_parser.py (CLI Test Script)

```python
#!/usr/bin/env python3
"""
CLI Test Script for Resume Parser
Usage: python test_parser.py <resume_file>
"""

import sys
from backend.parser import parse_resume

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_parser.py <resume_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"Parsing: {file_path}")
    print("=" * 60)
    
    try:
        result = parse_resume(file_path)
        
        print(f"✅ Success!")
        print(f"\nFile Type: {result['file_type']}")
        print(f"Text Length: {result['text_length']} characters")
        print(f"\nExtracted Text (first 500 chars):")
        print("-" * 60)
        print(result['cleaned_text'][:500])
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🎬 Video Walkthrough

### Part 1: Explain Document Parsing (5 min)
- Why we need to parse different formats
- PDF vs DOCX vs TXT differences
- Libraries: PyMuPDF vs pdfplumber vs PyPDF2
- Why PyMuPDF: Fast, accurate, well-maintained

### Part 2: Build utils.py (3 min)
- Create utility functions
- Text cleaning importance
- Regex for whitespace removal

### Part 3: Build PDF Parser (5 min)
- Import PyMuPDF (fitz)
- Open document
- Loop through pages
- Extract text
- Handle errors

### Part 4: Build DOCX Parser (5 min)
- Import python-docx
- Extract from paragraphs
- Extract from tables
- Combine text

### Part 5: Build Main Parser (4 min)
- File type detection
- Route to correct parser
- Return structured data

### Part 6: Test the Parser (3 min)
- Create test script
- Test with sample PDF
- Test with sample DOCX
- Show extracted text

---

## 🧪 Testing

```bash
# Test with PDF
python test_parser.py uploads/sample_resume.pdf

# Test with DOCX
python test_parser.py uploads/sample_resume.docx

# Test with TXT
python test_parser.py uploads/sample_resume.txt
```

---

## ✅ Module Completion Checklist

Students should have:
- [ ] backend/utils.py with text cleaning
- [ ] backend/parser.py with PDF/DOCX/TXT parsing
- [ ] test_parser.py CLI script
- [ ] Successfully parsed sample resumes
- [ ] Understanding of document parsing

---

## 🔗 Next Module

**Module 04**: Document Parser Part 2 (Contact Info & NER)
- Extract emails, phone numbers, URLs
- Named Entity Recognition with spaCy
- Extract names, companies, locations
