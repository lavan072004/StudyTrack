import re
import math
from datetime import datetime
from typing import List, Dict, Any, Optional

# Part 3 Dataset: Exactly 5 curated Computer Science notes
NOTES_DATASET = [
    {
        "id": 1,
        "title": "Binary Search Algorithm",
        "content": "Binary Search is a divide-and-conquer algorithm that finds the position of a target value within a sorted array. It compares the target value to the middle element of the array and cuts the search space in half at each step, achieving O(log n) time complexity."
    },
    {
        "id": 2,
        "title": "Insertion Sort Algorithm",
        "content": "Insertion Sort is a simple comparison-based sorting algorithm that builds the final sorted array one item at a time. It iterates through an input array, removing one element and placing it into its correct position within the sorted list. Best case is O(n), worst case is O(n^2)."
    },
    {
        "id": 3,
        "title": "FastAPI Web Development",
        "content": "FastAPI is a high-performance Python web framework designed for building RESTful APIs. It provides automatic interactive documentation via OpenAPI and Swagger UI, fast execution using Starlette and Pydantic, and native asynchronous support."
    },
    {
        "id": 4,
        "title": "SQLite and SQLAlchemy ORM",
        "content": "SQLite is a self-contained, serverless relational database engine stored as a single file. SQLAlchemy is an Object Relational Mapper (ORM) in Python that allows developers to interact with SQLite databases using Python object model operations instead of raw SQL queries."
    },
    {
        "id": 5,
        "title": "Cosine Similarity and Semantic Search",
        "content": "Cosine Similarity measures the orientation angle between two numerical vectors in a multi-dimensional feature space. In natural language processing, it measures the semantic text similarity between document term frequencies or embeddings regardless of document size."
    }
]


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase terms, removing non-alphanumeric chars and stop words."""
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    stop_words = {
        "the", "is", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
        "with", "by", "it", "this", "that", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "but", "if", "not",
        "from", "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "any", "both", "each",
        "few", "more", "most", "other", "some", "such", "no", "nor", "only", "own",
        "same", "so", "than", "too", "very", "can", "will", "just", "should", "now"
    }
    return [w for w in words if w not in stop_words and len(w) > 1]


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Computes term frequency for a list of tokens."""
    tf_dict = {}
    total_tokens = len(tokens)
    if total_tokens == 0:
        return tf_dict
    for token in tokens:
        tf_dict[token] = tf_dict.get(token, 0) + 1
    for token in tf_dict:
        tf_dict[token] = tf_dict[token] / total_tokens
    return tf_dict


def compute_idf(documents_tokens: List[List[str]]) -> Dict[str, float]:
    """Computes inverse document frequency across a corpus of tokenized documents."""
    N = len(documents_tokens)
    idf_dict = {}
    if N == 0:
        return idf_dict
        
    all_words = set(word for doc in documents_tokens for word in doc)
    for word in all_words:
        doc_count = sum(1 for doc in documents_tokens if word in doc)
        idf_dict[word] = math.log((N + 1) / (doc_count + 1)) + 1
    return idf_dict


def calculate_cosine_similarity(vector_a: Dict[str, float], vector_b: Dict[str, float]) -> float:
    """
    Computes Cosine Similarity between two term vectors mathematically:
    Cosine Similarity = (A . B) / (||A|| * ||B||)
    """
    common_keys = set(vector_a.keys()) & set(vector_b.keys())
    dot_product = sum(vector_a[k] * vector_b[k] for k in common_keys)
    
    magnitude_a = math.sqrt(sum(v ** 2 for v in vector_a.values()))
    magnitude_b = math.sqrt(sum(v ** 2 for v in vector_b.values()))
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
        
    similarity = dot_product / (magnitude_a * magnitude_b)
    return round(similarity, 4)


def perform_semantic_search(query: str) -> List[Dict[str, Any]]:
    """
    Ranks the 5 notes in the dataset based on Cosine Similarity with the user query.
    """
    query_tokens = tokenize(query)
    notes_tokens = [tokenize(note["title"] + " " + note["content"]) for note in NOTES_DATASET]
    
    all_docs = notes_tokens + [query_tokens]
    idf = compute_idf(all_docs)
    
    # Compute TF-IDF for query
    query_tf = compute_tf(query_tokens)
    query_tfidf = {word: tf * idf.get(word, 0) for word, tf in query_tf.items()}
    
    results = []
    for i, note in enumerate(NOTES_DATASET):
        doc_tokens = notes_tokens[i]
        doc_tf = compute_tf(doc_tokens)
        doc_tfidf = {word: tf * idf.get(word, 0) for word, tf in doc_tf.items()}
        
        score = calculate_cosine_similarity(query_tfidf, doc_tfidf)
        
        results.append({
            "id": note["id"],
            "title": note["title"],
            "content": note["content"],
            "similarity_score": score
        })
        
    # Sort results by similarity score descending using custom insertion sort
    n = len(results)
    for i in range(1, n):
        key_item = results[i]
        j = i - 1
        while j >= 0 and results[j]["similarity_score"] < key_item["similarity_score"]:
            results[j + 1] = results[j]
            j -= 1
        results[j + 1] = key_item
        
    return results


