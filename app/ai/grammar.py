"""
Grammar Checker Module
Handles grammar and spelling checking for resume text using LanguageTool

📚 TEACHING NOTE:
    This module is responsible for ONE specific job: checking grammar.
    This is called the "Single Responsibility Principle" — each file/module
    does only one thing, and does it well. Good software design!
"""

import streamlit as st
from typing import Dict, List, Tuple
import language_tool_python
from language_tool_python import Match


# ============================================================
# 📚 TEACHING NOTE — What is a Whitelist?
# A whitelist is a list of things we ALLOW / IGNORE.
# Here, LanguageTool doesn't know tech words like "React" or "Docker"
# so it would incorrectly flag them as spelling mistakes.
# This whitelist tells the app: "These are valid tech words — don't flag them!"
# ============================================================
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

# ============================================================
# 📚 TEACHING NOTE — Proper Nouns Set
# University names, certifications etc. are "proper nouns" — 
# they are names, not regular English words. LanguageTool might 
# flag "GGSIPU" as a spelling error, but it's a real institution.
# Keeping these separate from tech terms makes the code more organized
# and easier to update independently.
# ============================================================
PROPER_NOUN_PATTERNS = {
    # Common Indian university abbreviations
    'ggsipu', 'iit', 'nit', 'iiit', 'bits', 'vit', 'srm', 'manipal', 'amity',
    'du', 'jnu', 'bhu', 'iim', 'ism', 'isb', 'xlri', 'fms', 'iift', 'nmims',
    
    # Common US university abbreviations
    'mit', 'stanford', 'caltech', 'cmu', 'ucla', 'ucsd', 'ucb', 'usc', 'nyu',
    
    # Common certifications
    'pmp', 'cka', 'ckad', 'cks', 'ccna', 'ccnp', 'cissp', 'ceh', 'oscp',
}


# ============================================================
# 📚 TEACHING NOTE — @st.cache_resource
# Loading LanguageTool is slow (needs Java to start).
# @st.cache_resource means: load it ONCE and share it across all users.
# Without this, every user visit would reload the tool → very slow app!
# Think of it like turning on a machine once, not every time you use it.
# ============================================================
@st.cache_resource
def load_grammar_checker(language: str = "en-US") -> language_tool_python.LanguageTool:
    """
    Load and cache LanguageTool for grammar checking.
    LanguageTool requires Java installed on the machine to run.
    """
    try:
        tool = language_tool_python.LanguageTool(language)
        return tool
    except Exception as e:
        # Show a helpful error message with step-by-step fix instructions
        error_msg = (
            f"Failed to load LanguageTool for '{language}'.\n\n"
            f"Troubleshooting steps:\n"
            f"  1. pip install language-tool-python --upgrade\n"
            f"  2. Ensure Java is installed (required by LanguageTool)\n"  # LanguageTool runs on Java under the hood
            f"  3. Check if port 8081 is available\n"  # LanguageTool starts a local server on port 8081
            f"  4. Try restarting the application"
        )
        st.error(error_msg)
        raise  # Re-raise the exception so the app knows loading failed


def is_technical_term(word: str) -> bool:
    """
    Check if a word is a tech term that should be ignored by the grammar checker.
    
    📚 TEACHING NOTE:
        .lower() makes the check case-insensitive.
        "Python" and "python" and "PYTHON" all become "python" before checking.
        This avoids false mismatches due to capitalization.
    """
    return word.lower() in TECHNICAL_TERMS_WHITELIST


