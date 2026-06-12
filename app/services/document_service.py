import os

from app.loaders.pdf_loader import load_pdf
from app.loaders.ppt_loader import load_ppt
from app.loaders.notes_loader import load_notes

from app.rag.chunking import (
    chunk_documents
)

from app.services.vector_service import (
    VectorService
)


from typing import List, Optional
from langchain_core.documents import Document

from app.database.mysql import SessionLocal
from app.database.models import Document as DBDocument, DocumentChunk as DBDocumentChunk

class DocumentService:

    def __init__(self):

        self.vector_service = VectorService()

    def process_document(
        self,
        user_id: int,
        document_name: str,
        file_path: Optional[str] = None,
        documents: Optional[List[Document]] = None
    ):
        db = SessionLocal()
        try:
            if documents is None:
                if not file_path:
                    raise ValueError("Either file_path or documents must be provided")
                
                extension = os.path.splitext(file_path)[1].lower()

                # PDF
                if extension == ".pdf":
                    documents = load_pdf(file_path)

                # PPT
                elif extension in [".ppt", ".pptx"]:
                    documents = load_ppt(file_path)

                # TXT
                elif extension == ".txt":
                    documents = load_notes(file_path)

                else:
                    raise ValueError(f"Unsupported file type: {extension}")

            # Insert metadata into MySQL Document table
            total_pages = len(documents)
            db_doc = DBDocument(
                user_id=user_id,
                subject_id=None,
                document_name=document_name,
                file_path=file_path or f"youtube_{document_name}",
                document_type=os.path.splitext(file_path)[1].lower() if file_path else "youtube",
                total_pages=total_pages
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)

            # Chunk document contents
            chunks = chunk_documents(documents)

            chroma_documents = []
            for idx, chunk in enumerate(chunks):
                # Retrieve page/slide number
                page = chunk.metadata.get("page", chunk.metadata.get("slide", 1))
                if "page" in chunk.metadata:
                    try:
                        # PyPDFLoader returns 0-indexed page numbers. Let's make them 1-indexed.
                        page = int(page) + 1
                    except Exception:
                        pass
                
                # Add customized metadata fields for filtering
                chunk.metadata["user_id"] = user_id
                chunk.metadata["document_id"] = db_doc.id
                chunk.metadata["source"] = document_name
                chunk.metadata["page"] = page
                
                chroma_documents.append(chunk)

            # Ingest to ChromaDB and get generated IDs
            chroma_ids = self.vector_service.add_documents(chroma_documents)

            # Store chunk-to-vector mapping in MySQL
            for idx, chunk in enumerate(chroma_documents):
                chroma_id = chroma_ids[idx]
                page = chunk.metadata.get("page", 1)
                db_chunk = DBDocumentChunk(
                    document_id=db_doc.id,
                    chunk_index=idx,
                    page_number=page,
                    chroma_id=chroma_id
                )
                db.add(db_chunk)
            
            db.commit()

            return {
                "success": True,
                "document_id": db_doc.id,
                "document_name": document_name,
                "pages": total_pages,
                "chunks": len(chroma_documents)
            }

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()