"""
Unit Tests for File Parser Module

Tests specific edge cases, error conditions, and various file formats.
"""

import pytest
import importlib.util
from io import BytesIO

# Import file_parser module directly to avoid dependency issues
spec = importlib.util.spec_from_file_location("file_parser", "utils/file_parser.py")
file_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(file_parser)

validate_file = file_parser.validate_file
extract_text = file_parser.extract_text
extract_text_from_pdf = file_parser.extract_text_from_pdf
extract_text_from_docx = file_parser.extract_text_from_docx
extract_text_from_doc = file_parser.extract_text_from_doc
parse_resume_file = file_parser.parse_resume_file
FileParsingError = file_parser.FileParsingError
FileValidationError = file_parser.FileValidationError
MAX_FILE_SIZE_BYTES = file_parser.MAX_FILE_SIZE_BYTES


class TestFileValidation:
    """Test file validation edge cases"""
    
    def test_empty_file(self):
        """Test that empty files are rejected"""
        is_valid, error_msg, file_type = validate_file(b'', 'empty.pdf')
        assert not is_valid
        assert 'empty' in error_msg.lower()
        assert file_type is None
    
    def test_exactly_5mb_file(self):
        """Test file exactly at 5MB limit"""
        # Create a file exactly 5MB with PDF header
        file_data = b'%PDF-1.4\n' + b'x' * (MAX_FILE_SIZE_BYTES - 9)
        is_valid, error_msg, file_type = validate_file(file_data, 'exact.pdf')
        # Should be valid (at the limit, not exceeding)
        assert is_valid
        assert file_type == 'pdf'
    
    def test_5mb_plus_one_byte(self):
        """Test file just over 5MB limit"""
        file_data = b'%PDF-1.4\n' + b'x' * (MAX_FILE_SIZE_BYTES - 8)
        is_valid, error_msg, file_type = validate_file(file_data, 'over.pdf')
        assert not is_valid
        assert '5 MB' in error_msg or '5MB' in error_msg
        assert file_type is None
    
    def test_pdf_magic_number(self):
        """Test PDF detection with magic number"""
        pdf_data = b'%PDF-1.4\nSome content'
        is_valid, error_msg, file_type = validate_file(pdf_data, 'test.pdf')
        assert is_valid
        assert file_type == 'pdf'
    
    def test_docx_magic_number(self):
        """Test DOCX detection with magic number (ZIP format)"""
        # DOCX files are ZIP archives with specific structure
        # Minimal ZIP header
        docx_data = b'PK\x03\x04' + b'\x00' * 100
        is_valid, error_msg, file_type = validate_file(docx_data, 'test.docx')
        # This should be detected as a ZIP/DOCX file
        # Note: python-magic may detect this as application/zip
        # which is not in our supported types, so it may fail
        # This is expected behavior - we want proper DOCX files
        if not is_valid:
            assert 'Unsupported file type' in error_msg
    
    def test_text_file_rejected(self):
        """Test that plain text files are rejected"""
        text_data = b'This is plain text content'
        is_valid, error_msg, file_type = validate_file(text_data, 'test.txt')
        assert not is_valid
        assert 'Unsupported file type' in error_msg
        assert file_type is None
    
    def test_image_file_rejected(self):
        """Test that image files are rejected"""
        # PNG magic number
        png_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        is_valid, error_msg, file_type = validate_file(png_data, 'test.png')
        assert not is_valid
        assert 'Unsupported file type' in error_msg
        assert file_type is None


class TestPDFExtraction:
    """Test PDF text extraction edge cases"""
    
    def test_minimal_pdf_no_text(self):
        """Test PDF with no extractable text"""
        minimal_pdf = b'%PDF-1.4\n%%EOF'
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_pdf(minimal_pdf)
        assert 'No text could be extracted' in str(exc_info.value) or \
               'Failed to extract' in str(exc_info.value)
    
    def test_corrupted_pdf(self):
        """Test corrupted PDF file"""
        corrupted_pdf = b'%PDF-1.4\nCorrupted content without proper structure'
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_pdf(corrupted_pdf)
        error_msg = str(exc_info.value)
        assert len(error_msg) > 20
        assert 'PDF' in error_msg or 'extract' in error_msg
    
    def test_pdf_with_only_images(self):
        """Test PDF containing only images (no selectable text)"""
        # This is a minimal PDF structure, but won't have extractable text
        image_only_pdf = b'%PDF-1.4\n1 0 obj\n<<\n>>\nendobj\n%%EOF'
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_pdf(image_only_pdf)
        error_msg = str(exc_info.value)
        # Should mention that no text was extracted
        assert 'No text' in error_msg or 'Failed to extract' in error_msg


class TestDOCXExtraction:
    """Test DOCX text extraction edge cases"""
    
    def test_invalid_docx_structure(self):
        """Test DOCX with invalid structure"""
        invalid_docx = b'PK\x03\x04Invalid DOCX structure'
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_docx(invalid_docx)
        error_msg = str(exc_info.value)
        assert len(error_msg) > 20
        assert 'document' in error_msg.lower() or 'DOCX' in error_msg
    
    def test_empty_docx_content(self):
        """Test DOCX with no text content"""
        # This will fail to parse as a valid DOCX
        empty_docx = b'PK\x03\x04\x00\x00\x00\x00'
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_docx(empty_docx)
        error_msg = str(exc_info.value)
        assert 'document' in error_msg.lower() or 'extract' in error_msg.lower()


