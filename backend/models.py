from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    age = Column(Integer, nullable=False)

    # 1-to-Many Relationship: One Student can have multiple Courses
    courses = relationship("Course", back_populates="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "courses": [course.to_dict() for course in self.courses] if self.courses else []
        }


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String, nullable=False, index=True)
    credits = Column(Integer, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True)

    # Relationship to Student model
    student = relationship("Student", back_populates="courses")

    def to_dict(self):
        return {
            "id": self.id,
            "course_name": self.course_name,
            "credits": self.credits,
            "student_id": self.student_id
        }
