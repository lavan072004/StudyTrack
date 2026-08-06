"""
StudyTrack AI Assistant Module.
Re-exports core AI services from backend.ai_service for backwards compatibility.
"""

from backend.ai_service import (
    NOTES_DATASET,
    tokenize,
    compute_tf,
    compute_idf,
    calculate_cosine_similarity,
    perform_semantic_search,
    summarize_text,
    generate_ai_study_assistance,
)

__all__ = [
    "NOTES_DATASET",
    "tokenize",
    "compute_tf",
    "compute_idf",
    "calculate_cosine_similarity",
    "perform_semantic_search",
    "summarize_text",
    "generate_ai_study_assistance",
]
