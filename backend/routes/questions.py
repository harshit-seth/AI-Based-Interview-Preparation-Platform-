from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    HintRequest,
    HintResponse,
    Question,
    QuestionCreate,
    QuestionResponse,
    SolutionRequest,
    SolutionResponse,
)
from backend.services.db_service import db_service
from backend.services.llm_service import llm_service
from backend.services.rag_service import get_rag_service

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/")
async def list_questions(
    topic: str | None = None,
    difficulty: str | None = None,
    limit: int = 20,
):
    query = {}
    if topic:
        query["topic"] = topic
    if difficulty:
        query["difficulty"] = difficulty
    return await db_service.find_many("questions", query, limit)


@router.get("/{question_id}")
async def get_question(question_id: str):
    question = await db_service.find_one("questions", {"_id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post("/", response_model=QuestionResponse, status_code=201)
async def create_question(payload: QuestionCreate):
    doc = payload.model_dump()
    question_id = await db_service.insert_one("questions", doc)
    get_rag_service().add_documents(
        ids=[question_id],
        texts=[f"{payload.title}: {payload.description}"],
        metadatas=[{"difficulty": payload.difficulty, "topic": payload.topic}],
    )
    return {**doc, "id": question_id}


@router.post("/{question_id}/hint", response_model=HintResponse)
async def get_hint(question_id: str, payload: HintRequest):
    question = await db_service.find_one("questions", {"_id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    context = get_rag_service().query(query_text=question["title"], n_results=3)
    context_text = "\n".join([c["document"] for c in context])

    system_prompt = "You are a helpful DSA interview tutor. Provide a subtle hint without giving away the full solution."
    user_prompt = f"Question: {question['title']}\n{question['description']}\n\nUser's current code:\n{payload.user_code or 'No code yet'}"
    hint = await llm_service.generate_with_context(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        context=context_text,
        max_tokens=500,
        temperature=0.5,
    )
    return HintResponse(question_id=question_id, hint=hint)


@router.post("/{question_id}/solution", response_model=SolutionResponse)
async def get_solution(question_id: str, payload: SolutionRequest):
    question = await db_service.find_one("questions", {"_id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    context = get_rag_service().query(query_text=question["title"], n_results=3)
    context_text = "\n".join([c["document"] for c in context])

    system_prompt = "You are a DSA expert. Provide a well-documented solution with complexity analysis."
    user_prompt = f"Question: {question['title']}\n{question['description']}\nLanguage: {payload.language}"
    solution = await llm_service.generate_with_context(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        context=context_text,
        max_tokens=1500,
        temperature=0.3,
    )
    return SolutionResponse(
        question_id=question_id,
        solution_code=solution,
        explanation="",
        time_complexity="",
        space_complexity="",
    )
