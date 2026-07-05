from fastapi import APIRouter, HTTPException

from backend.code_templates import get_boilerplate, get_language_prompt
from backend.models.schemas import (
    GeneratedQuestion,
    GenerateQuestionRequest,
    GenerateQuestionResponse,
    HintRequest,
    HintResponse,
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

    system_prompt = (
        "You are a helpful DSA interview tutor. "
        "Provide a subtle hint without giving away the full solution."
    )
    user_prompt = (
        f"Question: {question['title']}\n{question['description']}\n\n"
        f"User's current code:\n{payload.user_code or 'No code yet'}"
    )
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

    lang_prompt = get_language_prompt(payload.language)
    boilerplate = get_boilerplate(payload.language)
    system_prompt = (
        "You are a DSA expert. "
        "Provide a well-documented solution with complexity analysis. "
        f"{lang_prompt}"
    )
    user_prompt = (
        f"Question: {question['title']}\n{question['description']}\n"
        f"Language: {payload.language}\n\n"
        f"Provide the complete {payload.language} solution. "
        f"Here is a starting template:\n{boilerplate}"
    )
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


@router.post("/generate", response_model=GenerateQuestionResponse)
async def generate_questions(payload: GenerateQuestionRequest):
    import json

    system_prompt = (
        "You are an expert DSA question creator. "
        "Generate high-quality interview questions with detailed specifications. "
        "Respond ONLY with a valid JSON array of objects, no markdown or explanation."
    )
    user_prompt = (
        f"Generate {payload.count} DSA interview questions about {payload.topic.value}. "
        f"Difficulty: {payload.difficulty.value}. "
        f"{payload.additional_instructions}\n\n"
        f"Each question must have these fields:\n"
        f"- title (short title)\n"
        f"- description (detailed description with examples)\n"
        f"- difficulty ({payload.difficulty.value})\n"
        f"- topic ({payload.topic.value})\n"
        f"- example_input (optional)\n"
        f"- example_output (optional)\n"
        f"- constraints (optional)\n"
        f"- solution_approach (brief approach hint)\n\n"
        f"Return as JSON array."
    )
    response_text = await llm_service.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=2000,
        temperature=0.8,
    )
    try:
        raw = response_text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return GenerateQuestionResponse(questions=[])

    questions = []
    for item in data[: payload.count]:
        constraints = item.get("constraints")
        if isinstance(constraints, list):
            constraints = "\n".join(constraints)
        questions.append(
            GeneratedQuestion(
                title=item.get("title", "Untitled"),
                description=item.get("description", ""),
                difficulty=payload.difficulty,
                topic=payload.topic,
                example_input=item.get("example_input"),
                example_output=item.get("example_output"),
                constraints=constraints,
                solution_approach=item.get("solution_approach"),
            )
        )
    return GenerateQuestionResponse(questions=questions)
