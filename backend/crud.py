from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models import Student, Course
from backend.schemas import StudentCreate, StudentUpdateAge, CourseCreate, CourseUpdate


# ============================================================================
# STUDENT CRUD OPERATIONS
# ============================================================================

def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Fetch a single student by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Fetch a single student by unique email address."""
    return db.query(Student).filter(Student.email == email).first()


def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
    """Fetch all students with optional pagination."""
    return db.query(Student).offset(skip).limit(limit).all()


def create_student(db: Session, student: StudentCreate) -> Student:
    """Create and persist a new Student record."""
    db_student = Student(
        name=student.name,
        email=student.email,
        age=student.age
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student_age(db: Session, student_id: int, age: int) -> Optional[Student]:
    """Update age attribute for a student profile."""
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    db_student.age = age
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    """Delete a student record by ID."""
    db_student = get_student(db, student_id)
    if not db_student:
        return False
    db.delete(db_student)
    db.commit()
    return True


# ============================================================================
# COURSE CRUD OPERATIONS
# ============================================================================

def get_course(db: Session, course_id: int) -> Optional[Course]:
    """Fetch a single course by primary key ID."""
    return db.query(Course).filter(Course.id == course_id).first()


def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    """Fetch all courses with optional pagination."""
    return db.query(Course).offset(skip).limit(limit).all()


def get_courses_by_student(db: Session, student_id: int) -> List[Course]:
    """Fetch all courses associated with a specific student."""
    return db.query(Course).filter(Course.student_id == student_id).all()


def create_course(db: Session, course: CourseCreate) -> Course:
    """Create and persist a new Course record."""
    db_course = Course(
        code=course.code,
        title=course.title,
        description=course.description,
        student_id=course.student_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def update_course(db: Session, course_id: int, course_update: CourseUpdate) -> Optional[Course]:
    """Update fields of an existing course record."""
    db_course = get_course(db, course_id)
    if not db_course:
        return None
    
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)

    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int) -> bool:
    """Delete a course record by ID."""
    db_course = get_course(db, course_id)
    if not db_course:
        return False
    db.delete(db_course)
    db.commit()
    return True
