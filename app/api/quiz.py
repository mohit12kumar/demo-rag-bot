from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.graph.study_graph import run_study_graph
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)


class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5


@router.post("/")
async def generate_quiz(
    request: QuizRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate MCQ quiz for a given topic from uploaded study materials.
    """
    user_id = current_user["user_id"]

    try:
        result = run_study_graph(
            question=f"Generate {request.num_questions} questions multiple-choice quiz for: {request.topic}",
            user_id=user_id,
            action="quiz",
            topic=request.topic
        )

        return {
            "success": True,
            "topic": request.topic,
            "quiz": result.get("quiz", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quiz generation failed: {str(e)}"
        )