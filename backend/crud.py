from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models import Student, Course
from backend.schemas import StudentCreate, StudentUpdate, CourseCreate, CourseUpdate


# ============================================================================
# STUDENT CRUD OPERATIONS
# ============================================================================

def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Fetch a single student by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Fetch a single student by unique email address."""
    return db.query(Student).filter(Student.email == email).first()


def get_students(db: Session, min_age: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Student]:
    """
    Fetch students with optional min_age filter.
    If min_age is provided, return students whose age is greater than or equal to min_age.
    """
    query = db.query(Student)
    if min_age is not None:
        query = query.filter(Student.age >= min_age)
    return query.offset(skip).limit(limit).all()


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


def update_student(db: Session, student_id: int, student_update: StudentUpdate) -> Optional[Student]:
    """Update fields for a student profile via PATCH."""
    db_student = get_student(db, student_id)
    if not db_student:
        return None

    update_data = student_update.model_dump(exclude_unset=True) if hasattr(student_update, "model_dump") else student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_student, field, value)

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


def get_student_course_count(db: Session, student_id: int) -> int:
    """
    Database-level count() query for a student's enrolled courses.
    Requirement 9: Must use database-level count() query, NOT len(student.courses).
    """
    return db.query(Course).filter(Course.student_id == student_id).count()


# ============================================================================
# COURSE CRUD OPERATIONS
# ============================================================================

def get_course(db: Session, course_id: int) -> Optional[Course]:
    """Fetch a single course by primary key ID."""
    return db.query(Course).filter(Course.id == course_id).first()


def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    """Fetch all courses with optional pagination."""
    return db.query(Course).offset(skip).limit(limit).all()


def create_course(db: Session, course: CourseCreate) -> Course:
    """Create and persist a new Course record."""
    db_course = Course(
        course_name=course.course_name,
        credits=course.credits,
        student_id=course.student_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def update_course(db: Session, course_id: int, course_update: CourseUpdate) -> Optional[Course]:
    """Update fields of an existing course record via PATCH."""
    db_course = get_course(db, course_id)
    if not db_course:
        return None

    update_data = course_update.model_dump(exclude_unset=True) if hasattr(course_update, "model_dump") else course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
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
