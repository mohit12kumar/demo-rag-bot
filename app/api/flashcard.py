from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.graph.study_graph import run_study_graph
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/flashcards",
    tags=["Flashcards"]
)


class FlashcardRequest(BaseModel):
    topic: str


@router.post("/")
async def generate_flashcards(
    request: FlashcardRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate study flashcards for a topic based on study materials.
    """
    user_id = current_user["user_id"]

    try:
        result = run_study_graph(
            question=f"Generate flashcards for: {request.topic}",
            user_id=user_id,
            action="flashcard",
            topic=request.topic
        )

        return {
            "success": True,
            "topic": request.topic,
            "flashcards": result.get("flashcards", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Flashcards generation failed: {str(e)}"
        )