def summarize_text(text: str) -> Dict[str, Any]:
    """
    Extracts key summary details from input text:
    - topic
    - key_points
    - difficulty ('Easy', 'Medium', 'Hard')
    """
    clean_text = text.strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    
    tokens = tokenize(clean_text)
    
    freq = {}
    for word in tokens:
        freq[word] = freq.get(word, 0) + 1
        
    sorted_words = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    top_keywords = [w[0].title() for w in sorted_words[:3]]
    
    topic = " ".join(top_keywords) if top_keywords else "General CS Overview"
    
    key_points = []
    for sent in sentences[:4]:
        if len(sent) > 10:
            key_points.append(sent)
            
    if not key_points and clean_text:
        key_points = [clean_text]
        
    avg_word_length = sum(len(w) for w in tokens) / max(1, len(tokens))
    
    if len(tokens) < 30 and avg_word_length < 5.5:
        difficulty = "Easy"
    elif len(tokens) < 80 or avg_word_length < 6.5:
        difficulty = "Medium"
    else:
        difficulty = "Hard"
        
    return {
        "topic": topic,
        "key_points": key_points,
        "difficulty": difficulty
    }


def generate_ai_study_assistance(prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Part 3 Interactive AI Assistant / Study Helper engine.
    Analyzes prompt intent and provides formatted intelligent study feedback,
    relevant concept breakdowns, and actionable study suggestions.
    """
    clean_prompt = prompt.strip()
    query_lower = clean_prompt.lower()

    # Search notes dataset for context grounding
    search_matches = perform_semantic_search(clean_prompt)
    top_match = search_matches[0] if search_matches and search_matches[0]["similarity_score"] > 0.05 else None

    # Determine intent & generate response
    if "binary" in query_lower or "search" in query_lower:
        response_text = (
            "Binary Search is an efficient O(log n) search algorithm for sorted datasets. "
            "It repeatedly divides the search space in half by comparing the middle element with the target key."
        )
        suggestions = [
            "Verify dataset is sorted by name/key before executing binary search",
            "Understand why best case is O(1) and worst case is O(log n)",
            "Compare Binary Search vs Linear Search performance"
        ]
    elif "sort" in query_lower or "insertion" in query_lower:
        response_text = (
            "Insertion Sort builds a sorted list one item at a time. "
            "It has an O(n) best-case time complexity for pre-sorted inputs and O(n²) worst-case complexity for reverse-ordered inputs."
        )
        suggestions = [
            "Review inner loop condition: arr[j] > key",
            "Test insertion sort on small arrays vs large random arrays",
            "Observe element shifts during sorting execution"
        ]
    elif "fastapi" in query_lower or "api" in query_lower or "backend" in query_lower:
        response_text = (
            "FastAPI uses Python type hints and Pydantic schemas for data validation and automatically "
            "generates interactive OpenAPI documentation at /docs."
        )
        suggestions = [
            "Use Dependency Injection (Depends(get_db)) for clean database sessions",
            "Validate request bodies using Pydantic BaseModel",
            "Define explicit response models for all REST endpoints"
        ]
    elif "course" in query_lower or "student" in query_lower:
        response_text = (
            "StudyTrack links Students to Courses via SQLAlchemy 1-to-Many relationships. "
            "Each Student can be enrolled in multiple courses like CS101, CS102, or CS103."
        )
        suggestions = [
            "Use /api/courses endpoints to register new course offerings",
            "Associate student IDs with courses to track individual enrollments",
            "Generate custom student age and course reports"
        ]
    else:
        response_text = (
            f"Regarding your query on '{clean_prompt}': "
            + (f"Related note concept: '{top_match['title']}' - {top_match['content']}" if top_match else 
               "Focus on breaking down core concepts into small daily revision targets and practice applying algorithms practically.")
        )
        suggestions = [
            "Try using the AI Text Summarizer for long lecture notes",
            "Use Semantic Search to discover related Computer Science topics",
            "Review algorithm space & time complexity trade-offs"
        ]

    return {
        "query": clean_prompt,
        "response": response_text,
        "suggestions": suggestions,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
