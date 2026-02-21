"""
Error Handler Module for ATS Resume Scorer

This module provides comprehensive error handling functionality including:
- Custom exception classes for different error types
- Error logging for debugging
- User-friendly error message generation
- Graceful degradation helpers
- Fallback mechanism utilities

Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
"""
import logging
import traceback
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union
from functools import wraps
from datetime import datetime
from enum import Enum
import os
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger('ats_resume_scorer')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(LOG_DIR,
    f"ats_scorer_{datetime.now().strftime('%Y%m%d')}.log"))
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
file_handler.setFormatter(file_formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class ErrorSeverity(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class ErrorCategory(Enum):
    FILE_UPLOAD = 'file_upload'
    FILE_PARSING = 'file_parsing'
    TEXT_EXTRACTION = 'text_extraction'
    NLP_PROCESSING = 'nlp_processing'
    MODEL_LOADING = 'model_loading'
    GRAMMAR_CHECK = 'grammar_check'
    SKILL_VALIDATION = 'skill_validation'
    LOCATION_DETECTION = 'location_detection'
    SCORING = 'scoring'
    JD_COMPARISON = 'jd_comparison'
    REPORT_GENERATION = 'report_generation'
    AUTHENTICATION = 'authentication'
    UNKNOWN = 'unknown'


class ATSBaseError(Exception):

    def __init__(self, message: str, user_message: Optional[str]=None,
        category: ErrorCategory=ErrorCategory.UNKNOWN, severity:
        ErrorSeverity=ErrorSeverity.MEDIUM, suggestions: Optional[List[str]
        ]=None, original_error: Optional[Exception]=None):
        super().__init__(message)
        self.message = message
        self.user_message = user_message or self._generate_user_message()
        self.category = category
        self.severity = severity
        self.suggestions = suggestions or []
        self.original_error = original_error
        self.timestamp = datetime.now()
        self._log_error()

    def _generate_user_message(self) ->str:
        return 'An error occurred. Please try again.'

    def _log_error(self):
        log_message = f'{self.category.value}: {self.message}'
        if self.original_error:
            log_message += (
                f' | Original: {type(self.original_error).__name__}: {str(self.original_error)}'
                )
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)


class FileUploadError(ATSBaseError):

    def __init__(self, message: str, user_message: Optional[str]=None,
        suggestions: Optional[List[str]]=None, original_error: Optional[
        Exception]=None):
        default_suggestions = [
            'Ensure your file is in PDF, DOC, or DOCX format',
            'Check that the file size is under 5MB',
            'Try re-saving the document and uploading again']
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.FILE_UPLOAD, severity=ErrorSeverity.
            MEDIUM, suggestions=suggestions or default_suggestions,
            original_error=original_error)

    def _generate_user_message(self) ->str:
        return (
            'There was a problem with your uploaded file. Please check the file format and try again.'
            )


class FileParsingError(ATSBaseError):

    def __init__(self, message: str, user_message: Optional[str]=None,
        suggestions: Optional[List[str]]=None, original_error: Optional[
        Exception]=None):
        default_suggestions = ['Try converting your document to PDF format',
            'Ensure the document is not password-protected',
            'Check that the document contains selectable text (not scanned images)'
            ]
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.FILE_PARSING, severity=ErrorSeverity.
            MEDIUM, suggestions=suggestions or default_suggestions,
            original_error=original_error)

    def _generate_user_message(self) ->str:
        return (
            'Could not extract text from your file. The document may be corrupted or in an unsupported format.'
            )


class TextExtractionError(ATSBaseError):

    def __init__(self, message: str, user_message: Optional[str]=None,
        suggestions: Optional[List[str]]=None, original_error: Optional[
        Exception]=None):
        default_suggestions = [
            'Ensure your PDF contains selectable text, not scanned images',
            'Try converting the document to DOCX format',
            'Use a PDF with embedded text rather than image-based content']
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.TEXT_EXTRACTION, severity=ErrorSeverity.
            MEDIUM, suggestions=suggestions or default_suggestions,
            original_error=original_error)

    def _generate_user_message(self) ->str:
        return (
            'No text could be extracted from your document. Please ensure it contains readable text.'
            )


