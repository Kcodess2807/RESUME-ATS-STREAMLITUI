# File Parser Module Implementation

## Overview
The file parser module (`utils/file_parser.py`) provides robust file validation and text extraction for the ATS Resume Scorer application.

## Features Implemented

### 1. File Validation (Requirements 3.1, 3.2, 15.1)
- **Magic number checking**: Uses `python-magic` library to detect actual file type regardless of extension
- **File size validation**: Enforces 5MB limit with clear error messages
- **Empty file detection**: Rejects empty files with helpful feedback
- **Supported formats**: PDF, DOC, DOCX

### 2. PDF Text Extraction (Requirements 3.3, 15.2)
- **Primary method**: `pdfplumber` for high-quality text extraction
- **Fallback method**: `PyPDF2` when pdfplumber fails
- **Error handling**: Clear messages for corrupted, password-protected, or image-only PDFs

### 3. DOCX Text Extraction (Requirements 3.4)
- **Paragraph extraction**: Extracts text from all paragraphs
- **Table extraction**: Extracts text from tables within the document
- **Error handling**: Handles corrupted or empty documents gracefully

### 4. DOC Format Handling (Requirements 3.4)
- **Legacy format notice**: Informs users that .doc format requires conversion
- **Helpful guidance**: Suggests converting to .docx or .pdf format

### 5. Error Handling (Requirements 3.5, 15.1, 15.2)
- **Custom exceptions**: `FileValidationError` and `FileParsingError`
- **User-friendly messages**: No technical stack traces exposed
- **Actionable feedback**: Suggests corrective actions for each error type
- **Graceful degradation**: Attempts fallback methods before failing

## API Reference

### Main Functions

#### `validate_file(file_data: bytes, filename: str) -> Tuple[bool, str, Optional[str]]`
Validates file type and size using magic number checking.

**Returns:**
- `is_valid`: True if file passes validation
- `error_message`: Error description if validation fails
- `file_type`: Detected file type ('pdf', 'doc', 'docx') or None

#### `extract_text(file_data: bytes, file_type: str) -> str`
Routes to appropriate parser based on file type.

**Raises:**
- `FileParsingError`: If text extraction fails
- `FileValidationError`: If file type is invalid

#### `parse_resume_file(file_data: bytes, filename: str) -> Tuple[str, dict]`
Complete parsing pipeline: validate and extract text.

**Returns:**
- `extracted_text`: Extracted text content
- `metadata`: Dictionary with file information

### Custom Exceptions

- **`FileValidationError`**: Raised when file validation fails (wrong type, too large, empty)
- **`FileParsingError`**: Raised when text extraction fails (corrupted, no text, etc.)

## Usage Example

```python
from utils.file_parser import parse_resume_file, FileValidationError, FileParsingError

try:
    # Read file data
    with open('resume.pdf', 'rb') as f:
        file_data = f.read()
    
    # Parse the file
    text, metadata = parse_resume_file(file_data, 'resume.pdf')
    
    print(f"Extracted {metadata['text_length']} characters")
    print(f"File type: {metadata['file_type']}")
    
except FileValidationError as e:
    print(f"Validation error: {e}")
except FileParsingError as e:
    print(f"Parsing error: {e}")
```

## Dependencies

- `pdfplumber>=0.10.0`: Primary PDF parsing
- `PyPDF2>=3.0.0`: Fallback PDF parsing
- `python-docx>=1.0.0`: DOCX parsing
- `python-magic>=0.4.27`: File type detection

## Testing

The implementation has been verified with tests covering:
- File size limit enforcement (5MB)
- Empty file detection
- PDF file validation with magic numbers
- Unsupported file type rejection
- Invalid file type handling
- Empty PDF error handling
- User-friendly error messages

All tests passed successfully.

## Requirements Coverage

✅ **Requirement 3.1**: File type validation (PDF, DOC, DOCX)
✅ **Requirement 3.2**: File size validation (5MB limit)
✅ **Requirement 3.3**: PDF text extraction
✅ **Requirement 3.4**: DOC/DOCX text extraction
✅ **Requirement 3.5**: Extraction failure error handling
✅ **Requirement 15.1**: Clear validation error messages
✅ **Requirement 15.2**: Fallback extraction attempts
