import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import Student, Course
from backend.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    SummarizerRequest,
    SummarizerResponse,
    NoteResponse,
)
from backend import crud
from backend.seed_data import seed_database
from backend.algorithms import (
    insertion_sort_by_field,
    binary_search_by_name,
    generate_student_report,
    count_students_meeting_min_age,
)
from backend.ai_service import (
    summarize_note,
    search_notes,
    NOTES_DATASET,
)

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyTrack API",
    description="Student & Course Management System with Custom Algorithms and AI Features",
    version="2.0.0",
)

# Requirement 10: Explicit CORS for http://localhost:5500 (No allow_origins=["*"])
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Seed database on startup if empty."""
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


# ============================================================================
# STUDENT CRUD ENDPOINTS
# ============================================================================

@app.post("/students/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Add a new student record to the database."""
    existing_student = crud.get_student_by_email(db, student.email)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email already exists."
        )

    return crud.create_student(db, student)


@app.get("/students/", response_model=List[StudentResponse])
@app.get("/students", response_model=List[StudentResponse])
@app.get("/api/students", response_model=List[StudentResponse])
def get_students(min_age: Optional[int] = Query(None, description="Minimum age filter"), db: Session = Depends(get_db)):
    """
    Retrieve students from the database.
    Requirement 8: If min_age is provided, return students whose age is >= min_age.
    """
    return crud.get_students(db, min_age=min_age)


# ============================================================================
# ALGORITHMS ENDPOINTS (Must be registered BEFORE /students/{student_id})
# ============================================================================

@app.get("/students/sorted", response_model=List[StudentResponse])
@app.get("/api/students/sorted", response_model=List[StudentResponse])
def get_students_sorted(by: str = Query("age", description="Sort by field: 'age' or 'name'"), db: Session = Depends(get_db)):
    """
    Requirement 12: GET /students/sorted?by=age or by=name.
    Sorts students using custom manual Insertion Sort.
    """
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    sorted_dicts = insertion_sort_by_field(student_dicts, field=by)
    return sorted_dicts


@app.get("/students/search", response_model=List[StudentResponse])
@app.get("/api/students/search", response_model=List[StudentResponse])
def search_student_by_name(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    Requirement 13: GET /students/search?name=
    Searches for a student by Name using custom handwritten iterative Binary Search.
    Sorts roster by Name first, then passes the name-sorted roster to binary_search_by_name.
    """
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    
    # Pre-sort roster by name as required for binary search input
    name_sorted_students = insertion_sort_by_field(student_dicts, field="name")
    matches = binary_search_by_name(name_sorted_students, name)

    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No student found with name '{name}'."
        )

    return matches


@app.get("/students/report")
@app.get("/api/students/report")
@app.get("/report")
@app.get("/api/report")
def get_report(min_age: int = Query(21, description="Minimum age threshold"), db: Session = Depends(get_db)):
    """
    Requirement 14: GET /students/report?min_age=21.
    Returns report formatted as '[Age X] Name <email>' and count_meeting_min_age.
    """
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    report_lines, count_meeting = generate_student_report(student_dicts, min_age=min_age)
    
    return {
        "report": report_lines,
        "count_meeting_min_age": count_meeting,
        "raw_text": "\n".join(report_lines)
    }


@app.get("/students/{student_id}/course-count")
@app.get("/api/students/{student_id}/course-count")
def get_student_course_count(student_id: int, db: Session = Depends(get_db)):
    """
    Requirement 9: GET /students/{student_id}/course-count.
    Uses database-level SQLAlchemy count() query.
    """
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    
    count = crud.get_student_course_count(db, student_id)
    return {
        "student_id": student_id,
        "course_count": count
    }


@app.get("/students/{student_id}", response_model=StudentResponse)
@app.get("/api/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    """Retrieve a single student by ID."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student


@app.patch("/students/{student_id}", response_model=StudentResponse)
@app.patch("/api/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    """
    Requirement 6 & 25: PATCH /students/{student_id}.
    Updates student fields (e.g. age) via PATCH.
    """
    updated_student = crud.update_student(db, student_id, student_update)
    if not updated_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return updated_student


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
@app.delete("/api/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Requirement 6: DELETE /students/{student_id}."""
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return {"message": f"Student ID {student_id} successfully deleted."}


# ============================================================================
# COURSE CRUD ENDPOINTS
# ============================================================================

@app.post("/courses/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def add_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Requirement 7: POST /courses/."""
    if course.student_id:
        student = crud.get_student(db, course.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student ID {course.student_id} does not exist."
            )
    return crud.create_course(db, course)


@app.get("/courses/", response_model=List[CourseResponse])
@app.get("/courses", response_model=List[CourseResponse])
@app.get("/api/courses", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    """Requirement 7: GET /courses/."""
    return crud.get_courses(db)


@app.get("/courses/{course_id}", response_model=CourseResponse)
@app.get("/api/courses/{course_id}", response_model=CourseResponse)
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    """Requirement 7: GET /courses/{course_id}."""
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return course


@app.patch("/courses/{course_id}", response_model=CourseResponse)
@app.patch("/api/courses/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db)):
    """Requirement 7: PATCH /courses/{course_id}."""
    if course_update.student_id:
        student = crud.get_student(db, course_update.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student ID {course_update.student_id} does not exist."
            )
    updated_course = crud.update_course(db, course_id, course_update)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return updated_course


@app.delete("/courses/{course_id}", status_code=status.HTTP_200_OK)
@app.delete("/api/courses/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Requirement 7: DELETE /courses/{course_id}."""
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return {"message": f"Course ID {course_id} successfully deleted."}


# ============================================================================
# AI SERVICE ENDPOINTS
# ============================================================================

@app.post("/assistant/summarize", response_model=SummarizerResponse)
@app.post("/api/assistant/summarize", response_model=SummarizerResponse)
@app.post("/ai/summarize", response_model=SummarizerResponse)
def summarize_endpoint(request: SummarizerRequest):
    """
    Requirement 16 & 20: POST /assistant/summarize.
    Summarizes note text into topic, key_points, difficulty (lowercase).
    """
    return summarize_note(request.text if request else "")


@app.get("/assistant/search", response_model=List[NoteResponse])
@app.get("/api/assistant/search", response_model=List[NoteResponse])
@app.get("/ai/semantic-search", response_model=List[NoteResponse])
def search_notes_endpoint(query: str = Query("", description="Search query string")):
    """
    Requirement 20: GET /assistant/search?query=.
    Ranks 5 notes using mock_embed and cosine_similarity.
    Returns 5 notes with score: 0.0 for empty/OOV query.
    """
    return search_notes(query)


@app.get("/assistant/notes", response_model=List[Dict[str, Any]])
def get_notes_dataset():
    """Returns exact 5 notes dataset."""
    return NOTES_DATASET


# ============================================================================
# SERVE STATIC FRONTEND FILES
# ============================================================================
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")