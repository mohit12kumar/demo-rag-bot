from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ==================================
# User Schemas
# ==================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


# ==================================
# Subject Schemas
# ==================================

class SubjectCreate(BaseModel):
    subject_name: str
    description: Optional[str] = None


class SubjectResponse(BaseModel):
    id: int
    subject_name: str
    description: Optional[str]

    class Config:
        from_attributes = True


# ==================================
# Document Schemas
# ==================================

class DocumentResponse(BaseModel):
    id: int
    document_name: str
    file_path: str
    document_type: str
    total_pages: Optional[int]

    class Config:
        from_attributes = True


# ==================================
# Query Schemas
# ==================================

class QueryRequest(BaseModel):
    user_id: int
    question: str


class Citation(BaseModel):
    document: str
    page: int


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]


# ==================================
# Summary Schemas
# ==================================

class SummaryRequest(BaseModel):
    topic: str


class SummaryResponse(BaseModel):
    topic: str
    summary: str


# ==================================
# Flashcard Schemas
# ==================================

class FlashcardItem(BaseModel):
    question: str
    answer: str


class FlashcardRequest(BaseModel):
    topic: str


class FlashcardResponse(BaseModel):
    topic: str
    flashcards: List[FlashcardItem]


# ==================================
# Quiz Schemas
# ==================================

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str


class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5


class QuizResponse(BaseModel):
    topic: str
    quiz: List[QuizQuestion]


# ==================================
# Revision Schemas
# ==================================

class RevisionRequest(BaseModel):
    topic: str
    days: int = 7


class RevisionTask(BaseModel):
    day: int
    task: str


class RevisionResponse(BaseModel):
    topic: str
    revision_plan: List[RevisionTask]


# ==================================
# Learning Memory Schemas
# ==================================

class MemoryResponse(BaseModel):
    topic: str
    mastery_level: float
    confidence_score: float
    last_revision: Optional[datetime]

    class Config:
        from_attributes = True