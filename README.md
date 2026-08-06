# StudyTrack | Student Management System & AI Assistant

A full-stack Student Management System built with **FastAPI**, **SQLite**, **SQLAlchemy ORM**, and vanilla **HTML/CSS/JavaScript**. It features custom manual algorithm implementations (Insertion Sort, Binary Search), structured AI Text Summarization, and Cosine Similarity Semantic Search across notes.

---

## 📌 Project Architecture

```
studytrack/
├── backend/
│   ├── __init__.py
│   ├── database.py       # SQLite connection & SQLAlchemy Session
│   ├── models.py         # Student SQLAlchemy ORM Data Model
│   ├── schemas.py        # Pydantic data validation schemas
│   ├── algorithms.py     # Custom Insertion Sort, Binary Search & Report Generator
│   ├── ai_assistant.py   # Text Summarizer & Cosine Similarity Semantic Search
│   └── main.py           # FastAPI Application & REST Endpoints
├── frontend/
│   ├── index.html        # Single Page Application (Dashboard, Algorithms, AI Tools)
│   ├── style.css         # Glassmorphic responsive dark mode styling
│   └── app.js            # Asynchronous fetch client logic & DOM rendering
├── README.md             # Project documentation & algorithm complexity analysis
└── requirements.txt      # Python dependencies
```

---

## 🧮 Algorithm Time Complexity Analysis (Part 2)

### 1. Insertion Sort

Insertion Sort builds the sorted array one element at a time by repeatedly taking the next unsorted element and inserting it into its correct relative position among previously sorted elements.

#### 🟢 Best Case: $O(n)$
* **Condition**: The input array is **already sorted** in ascending order.
* **Explanation**:
  - The outer loop runs $n - 1$ times to iterate over all elements.
  - In each iteration $i$, the inner `while` condition (`arr[j] > key`) immediately evaluates to `False` on the very first comparison because every element is already less than or equal to its right neighbor.
  - Number of total comparisons: $(n - 1) \times 1 = n - 1 = O(n)$.
  - Zero element shifts are required.

#### 🔴 Worst Case: $O(n^2)$
* **Condition**: The input array is sorted in **reverse order** (descending order).
* **Explanation**:
  - For each element at index $i$, it must be compared against and shifted past *all* previous $i$ elements in the sorted subarray.
  - The inner loop executes $1 + 2 + 3 + \dots + (n - 1)$ times.
  - Sum of arithmetic series:
    $$\sum_{i=1}^{n-1} i = \frac{n(n - 1)}{2} = \frac{n^2 - n}{2} = O(n^2)$$
  - Requires $O(n^2)$ total comparisons and element shifts.

---

### 2. Binary Search

* **Prerequisite**: The dataset must be sorted by student Name (achieved via Insertion Sort by Name).
* **Time Complexity**: $O(\log n)$
* **Explanation**: The algorithm selects the middle pointer `mid = (low + high) // 2`. If the target name is less than `arr[mid]`, the upper half is discarded (`high = mid - 1`); if greater, the lower half is discarded (`low = mid + 1`). At each step, the remaining search space is halved.

---

## 🤖 AI Assistant Features (Part 3)

### 1. Text Summarizer (`POST /api/ai/summarize`)
Takes long text input and returns structured JSON containing:
```json
{
  "topic": "Binary Search",
  "key_points": [
    "Binary search is a divide and conquer algorithm for sorted arrays.",
    "Time complexity is O(log n), making it very fast."
  ],
  "difficulty": "Easy"
}
```

### 2. Semantic Search (`POST /api/ai/semantic-search`)
Evaluates user query relevance against a pre-loaded dataset of 5 Computer Science notes using term frequency vector weighting and **Cosine Similarity**:

$$\text{Cosine Similarity} = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

Returns notes ranked by similarity score percentage.

---

## 🚀 Setup & Execution Instructions

### Prerequisites
* Python 3.9+
* Pip package manager

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone <YOUR_PUBLIC_GITHUB_REPO_URL>
cd studytrack
pip install -r requirements.txt
```

### 2. Run Application Server
Start the FastAPI server with Uvicorn:
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Open Application
Open your web browser and navigate to:
```
http://127.0.0.1:8000
```
The FastAPI server will serve the responsive glassmorphism single-page frontend.

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/students` | Add a new student (`name`, `email`, `age`) |
| `GET` | `/api/students` | Retrieve all students |
| `PUT` | `/api/students/{id}` | Update student age (`{"age": 22}`) |
| `DELETE` | `/api/students/{id}` | Delete student by ID |
| `GET` | `/api/students/sorted-by-age` | Sort students by age using Insertion Sort |
| `GET` | `/api/students/search?name=Rohan` | Binary search student by name |
| `GET` | `/api/report` | Returns formatted string report (`Age 19 - Rohan`) |
| `POST` | `/api/ai/summarize` | Returns topic, key points, difficulty JSON summary |
| `POST` | `/api/ai/semantic-search` | Cosine similarity ranking over notes dataset |

---

## 🌿 Git Workflow & History

This repository followed a structured Git feature branch workflow:
1. Created initial commit on `main`.
2. Created feature branch `feature/student-management-system`.
3. Modular commits made for backend, frontend, algorithms, AI features, and docs.
4. Feature branch merged back into `main`.