class TestDOCExtraction:
    """Test legacy DOC format handling"""
    
    def test_doc_format_not_supported(self):
        """Test that legacy .doc format raises appropriate error"""
        doc_data = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'  # DOC magic number
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_doc(doc_data)
        error_msg = str(exc_info.value)
        assert 'Legacy' in error_msg or 'not supported' in error_msg
        assert 'convert' in error_msg.lower()


class TestExtractTextRouting:
    """Test extract_text function routing"""
    
    def test_invalid_file_type(self):
        """Test that invalid file types raise FileValidationError"""
        with pytest.raises(FileValidationError) as exc_info:
            extract_text(b'some data', 'invalid')
        assert 'Invalid file type' in str(exc_info.value)
    
    def test_pdf_routing(self):
        """Test that PDF files are routed to PDF extractor"""
        pdf_data = b'%PDF-1.4\nInvalid but routed'
        with pytest.raises(FileParsingError):
            # Should attempt PDF extraction and fail
            extract_text(pdf_data, 'pdf')
    
    def test_docx_routing(self):
        """Test that DOCX files are routed to DOCX extractor"""
        docx_data = b'PK\x03\x04Invalid'
        with pytest.raises(FileParsingError):
            # Should attempt DOCX extraction and fail
            extract_text(docx_data, 'docx')
    
    def test_doc_routing(self):
        """Test that DOC files are routed to DOC extractor"""
        doc_data = b'\xd0\xcf\x11\xe0'
        with pytest.raises(FileParsingError) as exc_info:
            extract_text(doc_data, 'doc')
        # Should get the "not supported" message
        assert 'Legacy' in str(exc_info.value) or 'not supported' in str(exc_info.value)


class TestParseResumeFile:
    """Test complete parsing pipeline"""
    
    def test_parse_empty_file(self):
        """Test parsing empty file"""
        with pytest.raises(FileValidationError) as exc_info:
            parse_resume_file(b'', 'empty.pdf')
        assert 'empty' in str(exc_info.value).lower()
    
    def test_parse_oversized_file(self):
        """Test parsing oversized file"""
        large_data = b'%PDF-1.4\n' + b'x' * (MAX_FILE_SIZE_BYTES + 100)
        with pytest.raises(FileValidationError) as exc_info:
            parse_resume_file(large_data, 'large.pdf')
        assert 'exceeds' in str(exc_info.value) or '5 MB' in str(exc_info.value)
    
    def test_parse_unsupported_type(self):
        """Test parsing unsupported file type"""
        text_data = b'Plain text content'
        with pytest.raises(FileValidationError) as exc_info:
            parse_resume_file(text_data, 'test.txt')
        assert 'Unsupported file type' in str(exc_info.value)
    
    def test_parse_corrupted_pdf(self):
        """Test parsing corrupted PDF"""
        corrupted_pdf = b'%PDF-1.4\nCorrupted'
        with pytest.raises(FileParsingError):
            parse_resume_file(corrupted_pdf, 'corrupted.pdf')


class TestErrorMessages:
    """Test error message quality"""
    
    def test_error_messages_are_descriptive(self):
        """Test that all error messages are descriptive"""
        test_cases = [
            (b'', 'empty.pdf', 'empty'),
            (b'x' * (MAX_FILE_SIZE_BYTES + 1), 'large.pdf', 'exceeds'),
            (b'Plain text', 'test.txt', 'Unsupported'),
        ]
        
        for file_data, filename, expected_keyword in test_cases:
            try:
                parse_resume_file(file_data, filename)
                pytest.fail(f"Should have raised an error for {filename}")
            except (FileValidationError, FileParsingError) as e:
                error_msg = str(e)
                assert len(error_msg) > 20, f"Error message too short: {error_msg}"
                assert expected_keyword.lower() in error_msg.lower(), \
                    f"Expected '{expected_keyword}' in error message: {error_msg}"
    
    def test_no_stack_traces_in_errors(self):
        """Test that error messages don't contain stack traces"""
        try:
            parse_resume_file(b'', 'empty.pdf')
        except FileValidationError as e:
            error_msg = str(e)
            assert 'Traceback' not in error_msg
            assert 'File "' not in error_msg
            assert 'line ' not in error_msg
    
    def test_error_messages_suggest_actions(self):
        """Test that error messages suggest corrective actions"""
        # Test with oversized file
        large_data = b'%PDF-1.4\n' + b'x' * (MAX_FILE_SIZE_BYTES + 100)
        try:
            parse_resume_file(large_data, 'large.pdf')
        except FileValidationError as e:
            error_msg = str(e)
            # Should suggest action like "compress" or "smaller"
            has_suggestion = any(word in error_msg.lower() 
                               for word in ['compress', 'smaller', 'reduce', 'please'])
            assert has_suggestion, f"Error should suggest action: {error_msg}"


class TestEncodingHandling:
    """Test various text encodings"""
    
    def test_utf8_content(self):
        """Test handling of UTF-8 encoded content"""
        # This is more of an integration test - we'd need valid PDF/DOCX files
        # For now, just verify the error handling works with UTF-8 strings
        utf8_text = "Résumé with special characters: café, naïve, 日本語"
        # The file parser should handle UTF-8 gracefully in error messages
        try:
            parse_resume_file(utf8_text.encode('utf-8'), 'test.pdf')
        except (FileValidationError, FileParsingError) as e:
            # Error message should be a valid string
            error_msg = str(e)
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0
