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
    StudentUpdateAge,
    StudentResponse,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    SummarizerRequest,
    SummarizerResponse,
    SemanticSearchRequest,
    NoteResponse,
    AIHelperRequest,
    AIHelperResponse,
)
from backend import crud
from backend.seed_data import seed_database
from backend.algorithms import (
    insertion_sort_by_age,
    binary_search_by_name,
    generate_student_report,
)
from backend.ai_service import (
    summarize_text,
    perform_semantic_search,
    generate_ai_study_assistance,
    NOTES_DATASET,
)

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyTrack API",
    description="Student & Course Management System with Custom Algorithms and AI Features",
    version="2.0.0",
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Seed initial student and course data on application startup."""
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


# ----------------------------------------------------
# PART 1 (A): Core Student CRUD Endpoints
# ----------------------------------------------------

@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Add a new student to the database."""
    existing_student = crud.get_student_by_email(db, student.email)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email already exists."
        )

    db_student = crud.create_student(db, student)
    return db_student


@app.get("/students", response_model=List[StudentResponse])
@app.get("/api/students", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    """Retrieve all students from the database."""
    return crud.get_students(db)


# ----------------------------------------------------
# PART 2: Algorithm Endpoints (Must be registered BEFORE /{student_id})
# ----------------------------------------------------

@app.get("/students/sorted-by-age", response_model=List[StudentResponse])
@app.get("/api/students/sorted-by-age", response_model=List[StudentResponse])
def get_students_sorted_by_age(db: Session = Depends(get_db)):
    """
    Returns all students sorted by Age using custom Insertion Sort.
    Does not use Python built-in .sort() or sorted().
    """
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    sorted_dicts = insertion_sort_by_age(student_dicts)
    return sorted_dicts


@app.get("/students/search", response_model=List[StudentResponse])
@app.get("/api/students/search", response_model=List[StudentResponse])
def search_student_by_name(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    Searches for a student by Name using custom Binary Search.
    Does not use Python built-in search shortcuts.
    """
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    matches, match_idx = binary_search_by_name(student_dicts, name)

    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No student found with name '{name}'."
        )

    return matches


@app.get("/students/{student_id}", response_model=StudentResponse)
@app.get("/api/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    """Retrieve a single student by ID."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student


@app.put("/students/{student_id}", response_model=StudentResponse)
@app.put("/api/students/{student_id}", response_model=StudentResponse)
def update_student_age(
    student_id: int, student_update: StudentUpdateAge, db: Session = Depends(get_db)
):
    """Update a student's age in the database."""
    updated_student = crud.update_student_age(db, student_id, student_update.age)
    if not updated_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return updated_student


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
@app.delete("/api/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student from the database."""
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return {"message": f"Student ID {student_id} successfully deleted."}


@app.get("/report")
@app.get("/api/report")
def get_report(db: Session = Depends(get_db)):
    """
    Returns a report sorted by Age in the format:
    Age 19 - Rohan
    Age 20 - Farhan
    Age 21 - Priya
    """
    students = crud.get_students(db)
    student_dicts = [s.to_dict() for s in students]
    report_lines = generate_student_report(student_dicts)
    return {
        "formatted_report": report_lines,
        "raw_text": "\n".join(report_lines)
    }


# ----------------------------------------------------
# PART 1 (B): Core Course CRUD Endpoints
# ----------------------------------------------------

@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def add_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Add a new course to the database."""
    if course.student_id:
        student = crud.get_student(db, course.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student ID {course.student_id} does not exist."
            )
    return crud.create_course(db, course)


@app.get("/courses", response_model=List[CourseResponse])
@app.get("/api/courses", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    """Retrieve all courses from the database."""
    return crud.get_courses(db)


@app.get("/courses/{course_id}", response_model=CourseResponse)
@app.get("/api/courses/{course_id}", response_model=CourseResponse)
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    """Retrieve a single course by ID."""
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return course


@app.put("/courses/{course_id}", response_model=CourseResponse)
@app.put("/api/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db)
):
    """Update a course in the database."""
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
    """Delete a course from the database."""
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return {"message": f"Course ID {course_id} successfully deleted."}


# ----------------------------------------------------
# PART 3: AI Assistant Endpoints
# ----------------------------------------------------

@app.post("/ai/summarize", response_model=SummarizerResponse)
@app.post("/api/ai/summarize", response_model=SummarizerResponse)
def summarize_endpoint(request: SummarizerRequest):
    """Summarizes long text into structured JSON: topic, key_points, difficulty."""
    return summarize_text(request.text)


@app.post("/ai/semantic-search", response_model=List[NoteResponse])
@app.post("/api/ai/semantic-search", response_model=List[NoteResponse])
def semantic_search_endpoint(request: SemanticSearchRequest):
    """Performs Cosine Similarity search on the 5 pre-loaded CS notes."""
    return perform_semantic_search(request.query)


@app.post("/ai/helper", response_model=AIHelperResponse)
@app.post("/api/ai/helper", response_model=AIHelperResponse)
@app.post("/api/ai/ask", response_model=AIHelperResponse)
def ai_helper_endpoint(request: AIHelperRequest):
    """Interactive AI Assistant providing study tips, concept explanations, and course guidance."""
    return generate_ai_study_assistance(request.prompt, request.context)


@app.get("/ai/notes", response_model=List[Dict[str, Any]])
@app.get("/api/ai/notes", response_model=List[Dict[str, Any]])
def get_notes_dataset():
    """Retrieve the dataset of 5 CS notes."""
    return NOTES_DATASET


# ----------------------------------------------------
# Serve Static Frontend Files
# ----------------------------------------------------
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")