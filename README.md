# StudyTrack | Student & Course Management System & AI Assistant

A full-stack Student and Course Management System built with **FastAPI**, **SQLite**, **SQLAlchemy ORM**, and vanilla **HTML5/CSS3/JavaScript**. It features custom algorithm implementations (Insertion Sort, Binary Search), structured AI Text Summarization, Cosine Similarity Semantic Search across notes, and an interactive AI Study Assistant.

---

## 📌 Project Architecture

```
studytrack/
├── backend/
│   ├── __init__.py
│   ├── database.py       # SQLite connection & SQLAlchemy Session
│   ├── models.py         # Student & Course SQLAlchemy ORM Data Models (1-to-Many)
│   ├── schemas.py        # Pydantic validation schemas for Students, Courses & AI
│   ├── crud.py           # Database CRUD helper operations
│   ├── seed_data.py      # Database seeder script for Students & Courses
│   ├── algorithms.py     # Custom Insertion Sort, Binary Search & Report Generator
│   ├── ai_service.py     # Text Summarizer, Cosine Similarity Search & AI Assistant Helper
│   ├── ai_assistant.py   # Backwards compatibility bridge for AI services
│   └── main.py           # FastAPI REST Application & Endpoints
├── frontend/
│   ├── index.html        # Glassmorphic Single Page Application
│   ├── style.css         # Responsive glassmorphism styling & animations
│   └── app.js            # Asynchronous fetch client logic & DOM rendering
├── studytrack.db         # SQLite database file
├── README.md             # Project documentation & algorithm complexity analysis
└── requirements.txt      # Python dependencies
```

---

## 🗄️ Database Models & Relationships

### 1. `Student` Model
* `id` (Integer, Primary Key)
* `name` (String, Indexed)
* `email` (String, Unique, Indexed)
* `age` (Integer)
* `courses` (Relationship -> 1-to-Many back-populates to `Course`, cascade delete)

### 2. `Course` Model
* `id` (Integer, Primary Key)
* `code` (String, e.g., "CS101")
* `title` (String, e.g., "Data Structures & Algorithms")
* `description` (String, Optional)
* `student_id` (Integer, Foreign Key referencing `students.id`)

---

## 🧮 Algorithm Time Complexity Analysis (Part 2)

### 1. Insertion Sort
Insertion Sort builds the sorted array one element at a time by repeatedly taking the next unsorted element and inserting it into its correct relative position among previously sorted elements.

#### 🟢 Best Case: $O(n)$
* **Condition**: The input array is **already sorted** in ascending order.
* **Explanation**:
  - The outer loop runs $n - 1$ times to iterate over all elements.
  - In each iteration $i$, the inner `while` condition (`arr[j] > key`) immediately evaluates to `False` on the very first comparison because every element is already less than or equal to its right neighbor.
  - Total comparisons: $(n - 1) \times 1 = n - 1 = O(n)$. Zero element shifts required.

#### 🔴 Worst Case: $O(n^2)$
* **Condition**: The input array is sorted in **reverse order** (descending order).
* **Explanation**:
  - For each element at index $i$, it must be compared against and shifted past *all* previous $i$ elements in the sorted subarray.
  - Sum of arithmetic series:
    $$\sum_{i=1}^{n-1} i = \frac{n(n - 1)}{2} = \frac{n^2 - n}{2} = O(n^2)$$
  - Requires $O(n^2)$ total comparisons and element shifts.

---

### 2. Binary Search
* **Prerequisite**: The dataset must be sorted by student Name (achieved via Insertion Sort by Name).
* **Time Complexity**: $O(\log n)$
* **Explanation**: Halves search space repeatedly by calculating `mid = (low + high) // 2` pointer comparisons.

---

## 🤖 AI Assistant Features (Part 3)

### 1. AI Text Summarizer (`POST /api/ai/summarize`)
Extracts structured JSON summary metrics (`topic`, `key_points`, `difficulty`) from raw study text.

### 2. Semantic Search (`POST /api/ai/semantic-search`)
Evaluates user query relevance against a pre-loaded dataset of 5 Computer Science notes using term frequency vector weighting and **Cosine Similarity**:

$$\text{Cosine Similarity} = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

### 3. AI Study Companion / Helper (`POST /api/ai/helper`)
Interactive AI assistant providing contextual study recommendations, concept explanations, and course guidance.

---

## 🚀 Setup & Execution Instructions

### Prerequisites
* Python 3.9+
* Pip package manager

### 1. Installation
```bash
git clone <YOUR_PUBLIC_GITHUB_REPO_URL>
cd studytrack
pip install -r requirements.txt
```

### 2. Run Database Seeder (Optional / Automated)
```bash
python -m backend.seed_data
```

### 3. Run Application Server
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Open Application
Navigate to: `http://127.0.0.1:8000`

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/students` | Add a new student (`name`, `email`, `age`) |
| `GET` | `/api/students` | Retrieve all students |
| `GET` | `/api/students/{id}` | Retrieve student by ID |
| `PUT` | `/api/students/{id}` | Update student age (`{"age": 22}`) |
| `DELETE` | `/api/students/{id}` | Delete student by ID |
| `POST` | `/api/courses` | Create a new course (`code`, `title`, `description`, `student_id`) |
| `GET` | `/api/courses` | Retrieve all courses |
| `GET` | `/api/courses/{id}` | Retrieve course by ID |
| `PUT` | `/api/courses/{id}` | Update course attributes |
| `DELETE` | `/api/courses/{id}` | Delete course by ID |
| `GET` | `/api/students/sorted-by-age` | Sort students by age using custom Insertion Sort |
| `GET` | `/api/students/search?name=Rohan` | Binary search student by name |
| `GET` | `/api/report` | Returns formatted string report (`Age 19 - Rohan`) |
| `POST` | `/api/ai/summarize` | Text summarizer (returns topic, key points, difficulty) |
| `POST` | `/api/ai/semantic-search` | Cosine similarity ranking over notes dataset |
| `POST` | `/api/ai/helper` | Interactive AI Study Assistant endpoint |
