from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.mysql import Base


# ==========================================
# Users
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    subjects = relationship(
        "Subject",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ==========================================
# Subjects
# ==========================================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    subject_name = Column(
        String(255),
        nullable=False
    )

    description = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="subjects"
    )

    documents = relationship(
        "Document",
        back_populates="subject",
        cascade="all, delete-orphan"
    )


# ==========================================
# Documents
# ==========================================

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id")
    )

    document_name = Column(String(255))

    file_path = Column(Text)

    document_type = Column(String(50))

    total_pages = Column(Integer)

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="documents"
    )

    subject = relationship(
        "Subject",
        back_populates="documents"
    )


# ==========================================
# Document Chunks
# ==========================================

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id")
    )

    chunk_index = Column(Integer)

    page_number = Column(Integer)

    chroma_id = Column(String(255))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# Chat Sessions
# ==========================================

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan"
    )


# ==========================================
# Chat Messages
# ==========================================

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)

    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id")
    )

    role = Column(String(20))

    message = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    session = relationship(
        "ChatSession",
        back_populates="messages"
    )


# ==========================================
# Learning Memory
# ==========================================

class LearningMemory(Base):
    __tablename__ = "learning_memory"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    topic = Column(String(255))

    mastery_level = Column(Float)

    confidence_score = Column(Float)

    last_revision = Column(DateTime)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# Quiz Results
# ==========================================

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    topic = Column(String(255))

    score = Column(Float)

    total_questions = Column(Integer)

    completed_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# Flashcards
# ==========================================

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    topic = Column(String(255))

    question = Column(Text)

    answer = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# Revision Plans
# ==========================================

class RevisionPlan(Base):
    __tablename__ = "revision_plans"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    topic = Column(String(255))

    plan = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )