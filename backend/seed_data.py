from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import Student, Course


def seed_database(db: Session) -> None:
    """
    Seeds initial student and course records into the SQLite database.
    Checks count to ensure idempotent operation.
    """
    # Create tables if not present
    Base.metadata.create_all(bind=engine)

    if db.query(Student).count() == 0:
        print("[SEED] Seeding initial Student records...")
        sample_students = [
            Student(name="Rohan", email="rohan@studytrack.io", age=19),
            Student(name="Farhan", email="farhan@studytrack.io", age=20),
            Student(name="Priya", email="priya@studytrack.io", age=21),
            Student(name="Aanya", email="aanya@studytrack.io", age=18),
            Student(name="Dev", email="dev@studytrack.io", age=22),
        ]
        db.add_all(sample_students)
        db.commit()
        for s in sample_students:
            db.refresh(s)
        print(f"[SEED] Created {len(sample_students)} students.")

    if db.query(Course).count() == 0:
        print("[SEED] Seeding initial Course records...")
        # Get first few students for foreign key mapping
        students = db.query(Student).all()
        student_map = {s.name: s.id for s in students}

        sample_courses = [
            Course(
                code="CS101",
                title="Data Structures & Algorithms",
                description="Comprehensive study of arrays, linked lists, sorting, and search algorithms.",
                student_id=student_map.get("Rohan")
            ),
            Course(
                code="CS102",
                title="Web Application Development",
                description="RESTful API design with FastAPI, SQLite ORM, and HTML5/CSS3/JS frontend.",
                student_id=student_map.get("Farhan")
            ),
            Course(
                code="CS103",
                title="Artificial Intelligence & NLP",
                description="Natural Language Processing fundamentals, TF-IDF vectorization, and Cosine Similarity.",
                student_id=student_map.get("Priya")
            ),
            Course(
                code="CS104",
                title="Database Systems",
                description="Relational database schema design, transactions, indexing, and SQLAlchemy ORM.",
                student_id=student_map.get("Aanya")
            ),
            Course(
                code="CS105",
                title="Software Engineering Principles",
                description="Clean architecture, design patterns, automated testing, and CI/CD pipelines.",
                student_id=student_map.get("Dev")
            ),
        ]
        db.add_all(sample_courses)
        db.commit()
        print(f"[SEED] Created {len(sample_courses)} courses.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
        print("[SEED] Database seeding completed successfully!")
    finally:
        db.close()
