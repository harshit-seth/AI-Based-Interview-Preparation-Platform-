from fastapi import APIRouter, Depends

from backend.routes.auth import get_current_user
from backend.services.db_service import db_service

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/")
async def get_history(user: dict = Depends(get_current_user)):
    sessions = await db_service.get_user_history(str(user["_id"]))
    return sessions


@router.post("/")
async def save_session_endpoint(
    topic: str,
    question_id: str,
    score: int | None = None,
    user: dict = Depends(get_current_user),
):
    session_id = await db_service.save_session(str(user["_id"]), topic, question_id, score)
    return {"session_id": session_id}
