from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from app.graph.study_graph import run_study_graph
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/summary",
    tags=["Summary"]
)


class SummaryRequest(BaseModel):
    topic: str


@router.post("/")
async def generate_summary(
    request: SummaryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate an AI-powered summary for a topic based on study materials.
    """
    user_id = current_user["user_id"]

    try:
        result = run_study_graph(
            question=f"Generate a detailed summary for: {request.topic}",
            user_id=user_id,
            action="summary",
            topic=request.topic
        )

        return {
            "success": True,
            "topic": request.topic,
            "summary": result.get("summary", "Failed to generate summary.")
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {str(e)}"
        )