"""
Utils Package
Contains all utility modules for the ATS Resume Scorer application
"""

from .model_loader import (
    load_spacy_model,
    load_sentence_transformer,
    load_language_tool,
    initialize_all_models,
    get_models,
    get_model_load_times,
    get_model_status,
    is_model_loaded,
    preload_models_async
)

from .cache_manager import (
    generate_content_hash,
    get_cache_key,
    get_cached_analysis_results,
    store_analysis_results,
    clear_analysis_cache,
    get_cache_stats,
    get_lazy_loader,
    LazyLoader
)

from .recommendation_generator import (
    generate_skill_recommendations,
    generate_grammar_recommendations,
    generate_location_recommendations,
    generate_keyword_recommendations,
    generate_formatting_recommendations,
    generate_all_recommendations,
    prioritize_recommendations,
    format_recommendation_for_display,
    format_all_recommendations_for_display,
    generate_action_items_list,
    get_recommendation_summary,
    Priority,
    Recommendation
)

__all__ = [
    # Model loader
    'load_spacy_model',
    'load_sentence_transformer',
    'load_language_tool',
    'initialize_all_models',
    'get_models',
    'get_model_load_times',
    'get_model_status',
    'is_model_loaded',
    'preload_models_async',
    # Cache manager
    'generate_content_hash',
    'get_cache_key',
    'get_cached_analysis_results',
    'store_analysis_results',
    'clear_analysis_cache',
    'get_cache_stats',
    'get_lazy_loader',
    'LazyLoader',
    # Recommendation generator
    'generate_skill_recommendations',
    'generate_grammar_recommendations',
    'generate_location_recommendations',
    'generate_keyword_recommendations',
    'generate_formatting_recommendations',
    'generate_all_recommendations',
    'prioritize_recommendations',
    'format_recommendation_for_display',
    'format_all_recommendations_for_display',
    'generate_action_items_list',
    'get_recommendation_summary',
    'Priority',
    'Recommendation'
]
