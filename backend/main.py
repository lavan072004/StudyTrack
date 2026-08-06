import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import Student
from backend.schemas import (
    StudentCreate,
    StudentUpdateAge,
    StudentResponse,
    SummarizerRequest,
    SummarizerResponse,
    SemanticSearchRequest,
    NoteResponse,
)
from backend.algorithms import (
    insertion_sort_by_age,
    binary_search_by_name,
    generate_student_report,
)
from backend.ai_assistant import (
    summarize_text,
    perform_semantic_search,
    NOTES_DATASET,
)

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyTrack API",
    description="Student Management System with Custom Algorithms and AI Features",
    version="1.0.0",
)

# Enable CORS for cross-origin frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Seed initial student data if database is empty
def seed_initial_data(db: Session):
    if db.query(Student).count() == 0:
        sample_students = [
            Student(name="Rohan", email="rohan@studytrack.io", age=19),
            Student(name="Farhan", email="farhan@studytrack.io", age=20),
            Student(name="Priya", email="priya@studytrack.io", age=21),
            Student(name="Aanya", email="aanya@studytrack.io", age=18),
            Student(name="Dev", email="dev@studytrack.io", age=22),
        ]
        db.add_all(sample_students)
        db.commit()


@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        seed_initial_data(db)
    finally:
        db.close()


# ----------------------------------------------------
# PART 1: Core Student CRUD Endpoints
# ----------------------------------------------------

@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Add a new student to the database."""
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(
            status_code=400, detail="A student with this email already exists."
        )

    db_student = Student(name=student.name, email=student.email, age=student.age)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/students", response_model=List[StudentResponse])
@app.get("/api/students", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    """Retrieve all students from the database."""
    students = db.query(Student).all()
    return students


@app.put("/students/{student_id}", response_model=StudentResponse)
@app.put("/api/students/{student_id}", response_model=StudentResponse)
def update_student_age(
    student_id: int, student_update: StudentUpdateAge, db: Session = Depends(get_db)
):
    """Update a student's age in the database."""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found.")

    db_student.age = student_update.age
    db.commit()
    db.refresh(db_student)
    return db_student


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
@app.delete("/api/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student from the database."""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found.")

    db.delete(db_student)
    db.commit()
    return {"message": f"Student ID {student_id} successfully deleted."}


# ----------------------------------------------------
# PART 2: Algorithm Endpoints (Insertion Sort, Binary Search, Report)
# ----------------------------------------------------

@app.get("/students/sorted-by-age", response_model=List[StudentResponse])
@app.get("/api/students/sorted-by-age", response_model=List[StudentResponse])
def get_students_sorted_by_age(db: Session = Depends(get_db)):
    """
    Returns all students sorted by Age using custom Insertion Sort.
    Does not use Python built-in .sort() or sorted().
    """
    students = db.query(Student).all()
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
    students = db.query(Student).all()
    student_dicts = [s.to_dict() for s in students]
    matches, match_idx = binary_search_by_name(student_dicts, name)
    
    if not matches:
        raise HTTPException(status_code=404, detail=f"No student found with name '{name}'.")
        
    return matches


@app.get("/report")
@app.get("/api/report")
def get_report(db: Session = Depends(get_db)):
    """
    Returns a report sorted by Age in the format:
    Age 19 - Rohan
    Age 20 - Farhan
    Age 21 - Priya
    """
    students = db.query(Student).all()
    student_dicts = [s.to_dict() for s in students]
    report_lines = generate_student_report(student_dicts)
    return {
        "formatted_report": report_lines,
        "raw_text": "\n".join(report_lines)
    }


# ----------------------------------------------------
# PART 3: AI Assistant Endpoints
# ----------------------------------------------------

@app.post("/ai/summarize", response_model=SummarizerResponse)
@app.post("/api/ai/summarize", response_model=SummarizerResponse)
def summarize_endpoint(request: SummarizerRequest):
    """
    Summarizes long text into structured JSON: topic, key_points, difficulty.
    """
    result = summarize_text(request.text)
    return result


@app.post("/ai/semantic-search", response_model=List[NoteResponse])
@app.post("/api/ai/semantic-search", response_model=List[NoteResponse])
def semantic_search_endpoint(request: SemanticSearchRequest):
    """
    Performs Cosine Similarity search on the 5 pre-loaded CS notes.
    """
    results = perform_semantic_search(request.query)
    return results


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
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
