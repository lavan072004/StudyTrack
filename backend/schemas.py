from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ----------------------------------------------------
# Course Pydantic Schemas
# ----------------------------------------------------

class CourseBase(BaseModel):
    course_name: str = Field(..., min_length=1, example="Data Structures & Algorithms")
    credits: int = Field(..., ge=1, le=6, example=4)
    student_id: Optional[int] = Field(None, example=1)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_name: Optional[str] = Field(None, min_length=1, example="Advanced Data Structures")
    credits: Optional[int] = Field(None, ge=1, le=6, example=4)
    student_id: Optional[int] = Field(None, example=1)


class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# Student Pydantic Schemas
# ----------------------------------------------------

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, example="Aditi Rao")
    email: str = Field(..., example="aditi@example.com")
    age: int = Field(..., gt=0, example=20)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or "@" not in v:
            raise ValueError("Email must contain '@'")
        return v


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[str] = Field(None)
    age: Optional[int] = Field(None, gt=0)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and "@" not in v:
            raise ValueError("Email must contain '@'")
        return v


class StudentResponse(StudentBase):
    id: int
    courses: List[CourseResponse] = []

    class Config:
        from_attributes = True


# ----------------------------------------------------
# AI Assistant Pydantic Schemas
# ----------------------------------------------------

class SummarizerRequest(BaseModel):
    text: Optional[str] = Field("", example="Insertion sort builds a sorted list element by element.")


class SummarizerResponse(BaseModel):
    topic: str
    key_points: List[str]
    difficulty: str


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    score: float
