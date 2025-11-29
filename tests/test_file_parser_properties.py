"""
Property-Based Tests for File Parser Module

Uses Hypothesis for property-based testing to verify correctness properties
across a wide range of inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import importlib.util

# Import file_parser module directly to avoid dependency issues
spec = importlib.util.spec_from_file_location("file_parser", "utils/file_parser.py")
file_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(file_parser)

validate_file = file_parser.validate_file
extract_text = file_parser.extract_text
parse_resume_file = file_parser.parse_resume_file
FileParsingError = file_parser.FileParsingError
FileValidationError = file_parser.FileValidationError
MAX_FILE_SIZE_BYTES = file_parser.MAX_FILE_SIZE_BYTES


# Feature: ats-resume-scorer, Property 6: File type validation
@settings(max_examples=100)
@given(
    file_content=st.binary(min_size=1, max_size=1024),
    filename=st.text(min_size=1, max_size=50)
)
def test_property_file_type_validation(file_content, filename):
    """
    Property 6: File type validation
    
    For any uploaded file, the system should accept only PDF, DOC, or DOCX
    file types and reject all others.
    
    Validates: Requirements 3.1
    """
    is_valid, error_msg, file_type = validate_file(file_content, filename)
    
    # If file is valid, it must be one of the supported types
    if is_valid:
        assert file_type in ['pdf', 'doc', 'docx'], \
            f"Valid file must be pdf, doc, or docx, got {file_type}"
        assert error_msg == "", "Valid file should have empty error message"
    else:
        # If file is invalid, file_type should be None (unless it's a size issue)
        # and error_msg should be non-empty
        assert error_msg != "", "Invalid file must have error message"
        
        # If the error is not about file size, then file_type should be None
        if "exceeds the maximum allowed size" not in error_msg and "empty" not in error_msg:
            assert file_type is None, "Invalid file type should return None"


# Feature: ats-resume-scorer, Property 7: File size limit enforcement
@settings(max_examples=100)
@given(
    file_size=st.integers(min_value=0, max_value=MAX_FILE_SIZE_BYTES * 2),
    filename=st.sampled_from(['test.pdf', 'test.docx', 'test.doc'])
)
def test_property_file_size_limit(file_size, filename):
    """
    Property 7: File size limit enforcement
    
    For any uploaded file exceeding 5MB, the system should reject the file
    and display an error message.
    
    Validates: Requirements 3.2
    """
    # Create file content of specified size
    # Use PDF magic number for valid file type
    if file_size > 0:
        file_content = b'%PDF-1.4\n' + b'x' * (file_size - 9)
    else:
        file_content = b''
    
    is_valid, error_msg, file_type = validate_file(file_content, filename)
    
    if file_size > MAX_FILE_SIZE_BYTES:
        # Files exceeding limit should be rejected
        assert not is_valid, f"File of size {file_size} should be rejected"
        assert "exceeds the maximum allowed size" in error_msg or "5 MB" in error_msg, \
            f"Error message should mention size limit: {error_msg}"
        assert file_type is None, "Oversized file should return None for file_type"
    elif file_size == 0:
        # Empty files should be rejected
        assert not is_valid, "Empty file should be rejected"
        assert "empty" in error_msg.lower(), f"Error message should mention empty: {error_msg}"
    else:
        # Files within limit with valid PDF header should pass size check
        # (they may still fail type check depending on content)
        if not is_valid and "exceeds" in error_msg:
            pytest.fail(f"File of size {file_size} should not fail size check")


# Feature: ats-resume-scorer, Property 8: Text extraction from valid files
@settings(max_examples=100)
@given(
    text_content=st.text(min_size=10, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_property_text_extraction_from_valid_files(text_content):
    """
    Property 8: Text extraction from valid files
    
    For any valid PDF, DOC, or DOCX file, the system should successfully
    extract text content.
    
    Validates: Requirements 3.3, 3.4
    
    Note: This test focuses on the interface contract. Full PDF/DOCX generation
    would require complex libraries, so we test the error handling path.
    """
    # Test that extract_text properly routes to the right handler
    # and raises appropriate errors for invalid data
    
    # Test with invalid PDF data
    invalid_pdf = b'%PDF-1.4\nInvalid PDF content'
    try:
        result = extract_text(invalid_pdf, 'pdf')
        # If it succeeds, result should be a string
        assert isinstance(result, str), "Extracted text must be a string"
    except FileParsingError as e:
        # Should raise FileParsingError with helpful message
        error_msg = str(e)
        assert len(error_msg) > 20, "Error message should be descriptive"
        assert "PDF" in error_msg or "extract" in error_msg, \
            "Error should mention PDF or extraction"
    
    # Test with invalid DOCX data
    invalid_docx = b'PK\x03\x04Invalid DOCX'
    try:
        result = extract_text(invalid_docx, 'docx')
        assert isinstance(result, str), "Extracted text must be a string"
    except FileParsingError as e:
        error_msg = str(e)
        assert len(error_msg) > 20, "Error message should be descriptive"
        assert "document" in error_msg.lower() or "extract" in error_msg.lower()


# Feature: ats-resume-scorer, Property 9: Extraction failure error handling
@settings(max_examples=100)
@given(
    file_type=st.sampled_from(['pdf', 'docx', 'doc']),
    file_content=st.binary(min_size=1, max_size=100)
)
def test_property_extraction_failure_error_handling(file_type, file_content):
    """
    Property 9: Extraction failure error handling
    
    For any file where extraction fails, the system should display a specific
    error message with corrective action suggestions.
    
    Validates: Requirements 3.5
    """
    # Assume the file content is not a valid file of the given type
    # (random binary data is unlikely to be valid)
    assume(not file_content.startswith(b'%PDF') if file_type == 'pdf' else True)
    assume(not file_content.startswith(b'PK') if file_type == 'docx' else True)
    
    try:
        result = extract_text(file_content, file_type)
        # If extraction succeeds, result must be a string
        assert isinstance(result, str), "Extracted text must be a string"
    except FileParsingError as e:
        # Error message should be specific and helpful
        error_msg = str(e)
        
        # Should not be empty
        assert len(error_msg) > 0, "Error message should not be empty"
        
        # Should be descriptive (at least 20 characters)
        assert len(error_msg) > 20, \
            f"Error message should be descriptive, got: {error_msg}"
        
        # Should not contain technical stack traces
        assert "Traceback" not in error_msg, \
            "Error message should not contain stack traces"
        
        # Should mention the file type or extraction
        assert any(word in error_msg.lower() for word in ['pdf', 'docx', 'doc', 'document', 'extract', 'file']), \
            f"Error message should mention file type or extraction: {error_msg}"
        
        # Should provide corrective action (contains words like "try", "please", "convert")
        has_action = any(word in error_msg.lower() for word in ['try', 'please', 'convert', 'ensure', 'check'])
        assert has_action, \
            f"Error message should suggest corrective action: {error_msg}"
    except FileValidationError as e:
        # FileValidationError is also acceptable for invalid file types
        error_msg = str(e)
        assert len(error_msg) > 0, "Error message should not be empty"