def categorize_error(error: Match) -> str:
    """
    Categorize a grammar error as 'critical', 'moderate', or 'minor'.
    
    📚 TEACHING NOTE — Why categorize errors?
        Not all grammar mistakes are equally bad on a resume.
        "their" vs "there" (critical) is worse than a missing comma (minor).
        By categorizing, we can show the most important fixes first,
        and apply heavier penalties for serious mistakes.
        
        LanguageTool gives each error a 'rule_id' (e.g., "MORFOLOGIK_RULE")
        and a 'category' (e.g., "GRAMMAR"). We use these to decide severity.
    
    Error severity levels:
        - critical  → spelling, subject-verb agreement, confused words
        - moderate  → punctuation, capitalization, articles
        - minor     → style suggestions, whitespace
    """
    # Convert to uppercase for consistent string comparison
    rule_id = error.rule_id.upper()
    category = error.category.upper()
    
    # --- Critical error patterns ---
    # These are things a recruiter would immediately notice and judge negatively
    critical_patterns = [
        'MORFOLOGIK_RULE',  # Spelling errors detected by dictionary
        'AGREEMENT',        # e.g., "He run" instead of "He runs"
        'VERB_FORM',        # Wrong verb form (e.g., "I have went")
        'CONFUSION',        # Confused words: their/there/they're, your/you're
        'WRONG_WORD',       # Wrong word usage in context
        'GRAMMAR',          # General grammar violations
    ]
    
    for pattern in critical_patterns:
        if pattern in rule_id or pattern in category:
            return "critical"
    
    # --- Moderate error patterns ---
    # These affect professionalism but are less severe than critical errors
    moderate_patterns = [
        'PUNCTUATION',    # Missing/extra commas, periods, etc.
        'CAPITALIZATION', # "python developer" should be "Python developer"
        'ARTICLE',        # Missing "a", "an", "the"
        'REDUNDANCY',     # "past history" → just "history"
        'COMMA',          # Comma splice or missing Oxford comma
        'APOSTROPHE',     # "its" vs "it's"
    ]
    
    for pattern in moderate_patterns:
        if pattern in rule_id or pattern in category:
            return "moderate"
    
    # If it doesn't match critical or moderate, it's a minor style issue
    return "minor"


def filter_technical_term_errors(errors: List[Match], text: str) -> List[Match]:
    """
    Remove grammar errors that are just tech words being flagged incorrectly.
    
    📚 TEACHING NOTE — Why filter before reporting?
        LanguageTool doesn't know about tech words. It would flag "Docker",
        "NumPy", "GraphQL" etc. as spelling errors. That would be wrong!
        We use the whitelist to remove these false alarms BEFORE showing
        results to the user. This is called "filtering false positives".
        
    How it works:
        Each 'error' object knows its position in the text via 'offset'.
        We slice the text to get the exact word that was flagged,
        then check if it's in our whitelist. If yes, we skip it.
    """
    filtered_errors = []
    
    for error in errors:
        # Use the error's position (offset) to extract the flagged word from text
        error_start = error.offset
        error_end = error.offset + error.error_length
        error_word = text[error_start:error_end]  # e.g., "Docker" or "teh"
        
        # Skip this error if the flagged word is a known tech term
        if is_technical_term(error_word):
            continue  # Don't add to filtered list — effectively ignoring it
            
        filtered_errors.append(error)
    
    return filtered_errors


def extract_error_context(text: str, error: Match, context_chars: int = 50) -> str:
    """
    Extract a snippet of text around an error so the user can see it in context.
    
    📚 TEACHING NOTE — Why show context?
        If we just say "spelling error at position 142", that's not helpful.
        Instead we show: "...built a scalabel system..." so the user
        immediately sees WHERE the error is and can fix it.
        
        context_chars=50 means: show 50 characters before and after the error.
        max() and min() are used to avoid going out of string bounds
        (e.g., if error is at the very start or end of text).
    """
    # Don't go before the start of the string (minimum index = 0)
    start = max(0, error.offset - context_chars)
    # Don't go past the end of the string
    end = min(len(text), error.offset + error.error_length + context_chars)
    
    context = text[start:end]
    
    # Add "..." to indicate the text was cut off (truncated)
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context


