"""
Grammar Checker Module
Handles grammar and spelling checking for resume text using LanguageTool
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional

# Try to import language_tool_python, but make it optional for cloud deployment
try:
    import language_tool_python
    from language_tool_python import Match
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False
    Match = None  # type: ignore


# Technical terms whitelist to avoid false positives
TECHNICAL_TERMS_WHITELIST = {
    # Programming languages
    'python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 'golang', 'rust',
    'kotlin', 'swift', 'php', 'ruby', 'scala', 'perl', 'haskell', 'elixir',
    'dart', 'lua', 'r', 'matlab', 'fortran', 'cobol', 'lisp', 'clojure',
    
    # Frameworks and libraries
    'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'nodejs', 'express',
    'spring', 'springboot', 'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy',
    'scikit', 'matplotlib', 'seaborn', 'jquery', 'bootstrap', 'tailwind',
    'nextjs', 'nuxt', 'svelte', 'flutter', 'reactnative', 'ionic', 'xamarin',
    'streamlit', 'gradio', 'fastai', 'huggingface', 'langchain', 'opencv',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
    'dynamodb', 'firestore', 'sqlite', 'mariadb', 'neo4j', 'couchdb',
    'supabase', 'planetscale', 'cockroachdb', 'timescaledb', 'influxdb',
    
    # Cloud and DevOps
    'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'jenkins', 'gitlab', 'github',
    'terraform', 'ansible', 'circleci', 'travis', 'heroku', 'netlify', 'vercel',
    'digitalocean', 'linode', 'vultr', 'cloudflare', 'nginx', 'apache',
    
    # Tools and technologies
    'git', 'jira', 'confluence', 'slack', 'vscode', 'intellij', 'pycharm',
    'postman', 'swagger', 'graphql', 'restful', 'api', 'sdk', 'cli', 'gui',
    'oauth', 'jwt', 'ssl', 'tls', 'http', 'https', 'tcp', 'udp', 'dns',
    'colab', 'jupyter', 'kaggle', 'databricks', 'snowflake', 'airflow',
    'mlflow', 'kubeflow', 'sagemaker', 'vertex', 'openai', 'anthropic',
    
    # Methodologies and concepts
    'agile', 'scrum', 'kanban', 'devops', 'cicd', 'microservices', 'serverless',
    'frontend', 'backend', 'fullstack', 'ui', 'ux', 'api', 'seo', 'sso',
    'mlops', 'dataops', 'gitops', 'devsecops', 'finops',
    
    # Common tech abbreviations
    'html', 'css', 'json', 'xml', 'yaml', 'sql', 'nosql', 'orm', 'mvc', 'mvvm',
    'crud', 'rest', 'soap', 'grpc', 'websocket', 'cdn', 'vpc', 'ec2', 's3',
    'rds', 'lambda', 'iam', 'vpc', 'elb', 'alb', 'nlb', 'cloudfront', 'route53',
    'llm', 'nlp', 'cv', 'ml', 'ai', 'dl', 'rl', 'gan', 'cnn', 'rnn', 'lstm',
    'bert', 'gpt', 'rag', 'etl', 'elt', 'olap', 'oltp', 'hdfs', 'spark',
}

# Patterns that indicate proper nouns (should not be flagged)
PROPER_NOUN_PATTERNS = {
    # Common Indian university abbreviations
    'ggsipu', 'iit', 'nit', 'iiit', 'bits', 'vit', 'srm', 'manipal', 'amity',
    'du', 'jnu', 'bhu', 'iim', 'ism', 'isb', 'xlri', 'fms', 'iift', 'nmims',
    
    # Common US university abbreviations
    'mit', 'stanford', 'caltech', 'cmu', 'ucla', 'ucsd', 'ucb', 'usc', 'nyu',
    
    # Common certifications
    'pmp', 'cka', 'ckad', 'cks', 'ccna', 'ccnp', 'cissp', 'ceh', 'oscp',
}


@st.cache_resource
def load_grammar_checker(language: str = "en-US") -> Optional[object]:
    """
    Load and cache LanguageTool for grammar checking.
    
    Args:
        language: Language code for grammar checking (default: en-US)
        
    Returns:
        Loaded LanguageTool object, or None if not available
        
    Validates:
        - Requirements 14.3: Initialize LanguageTool locally
        - Requirements 15.5: Provide troubleshooting steps on failure
    """
    if not LANGUAGE_TOOL_AVAILABLE:
        return None
        
    try:
        tool = language_tool_python.LanguageTool(language)
        return tool
    except Exception as e:
        # Log warning but don't crash - grammar checking is optional
        st.warning(
            "Grammar checking is unavailable (requires Java). "
            "Other features will work normally."
        )
        return None


def is_technical_term(word: str) -> bool:
    """
    Check if a word is a technical term that should be whitelisted.
    
    Args:
        word: Word to check
        
    Returns:
        True if word is in technical terms whitelist
    """
    return word.lower() in TECHNICAL_TERMS_WHITELIST


def categorize_error(error) -> str:
    """
    Categorize a grammar error as critical, moderate, or minor.
    
    Critical errors:
    - Spelling mistakes in common words
    - Subject-verb agreement
    - Wrong verb tense
    - Incorrect word usage
    
    Moderate errors:
    - Punctuation issues
    - Capitalization errors
    - Missing articles
    - Redundant phrases
    
    Minor errors:
    - Style suggestions
    - Whitespace issues
    - Formatting suggestions
    
    Args:
        error: LanguageTool Match object
        
    Returns:
        Category string: "critical", "moderate", or "minor"
    """
    rule_id = error.rule_id.upper()
    category = error.category.upper()
    
    # Critical errors
    critical_patterns = [
        'MORFOLOGIK_RULE',  # Spelling errors
        'AGREEMENT',  # Subject-verb agreement
        'VERB_FORM',  # Wrong verb form
        'CONFUSION',  # Confused words (their/there/they're)
        'WRONG_WORD',  # Wrong word usage
        'GRAMMAR',  # General grammar issues
    ]
    
    for pattern in critical_patterns:
        if pattern in rule_id or pattern in category:
            return "critical"
    
    # Moderate errors
    moderate_patterns = [
        'PUNCTUATION',  # Punctuation issues
        'CAPITALIZATION',  # Capitalization errors
        'ARTICLE',  # Missing or wrong articles
        'REDUNDANCY',  # Redundant phrases
        'COMMA',  # Comma usage
        'APOSTROPHE',  # Apostrophe usage
    ]
    
    for pattern in moderate_patterns:
        if pattern in rule_id or pattern in category:
            return "moderate"
    
    # Everything else is minor (style, whitespace, etc.)
    return "minor"


def filter_technical_term_errors(errors: List, text: str) -> List:
    """
    Filter out errors related to technical terms in the whitelist.
    
    Args:
        errors: List of LanguageTool Match objects
        text: Original text being checked
        
    Returns:
        Filtered list of errors
    """
    filtered_errors = []
    
    for error in errors:
        # Get the word that triggered the error
        error_start = error.offset
        error_end = error.offset + error.error_length
        error_word = text[error_start:error_end]
        
        # Skip if it's a technical term
        if is_technical_term(error_word):
            continue
            
        filtered_errors.append(error)
    
    return filtered_errors


def extract_error_context(text: str, error, context_chars: int = 50) -> str:
    """
    Extract context around an error for display.
    
    Args:
        text: Full text
        error: LanguageTool Match object
        context_chars: Number of characters to show before and after error
        
    Returns:
        Context string with error highlighted
    """
    start = max(0, error.offset - context_chars)
    end = min(len(text), error.offset + error.error_length + context_chars)
    
    context = text[start:end]
    
    # Add ellipsis if truncated
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context


def _perform_grammar_check(
    text: str,
    language_tool
) -> Dict:
    """
    Internal function to perform grammar check.
    
    Args:
        text: Text to check
        language_tool: LanguageTool instance
        
    Returns:
        Dictionary containing grammar check results
    """
    # Check for errors
    matches = language_tool.check(text)
    
    # Filter out technical term false positives
    matches = filter_technical_term_errors(matches, text)
    
    # Categorize errors
    critical_errors = []
    moderate_errors = []
    minor_errors = []
    
    for error in matches:
        category = categorize_error(error)
        
        error_detail = {
            'message': error.message,
            'context': extract_error_context(text, error),
            'suggestions': error.replacements[:3] if error.replacements else [],
            'rule_id': error.rule_id,
            'offset': error.offset,
            'error_length': error.error_length,
            'error_text': text[error.offset:error.offset + error.error_length]
        }
        
        if category == "critical":
            critical_errors.append(error_detail)
        elif category == "moderate":
            moderate_errors.append(error_detail)
        else:
            minor_errors.append(error_detail)
    
    # Calculate penalty
    penalty = calculate_grammar_penalty({
        'critical_errors': critical_errors,
        'moderate_errors': moderate_errors,
        'minor_errors': minor_errors
    })
    
    # Calculate error-free percentage
    total_errors = len(critical_errors) + len(moderate_errors) + len(minor_errors)
    word_count = len(text.split())
    error_free_percentage = max(0, 100 - (total_errors / max(word_count, 1) * 100))
    
    return {
        'total_errors': total_errors,
        'critical_errors': critical_errors,
        'moderate_errors': moderate_errors,
        'minor_errors': minor_errors,
        'grammar_score': max(0, 100 - penalty),  # Base score of 100 minus penalty
        'penalty_applied': penalty,
        'error_free_percentage': round(error_free_percentage, 2)
    }


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_grammar_check(text_hash: str, text: str, _language_tool) -> Dict:
    """
    Cached version of grammar check.
    
    Args:
        text_hash: Hash of text content for cache key
        text: Text to check
        _language_tool: LanguageTool instance (excluded from hash)
        
    Returns:
        Dictionary containing grammar check results
        
    Validates:
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    return _perform_grammar_check(text, _language_tool)


def check_grammar_and_spelling(
    text: str,
    language_tool = None,
    use_cache: bool = True
) -> Dict:
    """
    Perform comprehensive grammar and spelling check on text.
    
    Args:
        text: Text to check
        language_tool: Optional pre-loaded LanguageTool instance
        use_cache: Whether to use caching for results (default: True)
        
    Returns:
        Dictionary containing:
        - total_errors: Total number of errors
        - critical_errors: List of critical error details
        - moderate_errors: List of moderate error details
        - minor_errors: List of minor error details
        - grammar_score: Score after applying penalties
        - penalty_applied: Total penalty points
        - error_free_percentage: Percentage of text without errors
        
    Validates:
        - Requirements 7.1, 7.2, 7.3: Detect spelling, grammar, punctuation errors
        - Requirements 7.4: Categorize errors by severity
        - Requirements 7.5: Provide correction suggestions
        - Requirements 7.6: Calculate grammar penalty
        - Requirements 16.1: Cache expensive computations
        - Requirements 16.2: Reuse cached results for same inputs
    """
    # Load grammar checker if not provided
    if language_tool is None:
        language_tool = load_grammar_checker()
    
    # If LanguageTool is not available, return empty results
    if language_tool is None:
        return {
            'total_errors': 0,
            'critical_errors': [],
            'moderate_errors': [],
            'minor_errors': [],
            'grammar_score': 100,
            'penalty_applied': 0,
            'error_free_percentage': 100.0,
            'unavailable': True,
            'message': 'Grammar checking unavailable (requires Java)'
        }
    
    if use_cache:
        # Generate hash for caching
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_grammar_check(text_hash, text, language_tool)
    else:
        return _perform_grammar_check(text, language_tool)


