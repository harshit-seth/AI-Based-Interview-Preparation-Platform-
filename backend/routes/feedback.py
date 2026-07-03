from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.code_templates import get_language_prompt
from backend.models.schemas import FeedbackRequest, FeedbackResponse
from backend.services.db_service import db_service
from backend.services.llm_service import llm_service

router = APIRouter(prefix="/feedback", tags=["feedback"])


class BatchEvalItem(BaseModel):
    question_id: str
    title: str
    description: str
    answer: str


class BatchEvalRequest(BaseModel):
    language: str = "python"
    items: list[BatchEvalItem]


class BatchEvalResult(BaseModel):
    question_id: str
    score: int
    feedback: str


class BatchEvalResponse(BaseModel):
    results: list[BatchEvalResult]


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
    question = await db_service.find_one(
        "questions", {"_id": payload.question_id}
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    lang_prompt = get_language_prompt(payload.language)
    system_prompt = (
        "You are an experienced coding interview coach. "
        "Review the user's code and provide constructive feedback, "
        "suggestions for improvement, and a rating out of 10. "
        f"{lang_prompt}"
    )
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


@router.post("/batch-eval", response_model=BatchEvalResponse)
async def batch_eval(payload: BatchEvalRequest):
    results = []
    for item in payload.items:
        system_prompt = (
            "You are an experienced coding interview coach. "
            "Rate the user's answer out of 10 and provide brief feedback. "
            "Start your response with 'Rating: X/10' on the first line."
        )
        user_prompt = (
            f"Question: {item.title}\n{item.description}\n\n"
            f"User's answer ({payload.language}):\n{item.answer}"
        )
        feedback_text = await llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=300,
            temperature=0.4,
        )
        score = 0
        first_line = feedback_text.split("\n")[0] if feedback_text else ""
        import re
        match = re.search(r"(\d+)/10", first_line)
        if match:
            score = int(match.group(1)) * 10
        results.append(
            BatchEvalResult(question_id=item.question_id, score=score, feedback=feedback_text)
        )
    return BatchEvalResponse(results=results)
