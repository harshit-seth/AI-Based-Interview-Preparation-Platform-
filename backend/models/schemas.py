from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Topic(StrEnum):
    ARRAYS = "arrays"
    STRINGS = "strings"
    LINKED_LIST = "linked_list"
    TREES = "trees"
    GRAPHS = "graphs"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    RECURSION = "recursion"
    SORTING = "sorting"
    SEARCHING = "searching"
    HASHING = "hashing"
    STACKS_QUEUES = "stacks_queues"
    HEAP = "heap"


class Question(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: str
    difficulty: Difficulty
    topic: Topic
    example_input: str | None = None
    example_output: str | None = None
    constraints: str | None = None
    solution_approach: str | None = None
    code_snippet: str | None = None
    tags: list[str] = []

    model_config = {"populate_by_name": True}


class QuestionCreate(BaseModel):
    title: str
    description: str
    difficulty: Difficulty
    topic: Topic
    example_input: str | None = None
    example_output: str | None = None
    constraints: str | None = None
    solution_approach: str | None = None
    code_snippet: str | None = None
    tags: list[str] = []


class QuestionResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: Difficulty
    topic: Topic
    example_input: str | None = None
    example_output: str | None = None
    constraints: str | None = None
    tags: list[str] = []


class FeedbackRequest(BaseModel):
    question_id: str
    user_code: str
    language: str = "python"


class FeedbackResponse(BaseModel):
    question_id: str
    feedback: str
    suggestions: list[str] = []
    rating: int | None = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HintRequest(BaseModel):
    question_id: str
    user_code: str | None = None


class HintResponse(BaseModel):
    question_id: str
    hint: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class SolutionRequest(BaseModel):
    question_id: str
    language: str = "python"


class SolutionResponse(BaseModel):
    question_id: str
    solution_code: str
    explanation: str
    time_complexity: str
    space_complexity: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class GenerateQuestionRequest(BaseModel):
    topic: Topic
    difficulty: Difficulty
    count: int = 3
    additional_instructions: str = ""


class GeneratedQuestion(BaseModel):
    title: str
    description: str
    difficulty: Difficulty
    topic: Topic
    example_input: str | None = None
    example_output: str | None = None
    constraints: str | list[str] | None = None
    solution_approach: str | None = None


class GenerateQuestionResponse(BaseModel):
    questions: list[GeneratedQuestion]
