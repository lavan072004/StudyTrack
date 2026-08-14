from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import Student, Course


def seed_database(db: Session) -> None:
    """
    Seeds initial student and course records into the SQLite database.
    Replaces old seed data with the exact 8 students specified in the assessment.
    """
    Base.metadata.create_all(bind=engine)

    if db.query(Student).count() == 0:
        print("[SEED] Seeding exact 8 Student records...")
        exact_students = [
            Student(name="Aditi Rao", email="aditi@example.com", age=20),
            Student(name="Rohan Mehta", email="rohan@example.com", age=19),
            Student(name="Kavya Nair", email="kavya@example.com", age=21),
            Student(name="Farhan Sheikh", email="farhan@example.com", age=20),
            Student(name="Priya Iyer", email="priya@example.com", age=22),
            Student(name="Devansh Gupta", email="devansh@example.com", age=23),
            Student(name="Meera Joshi", email="meera@example.com", age=18),
            Student(name="Sameer Khan", email="sameer@example.com", age=24),
        ]
        db.add_all(exact_students)
        db.commit()
        for s in exact_students:
            db.refresh(s)
        print(f"[SEED] Created {len(exact_students)} students.")

    if db.query(Course).count() == 0:
        print("[SEED] Seeding initial Course records...")
        students = db.query(Student).all()
        student_map = {s.name: s.id for s in students}

        exact_courses = [
            Course(
                course_name="Data Structures & Algorithms",
                credits=4,
                student_id=student_map.get("Rohan Mehta")
            ),
            Course(
                course_name="Web Application Development",
                credits=3,
                student_id=student_map.get("Farhan Sheikh")
            ),
            Course(
                course_name="Database Systems",
                credits=4,
                student_id=student_map.get("Priya Iyer")
            ),
            Course(
                course_name="Artificial Intelligence",
                credits=3,
                student_id=student_map.get("Aditi Rao")
            ),
            Course(
                course_name="Operating Systems",
                credits=4,
                student_id=student_map.get("Kavya Nair")
            ),
        ]
        db.add_all(exact_courses)
        db.commit()
        print(f"[SEED] Created {len(exact_courses)} courses.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
        print("[SEED] Database seeding completed successfully!")
    finally:
        db.close()
