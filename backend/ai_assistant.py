import re
import math
from typing import List, Dict, Any

# Part 3 Note Dataset: Exactly 5 curated Computer Science notes
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


# Helper: Tokenize text into words
def tokenize(text: str) -> List[str]:
    # Convert to lowercase and strip non-alphanumeric characters
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    # Basic stop words filter
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
    """Computes term frequency for tokens."""
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
    """Computes inverse document frequency across all documents."""
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
    # Find common keys
    common_keys = set(vector_a.keys()) & set(vector_b.keys())
    
    # Dot product
    dot_product = sum(vector_a[k] * vector_b[k] for k in common_keys)
    
    # Magnitudes
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
        
    # Sort results by similarity score descending (using custom insertion sort or lambda)
    # Using insertion sort descending for consistency
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
    
    # Word frequency analysis for topic extraction
    freq = {}
    for word in tokens:
        freq[word] = freq.get(word, 0) + 1
        
    # Identify top key words
    sorted_words = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    top_keywords = [w[0].title() for w in sorted_words[:3]]
    
    topic = " ".join(top_keywords) if top_keywords else "General Overview"
    
    # Key points: extract top 2-4 sentences based on length and relevance
    key_points = []
    for sent in sentences[:4]:
        if len(sent) > 10:
            key_points.append(sent)
            
    if not key_points and clean_text:
        key_points = [clean_text]
        
    # Assess difficulty based on average word length and vocabulary length
    avg_word_length = sum(len(w) for w in tokens) / max(1, len(tokens))
    vocab_size = len(set(tokens))
    
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
