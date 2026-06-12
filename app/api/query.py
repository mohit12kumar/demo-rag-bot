from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from app.graph.study_graph import run_study_graph
from app.services.groq_service import GroqService
from app.rag.retriever import retrieve_documents
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


class QueryRequest(BaseModel):
    question: str
    user_id: int
    document_id: Optional[int] = None


class CompareRequest(BaseModel):
    concept1: str
    concept2: str
    user_id: int


@router.post("/")
async def query_documents(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Query uploaded study materials with subject and document level filtering.
    """
    user_id = current_user["user_id"]
    try:
        result = run_study_graph(
            question=request.question,
            user_id=user_id,
            document_id=request.document_id
        )

        return {
            "success": True,
            "question": request.question,
            "answer": result.get("answer"),
            "citations": result.get("citations", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )


@router.post("/compare")
async def compare_concepts(
    request: CompareRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Compare and contrast two concepts across uploaded study materials.
    """
    user_id = current_user["user_id"]
    try:
        # Retrieve documents for both concepts and merge them
        docs1 = retrieve_documents(
            query=request.concept1,
            user_id=user_id,
            k=4
        )
        docs2 = retrieve_documents(
            query=request.concept2,
            user_id=user_id,
            k=4
        )
        
        # Merge list and remove duplicate chunks
        merged_docs = []
        seen_contents = set()
        
        for doc in docs1 + docs2:
            if doc.page_content not in seen_contents:
                seen_contents.add(doc.page_content)
                merged_docs.append(doc)
                
        if not merged_docs:
            return {
                "success": True,
                "comparison": f"No study materials found regarding '{request.concept1}' or '{request.concept2}' to perform a comparison."
            }

        context_str = "\n\n".join(
            f"Source: {doc.metadata.get('source', 'Document')} (Page {doc.metadata.get('page', 1)}):\n{doc.page_content}"
            for doc in merged_docs
        )

        prompt = f"""
You are an expert academic assistant.
Based on the study materials context below, compare and contrast the following two concepts: "{request.concept1}" and "{request.concept2}".
Provide a clear comparison in a Markdown table comparing their definitions, key features, use cases, pros, and cons.
Following the table, write a concise summary of when to use each concept.

Context:
{context_str}

Comparison:
"""

        groq_service = GroqService()
        comparison = groq_service.generate_response(prompt)

        return {
            "success": True,
            "concept1": request.concept1,
            "concept2": request.concept2,
            "comparison": comparison.strip()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )