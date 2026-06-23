from fastapi import APIRouter

from backend.services.db_service import db_service

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{user_id}")
async def get_history(user_id: str):
    sessions = await db_service.get_user_history(user_id)
    return sessions


@router.post("/{user_id}")
async def save_session_endpoint(user_id: str, topic: str, question_id: str, score: int | None = None):
    session_id = await db_service.save_session(user_id, topic, question_id, score)
    return {"session_id": session_id}
