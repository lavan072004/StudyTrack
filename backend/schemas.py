from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ----------------------------------------------------
# Course Pydantic Schemas
# ----------------------------------------------------

class CourseBase(BaseModel):
    code: str = Field(..., min_length=2, example="CS101")
    title: str = Field(..., min_length=2, example="Data Structures & Algorithms")
    description: Optional[str] = Field(None, example="Introduction to fundamental data structures.")
    student_id: Optional[int] = Field(None, example=1)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=2, example="CS101")
    title: Optional[str] = Field(None, min_length=2, example="Advanced Data Structures")
    description: Optional[str] = Field(None, example="Updated course description.")
    student_id: Optional[int] = Field(None, example=1)


class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# Student Pydantic Schemas
# ----------------------------------------------------

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, example="Rohan")
    email: str = Field(..., example="rohan@example.com")
    age: int = Field(..., ge=1, le=120, example=20)


class StudentCreate(StudentBase):
    pass


class StudentUpdateAge(BaseModel):
    age: int = Field(..., ge=1, le=120, example=21)


class StudentResponse(StudentBase):
    id: int
    courses: List[CourseResponse] = []

    class Config:
        from_attributes = True


# ----------------------------------------------------
# AI Feature Pydantic Schemas
# ----------------------------------------------------

class SummarizerRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=5,
        example="Binary search is an efficient algorithm for finding an item from a sorted list of items. It works by repeatedly dividing in half the portion of the list that could contain the item."
    )


class SummarizerResponse(BaseModel):
    topic: str
    key_points: List[str]
    difficulty: str


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, example="What is binary search algorithm?")


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    similarity_score: float


class AIHelperRequest(BaseModel):
    prompt: str = Field(..., min_length=2, example="How can I prepare for my Data Structures exam?")
    context: Optional[str] = Field(None, example="Student Rohan enrolled in CS101")


class AIHelperResponse(BaseModel):
    query: str
    response: str
    suggestions: List[str]
    timestamp: str
