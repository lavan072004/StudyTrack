# StudyTrack | Student & Course Management System with Custom Algorithms & AI Assistant

StudyTrack is a full-stack academic management application built using **FastAPI**, **SQLite**, **SQLAlchemy ORM**, and vanilla **HTML/CSS/JavaScript**. It includes handwritten algorithm implementations (Insertion Sort, Binary Search), structured AI note summarization, and 12-element mock vector Cosine Similarity semantic search.

---

## 📌 Project Overview & Structure

```
studytrack/
├── backend/
│   ├── main.py            # FastAPI Application & REST Endpoints
│   ├── database.py        # SQLite Database connection & Session Local
│   ├── models.py          # Student & Course SQLAlchemy ORM Models
│   ├── schemas.py         # Pydantic Schemas & Field Validators (@field_validator)
│   ├── crud.py            # Database CRUD Operations & Count Queries
│   ├── algorithms.py      # Custom Insertion Sort, Binary Search & Report Generator
│   ├── ai_service.py      # Mock 12-element Embeddings, Cosine Similarity & Summarizer
│   ├── seed_data.py       # Seed script with exact 8 assessment students
│   └── requirements.txt   # Backend dependencies
├── frontend/
│   ├── index.html         # Responsive Dashboard (Event Delegation & Error Banner)
│   ├── style.css          # Glassmorphism dark mode responsive CSS
│   └── app.js             # Vanilla JS DOM manipulation client
├── README.md              # Documentation & Complexity Analysis
├── .env.example           # Environment configuration template
└── .gitignore             # Excluded files (.env, __pycache__, *.pyc, *.db)
```

---

## ⚙️ Prerequisites & Setup Instructions

### Prerequisites
* Python 3.9+ installed
* Web browser (Chrome, Firefox, Edge)

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone <YOUR_PUBLIC_GITHUB_REPO_URL>
cd studytrack
pip install -r backend/requirements.txt
```

### 2. Run Backend Application Server
Start the FastAPI server on port 8000:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open Frontend Application
Navigate to `http://127.0.0.1:8000` in your web browser (or serve `frontend/` via Live Server on `http://localhost:5500`).

---

## 📡 API Endpoint Reference

### Student CRUD Endpoints
* `POST /students/` - Register new student (`name`, `email`, `age`). Validates email format containing `@` and `age > 0`.
* `GET /students/` - Retrieve students (supports `?min_age=X` filter).
* `GET /students/{student_id}` - Retrieve single student by ID.
* `PATCH /students/{student_id}` - Update student fields (e.g. `{"age": 21}`).
* `DELETE /students/{student_id}` - Delete student by ID.

### Course CRUD Endpoints
* `POST /courses/` - Register new course (`course_name`, `credits` [1..6], `student_id`).
* `GET /courses/` - Retrieve all courses.
* `GET /courses/{course_id}` - Retrieve single course by ID.
* `PATCH /courses/{course_id}` - Update course fields.
* `DELETE /courses/{course_id}` - Delete course by ID.

### Minimum Age Filter & Course Count Endpoints
* `GET /students/?min_age=20` - Returns students whose age is `>= min_age`.
* `GET /students/{student_id}/course-count` - Returns course count using database-level `func.count()` query:
  ```json
  {
    "student_id": 1,
    "course_count": 2
  }
  ```

### Algorithm Endpoints
* `GET /students/sorted?by=age` (or `by=name`) - Sorts live roster using manual Insertion Sort.
* `GET /students/search?name=Rohan` - Binary search on name-sorted roster using exact midpoint `low + (high - low) // 2`.
* `GET /students/report?min_age=21` - Returns formatted report lines `[Age X] Name <email>` and `count_meeting_min_age`.

### AI Assistant Endpoints
* `POST /assistant/summarize` - Accepts note text and returns:
  ```json
  {
    "topic": "Insertion Sort",
    "key_points": ["Insertion sort builds a sorted list element by element."],
    "difficulty": "easy"
  }
  ```
  *(Note: Empty input returns topic: `"untitled"`, key_points: `[]`, difficulty: `"easy"`)*.
* `GET /assistant/search?query=fastapi` - Generates 12-element mock vectors, calculates Cosine Similarity, and ranks 5 notes. *(Empty/OOV query returns all 5 notes with `score: 0.0`)*.

---

## 🧮 Algorithm Complexity & Analysis

### 1. Insertion Sort (`insertion_sort_by_field`)
* **Best Case**: $O(n)$ — Occurs when input array is already sorted. Inner while-loop condition fails on the 1st comparison per element ($n - 1$ total checks).
* **Worst Case**: $O(n^2)$ — Occurs when input array is sorted in reverse order. Requires $n(n-1)/2$ shifts and comparisons.

### 2. Binary Search (`binary_search_by_name`)
* **Prerequisite**: Expects an **already name-sorted roster** input.
* **Formula**: Uses exact integer division midpoint:
  $$\text{mid} = \text{low} + \frac{\text{high} - \text{low}}{2}$$
* **Complexity**: $O(\log n)$ — Repeatedly halves the search space.

---

## 🤖 AI Service Implementation

### 12-Word Mock Vocabulary
```text
1. sort       2. search     3. binary     4. insertion
5. sql        6. join       7. fastapi    8. pydantic
9. prompt     10. llm       11. database  12. validate
```

### Cosine Similarity Formula
$$\text{Similarity} = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} = \frac{\sum_{i=0}^{11} A_i B_i}{\sqrt{\sum_{i=0}^{11} A_i^2} \sqrt{\sum_{i=0}^{11} B_i^2}}$$
*(If either vector is a zero vector, returns `0.0`)*.

---

## 💡 Frontend Features & Architecture
* **Event Delegation**: Single event listener attached to `#roster-list` handling all dynamic button clicks (`.btn-save-age`, `.btn-delete-student`).
* **Visible Error Banner**: `<div id="error-banner">` displays runtime, network, or validation errors.
* **No Page Reload**: `POST /students/` creates and appends new student card using `document.createElement()` without reloading or rebuilding roster.
* **AI Helper Panel**: Interactive note summarizer and semantic search query engine directly integrated into dashboard.