def calculate_grammar_penalty(errors: Dict) -> float:
    """
    Calculate score penalty based on error counts.
    
    Formula: 5 × critical + 2 × moderate + 0.5 × minor
    Maximum penalty: 20 points
    
    Args:
        errors: Dictionary with 'critical_errors', 'moderate_errors', 'minor_errors' lists
        
    Returns:
        Penalty value (0-20)
    """
    critical_count = len(errors.get('critical_errors', []))
    moderate_count = len(errors.get('moderate_errors', []))
    minor_count = len(errors.get('minor_errors', []))
    
    penalty = (critical_count * 5) + (moderate_count * 2) + (minor_count * 0.5)
    
    # Cap at maximum of 20 points
    return min(penalty, 20.0)


def generate_grammar_feedback(grammar_results: Dict) -> List[str]:
    """
    Generate user-friendly feedback messages based on grammar check results.
    
    Args:
        grammar_results: Results from check_grammar_and_spelling()
        
    Returns:
        List of feedback messages
    """
    feedback = []
    
    total_errors = grammar_results['total_errors']
    critical_count = len(grammar_results['critical_errors'])
    moderate_count = len(grammar_results['moderate_errors'])
    minor_count = len(grammar_results['minor_errors'])
    
    if total_errors == 0:
        feedback.append("✅ Excellent! No grammar or spelling errors detected.")
        return feedback
    
    # Overall summary
    feedback.append(f"Found {total_errors} grammar/spelling issue(s) in your resume.")
    
    # Critical errors
    if critical_count > 0:
        feedback.append(
            f"🔴 {critical_count} critical error(s) detected. "
            "These are spelling mistakes or major grammar issues that must be fixed."
        )
    
    # Moderate errors
    if moderate_count > 0:
        feedback.append(
            f"🟡 {moderate_count} moderate error(s) detected. "
            "These are punctuation or capitalization issues that should be addressed."
        )
    
    # Minor errors
    if minor_count > 0:
        feedback.append(
            f"🟢 {minor_count} minor issue(s) detected. "
            "These are style suggestions that could improve readability."
        )
    
    # Penalty information
    penalty = grammar_results['penalty_applied']
    if penalty > 0:
        feedback.append(
            f"⚠️ Grammar issues resulted in a {penalty:.1f} point penalty "
            f"(max penalty is 20 points)."
        )
    
    return feedback


def get_top_errors(grammar_results: Dict, max_errors: int = 5) -> List[Dict]:
    """
    Get the most important errors to display to the user.
    Prioritizes critical errors, then moderate, then minor.
    
    Args:
        grammar_results: Results from check_grammar_and_spelling()
        max_errors: Maximum number of errors to return
        
    Returns:
        List of error details, prioritized by severity
    """
    top_errors = []
    
    # Add critical errors first
    for error in grammar_results['critical_errors'][:max_errors]:
        error['severity'] = 'critical'
        top_errors.append(error)
    
    # Add moderate errors if space remains
    remaining = max_errors - len(top_errors)
    if remaining > 0:
        for error in grammar_results['moderate_errors'][:remaining]:
            error['severity'] = 'moderate'
            top_errors.append(error)
    
    # Add minor errors if space remains
    remaining = max_errors - len(top_errors)
    if remaining > 0:
        for error in grammar_results['minor_errors'][:remaining]:
            error['severity'] = 'minor'
            top_errors.append(error)
    
    return top_errors
