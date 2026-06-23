import os
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.config import settings
from app.database.mysql import get_db
from app.database.models import Document as DBDocument, DocumentChunk as DBDocumentChunk
from app.auth.dependencies import get_current_user
from app.services.document_service import DocumentService
from app.loaders.youtube_loader import load_youtube

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


class YoutubeUploadRequest(BaseModel):
    url_or_id: str


def extract_youtube_id(url_or_id: str) -> str:
    match = re.search(
        r'(?:v=|\/embed\/|\/1\/|\/v\/|https:\/\/youtu\.be\/)([a-zA-Z0-9_-]{11})',
        url_or_id
    )
    if match:
        return match.group(1)
    # Check if it matches exactly 11 characters video ID
    if len(url_or_id) == 11:
        return url_or_id
    return url_or_id


@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process PDF, PPT, TXT documents.
    """
    user_id = current_user["user_id"]

    try:
        allowed_extensions = [
            ".pdf",
            ".ppt",
            ".pptx",
            ".txt"
        ]

        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, PPT, PPTX and TXT files are allowed."
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(
            settings.UPLOAD_DIR,
            filename
        )

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process and index the document
        doc_service = DocumentService()
        result = doc_service.process_document(
            user_id=user_id,
            document_name=file.filename,
            file_path=file_path
        )

        return {
            "success": True,
            "filename": filename,
            "file_path": file_path,
            "document_id": result.get("document_id"),
            "pages": result.get("pages"),
            "chunks": result.get("chunks"),
            "message": "File uploaded and processed successfully."
        }

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload and processing failed: {str(e)}"
        )


@router.post("/youtube")
async def import_youtube_transcript(
    request: YoutubeUploadRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch and index transcript from YouTube URL or Video ID.
    """
    user_id = current_user["user_id"]
    video_id = extract_youtube_id(request.url_or_id)

    try:
        # Load the transcript
        documents = load_youtube(video_id)
        
        # Process and index
        doc_service = DocumentService()
        result = doc_service.process_document(
            user_id=user_id,
            document_name=f"YouTube_{video_id}",
            documents=documents
        )

        return {
            "success": True,
            "video_id": video_id,
            "document_id": result.get("document_id"),
            "chunks": result.get("chunks"),
            "message": "YouTube transcript downloaded and indexed successfully."
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch YouTube transcript: {str(e)}"
        )


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all uploaded documents for the user.
    """
    user_id = current_user["user_id"]
    docs = db.query(DBDocument).filter(DBDocument.user_id == user_id).all()
    
    # Structure response
    return [
        {
            "id": doc.id,
            "document_name": doc.document_name,
            "document_type": doc.document_type,
            "total_pages": doc.total_pages,
            "uploaded_at": doc.uploaded_at
        }
        for doc in docs
    ]


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a document, its metadata, local files, and ChromaDB chunks.
    """
    user_id = current_user["user_id"]
    doc = db.query(DBDocument).filter(
        DBDocument.id == document_id,
        DBDocument.user_id == user_id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get all chunk chroma IDs
    chunks = db.query(DBDocumentChunk).filter(
        DBDocumentChunk.document_id == document_id
    ).all()
    chroma_ids = [chunk.chroma_id for chunk in chunks]

    # Delete from ChromaDB
    if chroma_ids:
        try:
            from app.services.vector_service import VectorService
            vector_service = VectorService()
            vector_service.vector_store.delete(ids=chroma_ids)
        except Exception as e:
            # We log but continue DB deletion in case vector delete fails
            print(f"ChromaDB deletion error: {e}")

    # Remove local file
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"File removal error: {e}")

    # Delete records from MySQL
    db.query(DBDocumentChunk).filter(DBDocumentChunk.document_id == document_id).delete()
    db.delete(doc)
    db.commit()

    return {
        "success": True,
        "message": f"Document '{doc.document_name}' deleted successfully."
    }