def _perform_grammar_check(
    text: str,
    language_tool: language_tool_python.LanguageTool
) -> Dict:
    """
    Internal function — runs the actual grammar check and builds the result dictionary.
    
    📚 TEACHING NOTE — Naming convention: underscore prefix (_)
        Functions that start with _ are "private" by convention in Python.
        This means: "Don't call this directly from outside this file."
        The public function (check_grammar_and_spelling) is what other
        modules should use. This internal one does the heavy lifting.
        
    Flow:
        1. Run LanguageTool on the text → get list of errors (called 'matches')
        2. Filter out false positives (tech terms)
        3. Categorize each error as critical / moderate / minor
        4. Calculate a penalty score
        5. Return everything as a clean dictionary
    """
    # Step 1: Run LanguageTool — this is the core AI grammar check
    matches = language_tool.check(text)
    
    # Step 2: Remove false positives caused by tech words like "React", "AWS" etc.
    matches = filter_technical_term_errors(matches, text)
    
    # Step 3: Sort errors into severity buckets
    critical_errors = []
    moderate_errors = []
    minor_errors = []
    
    for error in matches:
        category = categorize_error(error)
        
        # Build a structured dictionary for each error — easy to display in UI
        error_detail = {
            'message': error.message,                          # Human-readable explanation
            'context': extract_error_context(text, error),    # Snippet showing where the error is
            'suggestions': error.replacements[:3] if error.replacements else [],  # Top 3 fix suggestions
            'rule_id': error.rule_id,                         # Technical rule ID (for debugging)
            'offset': error.offset,                           # Character position in text
            'error_length': error.error_length,               # How many characters the error spans
            'error_text': text[error.offset:error.offset + error.error_length]  # The actual wrong word/phrase
        }
        
        # Add to the correct severity bucket
        if category == "critical":
            critical_errors.append(error_detail)
        elif category == "moderate":
            moderate_errors.append(error_detail)
        else:
            minor_errors.append(error_detail)
    
    # Step 4: Calculate how many points to deduct from the score
    penalty = calculate_grammar_penalty({
        'critical_errors': critical_errors,
        'moderate_errors': moderate_errors,
        'minor_errors': minor_errors
    })
    
    # Step 5: Calculate what % of the text is error-free
    # Formula: if 3 errors in 100 words → 97% error-free
    total_errors = len(critical_errors) + len(moderate_errors) + len(minor_errors)
    word_count = len(text.split())
    error_free_percentage = max(0, 100 - (total_errors / max(word_count, 1) * 100))
    # max(word_count, 1) prevents division by zero if text is empty
    
    return {
        'total_errors': total_errors,
        'critical_errors': critical_errors,
        'moderate_errors': moderate_errors,
        'minor_errors': minor_errors,
        'grammar_score': max(0, 100 - penalty),  # Score = 100 minus penalty (minimum 0)
        'penalty_applied': penalty,
        'error_free_percentage': round(error_free_percentage, 2)
    }


# ============================================================
# 📚 TEACHING NOTE — @st.cache_data vs @st.cache_resource
# @st.cache_resource → caches objects like models (shared across users)
# @st.cache_data     → caches function return values (data/results)
# ttl=3600 means the cache expires after 3600 seconds = 1 hour
# After 1 hour, the function will re-run instead of using old cached result.
#
# The parameter _language_tool has an underscore prefix → Streamlit ignores
# it when creating the cache key (because objects can't be hashed easily).
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def _cached_grammar_check(text_hash: str, text: str, _language_tool) -> Dict:
    """
    Cached wrapper around _perform_grammar_check.
    
    📚 TEACHING NOTE — Why hash the text?
        Streamlit's cache works by comparing inputs. But hashing the full
        text as a cache key is expensive. Instead, we hash the text to a
        short fixed-length string (SHA-256) and use THAT as the key.
        Same resume text → same hash → returns cached result instantly!
    """
    return _perform_grammar_check(text, _language_tool)


def check_grammar_and_spelling(
    text: str,
    language_tool: language_tool_python.LanguageTool = None,
    use_cache: bool = True
) -> Dict:
    """
    Main public function — performs grammar and spelling check on resume text.
    
    📚 TEACHING NOTE — This is the "entry point" for grammar checking.
        Other modules call THIS function, not the internal ones.
        It handles two jobs:
        1. Loading the grammar tool if not already provided (lazy loading)
        2. Deciding whether to use cache or run fresh
        
    Returns a dictionary with:
        - total_errors: int
        - critical_errors, moderate_errors, minor_errors: lists
        - grammar_score: float (0-100)
        - penalty_applied: float
        - error_free_percentage: float
    """
    # Lazy loading: only load the grammar checker if it wasn't passed in
    # This gives callers flexibility — they can reuse an existing tool instance
    if language_tool is None:
        language_tool = load_grammar_checker()
    
    if use_cache:
        # Create a unique fingerprint of the text using SHA-256 hashing
        # SHA-256 always produces a 64-character string, no matter how long the text is
        import hashlib
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return _cached_grammar_check(text_hash, text, language_tool)
    else:
        # Skip cache — useful during testing or when you always need fresh results
        return _perform_grammar_check(text, language_tool)


def calculate_grammar_penalty(errors: Dict) -> float:
    """
    Calculate how many points to deduct from the ATS score based on grammar errors.
    
    📚 TEACHING NOTE — Weighted Penalty System:
        Not all errors cost the same points. The formula is:
            penalty = (critical × 5) + (moderate × 2) + (minor × 0.5)
        
        Example: 2 critical + 3 moderate + 5 minor errors
            = (2×5) + (3×2) + (5×0.5)
            = 10 + 6 + 2.5
            = 18.5 points deducted
        
        Maximum penalty is capped at 20 points so even terrible grammar
        doesn't make the score go below 0 from this component alone.
        
        This is a deliberate product decision — grammar is important
        but shouldn't completely dominate the ATS score.
    """
    critical_count = len(errors.get('critical_errors', []))
    moderate_count = len(errors.get('moderate_errors', []))
    minor_count = len(errors.get('minor_errors', []))
    
    # Weighted formula — critical errors cost the most
    penalty = (critical_count * 5) + (moderate_count * 2) + (minor_count * 0.5)
    
    # Cap penalty at 20 — prevents extreme cases from dominating the total score
    return min(penalty, 20.0)


def generate_grammar_feedback(grammar_results: Dict) -> List[str]:
    """
    Convert raw grammar check numbers into human-readable feedback messages.
    
    📚 TEACHING NOTE — Separation of Concerns:
        Notice how this function doesn't DO the grammar check.
        It only takes results and formats them nicely.
        This separation makes both functions easier to test and change.
        E.g., if you want to change the emoji style, you only touch THIS function.
        
    The feedback is tiered:
        🔴 Critical  → "Must fix" — spelling, wrong words
        🟡 Moderate  → "Should fix" — punctuation, capitalization
        🟢 Minor     → "Nice to fix" — style suggestions
    """
    feedback = []
    
    total_errors = grammar_results['total_errors']
    critical_count = len(grammar_results['critical_errors'])
    moderate_count = len(grammar_results['moderate_errors'])
    minor_count = len(grammar_results['minor_errors'])
    
    # Best case — no errors found
    if total_errors == 0:
        feedback.append("✅ Excellent! No grammar or spelling errors detected.")
        return feedback  # Early return — no need to process further
    
    # Summary line showing total count
    feedback.append(f"Found {total_errors} grammar/spelling issue(s) in your resume.")
    
    # Each severity level adds its own message if it has errors
    if critical_count > 0:
        feedback.append(
            f"🔴 {critical_count} critical error(s) detected. "
            "These are spelling mistakes or major grammar issues that must be fixed."
        )
    
    if moderate_count > 0:
        feedback.append(
            f"🟡 {moderate_count} moderate error(s) detected. "
            "These are punctuation or capitalization issues that should be addressed."
        )
    
    if minor_count > 0:
        feedback.append(
            f"🟢 {minor_count} minor issue(s) detected. "
            "These are style suggestions that could improve readability."
        )
    
    # Tell the user how many ATS points they lost due to grammar
    penalty = grammar_results['penalty_applied']
    if penalty > 0:
        feedback.append(
            f"⚠️ Grammar issues resulted in a {penalty:.1f} point penalty "
            f"(max penalty is 20 points)."
        )
    
    return feedback


def get_top_errors(grammar_results: Dict, max_errors: int = 5) -> List[Dict]:
    """
    Return the most important errors to show the user — prioritized by severity.
    
    📚 TEACHING NOTE — Priority Queue concept (simplified):
        We don't show ALL errors (could be 50+). We show the top 5 (default),
        always filling slots with critical errors first, then moderate, then minor.
        
        Example with max_errors=5:
            3 critical → fills slots 1,2,3
            2 moderate → fills slots 4,5
            minor errors → no room left, not shown
        
        This ensures users see the MOST IMPORTANT issues first.
        UX principle: don't overwhelm users with information.
    """
    top_errors = []
    
    # Fill from critical errors first — these matter most
    for error in grammar_results['critical_errors'][:max_errors]:
        error['severity'] = 'critical'  # Tag the error so UI can color-code it
        top_errors.append(error)
    
    # Fill remaining slots with moderate errors
    remaining = max_errors - len(top_errors)
    if remaining > 0:
        for error in grammar_results['moderate_errors'][:remaining]:
            error['severity'] = 'moderate'
            top_errors.append(error)
    
    # Fill any still-remaining slots with minor errors
    remaining = max_errors - len(top_errors)
    if remaining > 0:
        for error in grammar_results['minor_errors'][:remaining]:
            error['severity'] = 'minor'
            top_errors.append(error)
    
    return top_errors