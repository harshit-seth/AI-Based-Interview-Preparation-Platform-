from fastapi import APIRouter, HTTPException

from backend.models.schemas import FeedbackRequest, FeedbackResponse
from backend.services.db_service import db_service
from backend.services.llm_service import llm_service

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
    question = await db_service.find_one(
        "questions", {"_id": payload.question_id}
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    system_prompt = "You are an experienced coding interview coach. Review the user's code and provide constructive feedback, suggestions for improvement, and a rating out of 10."
    user_prompt = f"""Question: {question['title']}
Description: {question['description']}

User's code ({payload.language}):
{payload.user_code}

Provide:
1. Overall feedback on correctness, efficiency, and style.
2. Specific suggestions for improvement.
3. A rating out of 10."""

    feedback_text = await llm_service.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=1000,
        temperature=0.4,
    )
    return FeedbackResponse(
        question_id=payload.question_id,
        feedback=feedback_text,
        suggestions=[],
        rating=None,
    )


@router.get("/history/{question_id}", response_model=list[FeedbackResponse])
async def get_feedback_history(question_id: str):
    feedbacks = await db_service.find_many(
        "feedback", {"question_id": question_id}
    )
    return feedbacks