class ModelLoadError(ATSBaseError):

    def __init__(self, message: str, model_name: str='unknown',
        user_message: Optional[str]=None, suggestions: Optional[List[str]]=
        None, original_error: Optional[Exception]=None):
        self.model_name = model_name
        default_suggestions = self._get_model_suggestions(model_name)
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.MODEL_LOADING, severity=ErrorSeverity.
            HIGH, suggestions=suggestions or default_suggestions,
            original_error=original_error)

    def _get_model_suggestions(self, model_name: str) ->List[str]:
        if 'spacy' in model_name.lower() or 'en_core' in model_name.lower():
            return [f'Run: python -m spacy download {model_name}',
                'Try: pip install spacy --upgrade',
                'Ensure you have sufficient disk space for model files']
        elif 'sentence' in model_name.lower(
            ) or 'transformer' in model_name.lower():
            return ['Run: pip install sentence-transformers --upgrade',
                'Ensure internet access for first-time model download',
                'Check disk space (~100MB required for model cache)']
        elif 'language' in model_name.lower() or 'tool' in model_name.lower():
            return ['Run: pip install language-tool-python --upgrade',
                'Ensure Java is installed (required by LanguageTool)',
                'Check if port 8081 is available',
                'Try restarting the application']
        else:
            return ['Check your internet connection',
                'Ensure sufficient disk space',
                'Try restarting the application']

    def _generate_user_message(self) ->str:
        return (
            f'Failed to load the {self.model_name} model. Please check the troubleshooting steps.'
            )


class NLPProcessingError(ATSBaseError):

    def __init__(self, message: str, user_message: Optional[str]=None,
        suggestions: Optional[List[str]]=None, original_error: Optional[
        Exception]=None):
        default_suggestions = [
            'Try uploading a different version of your resume',
            'Ensure your resume contains standard text formatting',
            'Contact support if the problem persists']
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.NLP_PROCESSING, severity=ErrorSeverity.
            MEDIUM, suggestions=suggestions or default_suggestions,
            original_error=original_error)

    def _generate_user_message(self) ->str:
        return (
            'There was an issue processing your resume text. Please try again.'
            )


class GrammarCheckError(ATSBaseError):

    def __init__(self, message: str, user_message: Optional[str]=None,
        suggestions: Optional[List[str]]=None, original_error: Optional[
        Exception]=None):
        default_suggestions = ['Grammar checking is temporarily unavailable',
            'Other analysis features will continue to work',
            'Try restarting the application if the issue persists']
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.GRAMMAR_CHECK, severity=ErrorSeverity.
            LOW, suggestions=suggestions or default_suggestions,
            original_error=original_error)

    def _generate_user_message(self) ->str:
        return (
            'Grammar checking is temporarily unavailable. Other analysis features will continue.'
            )


class ScoringError(ATSBaseError):

    def __init__(self, message: str, user_message: Optional[str]=None,
        suggestions: Optional[List[str]]=None, original_error: Optional[
        Exception]=None):
        default_suggestions = ['Try uploading your resume again',
            'Ensure your resume has standard sections',
            'Contact support if the problem persists']
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.SCORING, severity=ErrorSeverity.HIGH,
            suggestions=suggestions or default_suggestions, original_error=
            original_error)

    def _generate_user_message(self) ->str:
        return 'Could not calculate your resume score. Please try again.'


class ReportGenerationError(ATSBaseError):

    def __init__(self, message: str, user_message: Optional[str]=None,
        suggestions: Optional[List[str]]=None, original_error: Optional[
        Exception]=None):
        default_suggestions = ['Try downloading the summary text instead',
            'Refresh the page and try again',
            'Contact support if the problem persists']
        super().__init__(message=message, user_message=user_message,
            category=ErrorCategory.REPORT_GENERATION, severity=
            ErrorSeverity.LOW, suggestions=suggestions or
            default_suggestions, original_error=original_error)

    def _generate_user_message(self) ->str:
        return (
            'Could not generate the report. Please try an alternative download option.'
            )


def log_error(error: Exception, context: Optional[str]=None, category:
    ErrorCategory=ErrorCategory.UNKNOWN, include_traceback: bool=True) ->None:
    error_info = {'type': type(error).__name__, 'message': str(error),
        'category': category.value, 'context': context, 'timestamp':
        datetime.now().isoformat()}
    log_message = (
        f"Error in {context or 'unknown context'}: {error_info['type']}: {error_info['message']}"
        )
    if include_traceback:
        tb = traceback.format_exc()
        logger.error(f'{log_message}\nTraceback:\n{tb}')
    else:
        logger.error(log_message)


