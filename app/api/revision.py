from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.graph.study_graph import run_study_graph
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/revision",
    tags=["Revision"]
)


class RevisionRequest(BaseModel):
    topic: str
    days: int = 5


@router.post("/")
async def generate_revision_plan(
    request: RevisionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate study revision schedule from uploaded study materials.
    """
    user_id = current_user["user_id"]

    try:
        result = run_study_graph(
            question=f"Generate {request.days} days revision plan for: {request.topic}",
            user_id=user_id,
            action="revision",
            topic=request.topic
        )

        return {
            "success": True,
            "topic": request.topic,
            "revision_plan": result.get("revision_plan", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Revision plan generation failed: {str(e)}"
        )