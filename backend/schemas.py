from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


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

    class Config:
        from_attributes = True


class SummarizerRequest(BaseModel):
    text: str = Field(..., min_length=5, example="Binary search is an efficient algorithm for finding an item from a sorted list of items. It works by repeatedly dividing in half the portion of the list that could contain the item.")


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
