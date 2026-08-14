import re
import math
from typing import List, Dict, Any, Optional

# 12-word vocabulary index for vector term embeddings
VOCABULARY = [
    "sort",
    "search",
    "binary",
    "insertion",
    "sql",
    "join",
    "fastapi",
    "pydantic",
    "prompt",
    "llm",
    "database",
    "validate"
]

# Curated Computer Science study notes dataset
NOTES_DATASET = [
    {
        "id": 1,
        "title": "Insertion Sort & Binary Search",
        "content": "Insertion sort builds a sorted list element by element. Binary search finds items in a binary sorted list with log n complexity."
    },
    {
        "id": 2,
        "title": "Database Systems & SQL Join",
        "content": "Relational databases use SQL to join tables, query database records, and manage indexes."
    },
    {
        "id": 3,
        "title": "FastAPI & Pydantic Validation",
        "content": "FastAPI uses pydantic schemas to validate data inputs and generate openapi documentation."
    },
    {
        "id": 4,
        "title": "LLM & Prompt Engineering",
        "content": "Prompt templates guide an llm to generate structured response payloads and text summaries."
    },
    {
        "id": 5,
        "title": "Software Architecture",
        "content": "Clean architecture separates backend crud operations from algorithms and database models."
    }
]


def mock_embed(text: str) -> List[float]:
    """Generates a 12-element numeric vector based on vocabulary word frequencies."""
    if not text:
        return [0.0] * 12

    text_lower = text.lower()
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text_lower)
    
    vec = []
    for term in VOCABULARY:
        count = words.count(term)
        vec.append(float(count))
        
    return vec


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Computes Cosine Similarity between two 12-element numeric vectors:
    Cosine Similarity = (A . B) / (||A|| * ||B||)
    Handles zero vectors safely: if either vector is zero vector, returns 0.0.
    """
    if not vec_a or not vec_b or len(vec_a) != 12 or len(vec_b) != 12:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    similarity = dot_product / (mag_a * mag_b)
    return round(similarity, 4)


def summarize_note(text: Optional[str]) -> Dict[str, Any]:
    """
    Summarizes note text into JSON format:
    {
      "topic": "...",
      "key_points": [],
      "difficulty": "easy"
    }
    For empty text, returns topic: "untitled", key_points: [], difficulty: "easy".
    """
    if not text or not text.strip():
        return {
            "topic": "untitled",
            "key_points": [],
            "difficulty": "easy"
        }

    clean_text = text.strip()
    words = re.findall(r'\b[a-zA-Z0-9]+\b', clean_text.lower())
    
    if not words:
        return {
            "topic": "untitled",
            "key_points": [],
            "difficulty": "easy"
        }

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if s.strip()]

    stop_words = {
        "the", "is", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
        "with", "by", "it", "this", "that", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "but", "if", "not", "from"
    }
    
    freq = {}
    for w in words:
        if w not in stop_words and len(w) > 1:
            freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    top_keywords = [w[0].title() for w in sorted_words[:3]]
    topic = " ".join(top_keywords) if top_keywords else "Study Note"

    key_points = sentences[:4] if sentences else [clean_text]

    total_words = len(words)
    if total_words < 20:
        difficulty = "easy"
    elif total_words < 60:
        difficulty = "medium"
    else:
        difficulty = "hard"

    return {
        "topic": topic,
        "key_points": key_points,
        "difficulty": difficulty
    }


def search_notes(query: str) -> List[Dict[str, Any]]:
    """
    Ranks notes using Cosine Similarity over 12-element vector embeddings.
    For empty queries, returns notes with score: 0.0.
    """
    query_vec = mock_embed(query)

    results = []
    for note in NOTES_DATASET:
        note_text = note["title"] + " " + note["content"]
        note_vec = mock_embed(note_text)
        score = cosine_similarity(query_vec, note_vec)
        results.append({
            "id": note["id"],
            "title": note["title"],
            "content": note["content"],
            "score": score
        })

    n = len(results)
    for i in range(1, n):
        key_item = results[i]
        j = i - 1
        while j >= 0 and results[j]["score"] < key_item["score"]:
            results[j + 1] = results[j]
            j -= 1
        results[j + 1] = key_item

    return results
