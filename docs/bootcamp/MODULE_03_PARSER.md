# Module 03: Document Parser (25 min)

## Objective
Build a robust file parser that extracts text from PDF, DOC, and DOCX files.

## Files to Create
- `app/core/parser.py`

## Script

### Part 1: Why File Parsing Matters (3 min)

"Before we can analyze a resume, we need to extract the text. Sounds simple, right? It's not.

**Challenges:**
- PDFs can be images (scanned documents)
- PDFs can have complex layouts (columns, tables)
- Word documents have formatting, styles
- Files can be corrupted
- Different encodings

**Our approach:**
- Try pdfplumber first (best for PDFs)
- Fallback to PyPDF2 if needed
- Use python-docx for Word files
- Validate file type and size
- Handle errors gracefully"

### Part 2: Live Coding - File Validation (7 min)

**Create app/core/parser.py:**

```python
"""
Document Parser Module
Extracts text from PDF, DOC, and DOCX files
"""

import pdfplumber
import PyPDF2
from docx import Document
import io
from typing import Tuple, Dict

# Constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx']


class FileValidationError(Exception):
    """Raised when file validation fails"""
    pass


class FileParsingError(Exception):
    """Raised when file parsing fails"""
    pass


def validate_file(file_data: bytes, filename: str) -> None:
    """
    Validate uploaded file
    
    Why this matters:
    - Prevents malicious files
    - Ensures we can process it
    - Gives clear error messages
    """
    # Check file size
    if len(file_data) > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File too large. Max size: {MAX_FILE_SIZE_BYTES // (1024*1024)}MB"
        )
    
    # Check file extension
    ext = filename.lower().split('.')[-1]
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file is not empty
    if len(file_data) == 0:
        raise FileValidationError("File is empty")
```

**Explain:**
"Why these validations?
- **Size limit**: Prevents memory issues, DoS attacks
- **Extension check**: Only process supported formats
- **Empty check**: Fail fast on bad uploads

Why custom exceptions?
- Clear error types
- Easy to catch specific errors
- Better error messages"

### Part 3: PDF Parsing (8 min)

```python
def parse_pdf(file_data: bytes) -> str:
    """
    Extract text from PDF using pdfplumber
    
    Why pdfplumber?
    - Better layout detection than PyPDF2
    - Handles tables and columns
    - More accurate text extraction
    """
    try:
        text_parts = []
        
        # Create file-like object
        pdf_file = io.BytesIO(file_data)
        
        # Open with pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # Extract text from page
                page_text = page.extract_text()
                
                if page_text:
                    text_parts.append(page_text)
        
        # Join all pages
        full_text = '\n\n'.join(text_parts)
        
        if not full_text.strip():
            raise FileParsingError("No text found in PDF")
        
        return full_text
        
    except Exception as e:
        # Try fallback parser
        return parse_pdf_fallback(file_data)


def parse_pdf_fallback(file_data: bytes) -> str:
    """
    Fallback PDF parser using PyPDF2
    
    Why fallback?
    - Some PDFs work better with PyPDF2
    - Redundancy = reliability
    - Better than failing completely
    """
    try:
        pdf_file = io.BytesIO(file_data)
        reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        full_text = '\n\n'.join(text_parts)
        
        if not full_text.strip():
            raise FileParsingError("Could not extract text from PDF")
        
        return full_text
        
    except Exception as e:
        raise FileParsingError(f"PDF parsing failed: {str(e)}")
```

**Explain:**
"Notice the pattern:
1. Try primary method (pdfplumber)
2. If fails, try fallback (PyPDF2)
3. If both fail, raise clear error

Why two libraries?
- pdfplumber: Better for complex layouts
- PyPDF2: Better for simple PDFs
- Together: Handle 95%+ of PDFs

The `io.BytesIO` trick:
- Converts bytes to file-like object
- Libraries expect file objects
- Works with uploaded data"

### Part 4: Word Document Parsing (5 min)

```python
def parse_docx(file_data: bytes) -> str:
    """
    Extract text from DOCX file
    
    Why python-docx?
    - Official library for .docx format
    - Handles styles, formatting
    - Reliable and well-maintained
    """
    try:
        docx_file = io.BytesIO(file_data)
        doc = Document(docx_file)
        
        # Extract paragraphs
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text)
        
        full_text = '\n'.join(text_parts)
        
        if not full_text.strip():
            raise FileParsingError("No text found in document")
        
        return full_text
        
    except Exception as e:
        raise FileParsingError(f"DOCX parsing failed: {str(e)}")
```

**Explain:**
"DOCX structure:
- Paragraphs: Main text content
- Tables: Often used in resumes
- We extract both

Why join with `\n`?
- Preserves line breaks
- Maintains structure
- Helps NLP later"

### Part 5: Main Parser Function (2 min)

```python
def parse_resume_file(file_data: bytes, filename: str) -> Tuple[str, Dict]:
    """
    Main entry point for file parsing
    
    Returns:
        Tuple of (text, metadata)
    """
    # Validate first
    validate_file(file_data, filename)
    
    # Determine file type
    ext = filename.lower().split('.')[-1]
    
    # Parse based on type
    if ext == 'pdf':
        text = parse_pdf(file_data)
    elif ext in ['doc', 'docx']:
        text = parse_docx(file_data)
    else:
        raise FileValidationError(f"Unsupported file type: {ext}")
    
    # Create metadata
    metadata = {
        'filename': filename,
        'file_type': ext,
        'file_size': len(file_data),
        'text_length': len(text),
        'word_count': len(text.split())
    }
    
    return text, metadata
```

**Explain:**
"This is our public API. Clean and simple:
- Input: file bytes + filename
- Output: text + metadata
- All complexity hidden inside

Metadata is useful for:
- Debugging
- Analytics
- User feedback"

## Testing the Parser

**Create test script:**

```python
# test_parser.py
from app.core.parser import parse_resume_file

# Test with a sample file
with open('sample_resume.pdf', 'rb') as f:
    file_data = f.read()

text, metadata = parse_resume_file(file_data, 'sample_resume.pdf')

print("Metadata:", metadata)
print("\nFirst 500 characters:")
print(text[:500])
```

## Key Concepts
1. **Validation before processing** - Fail fast
2. **Fallback mechanisms** - Reliability
3. **Clear error messages** - Debugging
4. **Metadata tracking** - Observability

## Common Issues
- **"No text extracted"**: PDF might be scanned image
- **Encoding errors**: Try different encodings
- **Memory errors**: File too large

## Transition to Module 04
"Now we have text! Next, we'll use spaCy to extract structured information: skills, experience, sections."
