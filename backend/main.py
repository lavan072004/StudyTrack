import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# CORS Configuration for local development
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
    """Seed database on application startup if empty."""
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


# ============================================================================
# STUDENT CRUD ENDPOINTS
# ============================================================================

@app.post("/students/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Add a new student record to the database."""
    existing_student = crud.get_student_by_email(db, student.email)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists."
        )

    return crud.create_student(db, student)


@app.get("/students/", response_model=List[StudentResponse])
@app.get("/students", response_model=List[StudentResponse], include_in_schema=False)
def get_students(min_age: Optional[int] = Query(None, description="Minimum age filter"), db: Session = Depends(get_db)):
    """
    Retrieve students from the database.
    If min_age is provided, returns students whose age is >= min_age.
    """
    return crud.get_students(db, min_age=min_age)


# ============================================================================
# ALGORITHMS & REPORT ENDPOINTS
# ============================================================================

@app.get("/students/sorted", response_model=List[StudentResponse])
def get_students_sorted(by: str = Query("age", description="Sort by field: 'age' or 'name'"), db: Session = Depends(get_db)):
    """Sorts students using custom manual Insertion Sort algorithm."""
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    sorted_dicts = insertion_sort_by_field(student_dicts, field=by)
    return sorted_dicts


@app.get("/students/search", response_model=List[StudentResponse])
def search_student_by_name(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Searches for a student by Name using custom iterative Binary Search on a name-sorted roster."""
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    
    name_sorted_students = insertion_sort_by_field(student_dicts, field="name")
    matches = binary_search_by_name(name_sorted_students, name)

    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No student found with name '{name}'."
        )

    return matches


@app.get("/students/report")
def get_report(min_age: int = Query(21, description="Minimum age threshold"), db: Session = Depends(get_db)):
    """Returns a formatted student report filtered by min_age and sorted by age."""
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    report_lines, count_meeting = generate_student_report(student_dicts, min_age=min_age)
    
    return {
        "report": report_lines,
        "count_meeting_min_age": count_meeting,
        "raw_text": "\n".join(report_lines)
    }


@app.get("/students/{student_id}/course-count")
def get_student_course_count(student_id: int, db: Session = Depends(get_db)):
    """Returns the database-level course count for a student using SQLAlchemy count()."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    
    count = crud.get_student_course_count(db, student_id)
    return {
        "student_id": student_id,
        "course_count": count
    }


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    """Retrieve a single student by ID."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student


@app.patch("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    """Update student profile fields via PATCH."""
    updated_student = crud.update_student(db, student_id, student_update)
    if not updated_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return updated_student


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student profile by ID."""
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return {"message": f"Student ID {student_id} successfully deleted."}


# ============================================================================
# COURSE CRUD ENDPOINTS
# ============================================================================

@app.post("/courses/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def add_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Add a new course offering."""
    if course.student_id:
        student = crud.get_student(db, course.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student ID {course.student_id} does not exist."
            )
    return crud.create_course(db, course)


@app.get("/courses/", response_model=List[CourseResponse])
@app.get("/courses", response_model=List[CourseResponse], include_in_schema=False)
def get_courses(db: Session = Depends(get_db)):
    """Retrieve all course offerings."""
    return crud.get_courses(db)


@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    """Retrieve a single course by ID."""
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return course


@app.patch("/courses/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db)):
    """Update course fields via PATCH."""
    if course_update.student_id:
        student = crud.get_student(db, course_update.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student ID {course_update.student_id} does not exist."
            )
    updated_course = crud.update_course(db, course_id, course_update)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return updated_course


@app.delete("/courses/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course offering by ID."""
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return {"message": f"Course ID {course_id} successfully deleted."}


# ============================================================================
# AI ASSISTANT ENDPOINTS
# ============================================================================

@app.post("/assistant/summarize", response_model=SummarizerResponse)
def summarize_endpoint(request: SummarizerRequest):
    """Summarizes note text into topic, key_points, and difficulty level."""
    return summarize_note(request.text if request else "")


@app.get("/assistant/search", response_model=List[NoteResponse])
def search_notes_endpoint(query: str = Query("", description="Search query string")):
    """Ranks computer science notes using vector term embeddings and Cosine Similarity."""
    return search_notes(query)


@app.get("/assistant/notes", response_model=List[Dict[str, Any]])
def get_notes_dataset():
    """Returns the computer science notes dataset."""
    return NOTES_DATASET


# ============================================================================
# SERVE STATIC FRONTEND FILES
# ============================================================================
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")