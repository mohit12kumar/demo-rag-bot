from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Database
from app.database.mysql import engine
from app.database.models import Base

# API Routers
from app.api.auth import router as auth_router
from app.api.upload import router as upload_router
from app.api.query import router as query_router
from app.api.summary import router as summary_router
from app.api.flashcard import router as flashcard_router
from app.api.quiz import router as quiz_router
from app.api.revision import router as revision_router



# ==========================================
# Lifespan Events
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("=" * 60)
    print("Starting AI Study Library...")
    print("=" * 60)

    # Create MySQL Tables
    Base.metadata.create_all(bind=engine)

    print("Database Connected")
    print("Application Ready")

    yield

    print("=" * 60)
    print("Stopping AI Study Library...")
    print("=" * 60)


# ==========================================
# FastAPI App
# ==========================================

app = FastAPI(
    title="AI Study Library",
    description="Multi-Document RAG Study Assistant using LangGraph, ChromaDB and Groq",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# CORS Configuration
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Register Routers
# ==========================================

app.include_router(auth_router)

app.include_router(upload_router)
app.include_router(query_router)

app.include_router(summary_router)
app.include_router(flashcard_router)
app.include_router(quiz_router)
app.include_router(revision_router)


# ==========================================
# Root Endpoint
# ==========================================

@app.get("/")
async def root():

    return {
        "success": True,
        "application": "AI Study Library",
        "version": "1.0.0",
        "status": "running"
    }


# ==========================================
# Health Check
# ==========================================

@app.get("/health")
async def health_check():

    return {
        "success": True,
        "status": "healthy",
        "database": "connected",
        "vector_store": "ready"
    }


# ==========================================
# Version Endpoint
# ==========================================

@app.get("/version")
async def version():

    return {
        "application": "AI Study Library",
        "version": "1.0.0"
    }


# ==========================================
# Protected Test Endpoint
# ==========================================

@app.get("/protected")
async def protected():

    return {
        "message": "JWT Authentication Working"
    }