def log_warning(message: str, context: Optional[str]=None) ->None:
    log_message = f'{context}: {message}' if context else message
    logger.warning(log_message)


def log_info(message: str, context: Optional[str]=None) ->None:
    log_message = f'{context}: {message}' if context else message
    logger.info(log_message)


def get_user_friendly_message(error: Exception, category: Optional[
    ErrorCategory]=None) ->str:
    if isinstance(error, ATSBaseError):
        return error.user_message
    category_messages = {ErrorCategory.FILE_UPLOAD:
        'There was a problem with your uploaded file. Please check the format and try again.'
        , ErrorCategory.FILE_PARSING:
        'Could not read your file. Please try a different format (PDF or DOCX).'
        , ErrorCategory.TEXT_EXTRACTION:
        'No text could be extracted from your document. Please ensure it contains readable text.'
        , ErrorCategory.NLP_PROCESSING:
        'There was an issue analyzing your resume. Please try again.',
        ErrorCategory.MODEL_LOADING:
        'A required component failed to load. Please refresh the page and try again.'
        , ErrorCategory.GRAMMAR_CHECK:
        'Grammar checking is temporarily unavailable. Other features will continue to work.'
        , ErrorCategory.SKILL_VALIDATION:
        'Could not validate skills. Other analysis features will continue.',
        ErrorCategory.LOCATION_DETECTION:
        'Location detection encountered an issue. Other analysis features will continue.'
        , ErrorCategory.SCORING:
        'Could not calculate your score. Please try again.', ErrorCategory.
        JD_COMPARISON:
        'Could not compare with job description. Please try again.',
        ErrorCategory.REPORT_GENERATION:
        'Could not generate the report. Please try an alternative download option.'
        , ErrorCategory.AUTHENTICATION:
        'Authentication failed. Please log in again.', ErrorCategory.
        UNKNOWN:
        'An unexpected error occurred. Please try again or contact support.'}
    if category:
        return category_messages.get(category, category_messages[
            ErrorCategory.UNKNOWN])
    error_type = type(error).__name__.lower()
    if 'file' in error_type or 'upload' in error_type:
        return category_messages[ErrorCategory.FILE_UPLOAD]
    elif 'parse' in error_type or 'extract' in error_type:
        return category_messages[ErrorCategory.FILE_PARSING]
    elif 'model' in error_type or 'load' in error_type:
        return category_messages[ErrorCategory.MODEL_LOADING]
    elif 'auth' in error_type or 'login' in error_type:
        return category_messages[ErrorCategory.AUTHENTICATION]
    return category_messages[ErrorCategory.UNKNOWN]


def get_error_suggestions(error: Exception, category: Optional[
    ErrorCategory]=None) ->List[str]:
    if isinstance(error, ATSBaseError):
        return error.suggestions
    category_suggestions = {ErrorCategory.FILE_UPLOAD: [
        'Ensure your file is in PDF, DOC, or DOCX format',
        'Check that the file size is under 5MB',
        'Try re-saving the document and uploading again'], ErrorCategory.
        FILE_PARSING: ['Try converting your document to PDF format',
        'Ensure the document is not password-protected',
        'Check that the document contains selectable text'], ErrorCategory.
        MODEL_LOADING: ['Refresh the page and try again',
        'Check your internet connection',
        'Contact support if the problem persists'], ErrorCategory.UNKNOWN:
        ['Try refreshing the page', 'Upload your file again',
        'Contact support if the problem persists']}
    if category:
        return category_suggestions.get(category, category_suggestions[
            ErrorCategory.UNKNOWN])
    return category_suggestions[ErrorCategory.UNKNOWN]


T = TypeVar('T')


def with_fallback(primary_func: Callable[..., T], fallback_func: Callable[
    ..., T], *args, error_category: ErrorCategory=ErrorCategory.UNKNOWN,
    log_fallback: bool=True, **kwargs) ->Tuple[T, bool]:
    try:
        result = primary_func(*args, **kwargs)
        return result, False
    except Exception as primary_error:
        if log_fallback:
            log_warning(
                f'Primary method failed, using fallback: {str(primary_error)}',
                context=error_category.value)
        try:
            result = fallback_func(*args, **kwargs)
            return result, True
        except Exception as fallback_error:
            log_error(fallback_error, context=
                f'{error_category.value}_fallback', category=error_category)
            raise


def safe_execute(func: Callable[..., T], default_value: T, *args,
    error_category: ErrorCategory=ErrorCategory.UNKNOWN, log_error_flag:
    bool=True, **kwargs) ->Tuple[T, Optional[Exception]]:
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        if log_error_flag:
            log_error(e, context=error_category.value, category=error_category)
        return default_value, e


def graceful_degradation(component_name: str, error_category: ErrorCategory
    =ErrorCategory.UNKNOWN):

    def decorator(func: Callable[..., Dict]) ->Callable[..., Dict]:

        @wraps(func)
        def wrapper(*args, **kwargs) ->Dict:
            try:
                result = func(*args, **kwargs)
                result['_component_status'] = 'success'
                return result
            except Exception as e:
                log_error(e, context=component_name, category=error_category)
                return {'_component_status': 'failed', '_component_name':
                    component_name, '_error_message':
                    get_user_friendly_message(e, error_category),
                    '_error_suggestions': get_error_suggestions(e,
                    error_category)}
        return wrapper
    return decorator


class AnalysisResult:

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, Dict] = {}
        self.warnings: List[str] = []
        self.success = True

    def add_result(self, component: str, result: Any) ->None:
        self.results[component] = result

    def add_error(self, component: str, error: Exception, category:
        ErrorCategory=ErrorCategory.UNKNOWN) ->None:
        self.errors[component] = {'message': get_user_friendly_message(
            error, category), 'suggestions': get_error_suggestions(error,
            category), 'category': category.value}
        log_error(error, context=component, category=category)

    def add_warning(self, message: str) ->None:
        self.warnings.append(message)
        log_warning(message)

    def has_critical_errors(self) ->bool:
        critical_categories = {ErrorCategory.FILE_UPLOAD.value,
            ErrorCategory.FILE_PARSING.value, ErrorCategory.TEXT_EXTRACTION
            .value}
        return any(err.get('category') in critical_categories for err in
            self.errors.values())

    def get_failed_components(self) ->List[str]:
        return list(self.errors.keys())

    def get_successful_components(self) ->List[str]:
        return list(self.results.keys())

    def to_dict(self) ->Dict:
        return {'results': self.results, 'errors': self.errors, 'warnings':
            self.warnings, 'success': not self.has_critical_errors(),
            'failed_components': self.get_failed_components(),
            'successful_components': self.get_successful_components()}


def get_default_grammar_results() ->Dict:
    return {'total_errors': 0, 'critical_errors': [], 'moderate_errors': [],
        'minor_errors': [], 'grammar_score': 100, 'penalty_applied': 0,
        'error_free_percentage': 100, '_component_status': 'unavailable',
        '_note': 'Grammar checking was unavailable. Results may be incomplete.'
        }


def get_default_location_results() ->Dict:
    return {'location_found': False, 'detected_locations': [],
        'privacy_risk': 'unknown', 'recommendations': [
        'Location detection was unavailable.'], 'penalty_applied': 0,
        '_component_status': 'unavailable', '_note':
        'Location detection was unavailable. Results may be incomplete.'}


def get_default_skill_validation_results() ->Dict:
    return {'validated_skills': [], 'unvalidated_skills': [],
        'validation_percentage': 0.0, 'skill_project_mapping': {},
        'validation_score': 0.0, '_component_status': 'unavailable',
        '_note': 'Skill validation was unavailable. Results may be incomplete.'
        }


def get_default_jd_comparison_results() ->Dict:
    return {'semantic_similarity': 0.0, 'matched_keywords': [],
        'missing_keywords': [], 'skills_gap': [], 'match_percentage': 0.0,
        '_component_status': 'unavailable', '_note':
        'Job description comparison was unavailable.'}


def format_error_for_display(error: Exception, category: Optional[
    ErrorCategory]=None, show_suggestions: bool=True) ->Dict[str, Any]:
    result = {'message': get_user_friendly_message(error, category),
        'severity': 'error'}
    if show_suggestions:
        result['suggestions'] = get_error_suggestions(error, category)
    if isinstance(error, ATSBaseError):
        result['severity'] = error.severity.value
    return result


def get_component_status_message(results: Dict) ->Optional[str]:
    status = results.get('_component_status')
    if status == 'unavailable':
        note = results.get('_note', 'This component was unavailable.')
        return f'⚠️ {note}'
    elif status == 'failed':
        message = results.get('_error_message',
            'This component encountered an error.')
        return f'❌ {message}'
    return None
