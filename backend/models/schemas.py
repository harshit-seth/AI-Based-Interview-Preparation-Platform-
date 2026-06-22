from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Topic(str, Enum):
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
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    constraints: Optional[str] = None
    solution_approach: Optional[str] = None
    code_snippet: Optional[str] = None
    tags: list[str] = []

    class Config:
        populate_by_name = True


class QuestionCreate(BaseModel):
    title: str
    description: str
    difficulty: Difficulty
    topic: Topic
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    constraints: Optional[str] = None
    solution_approach: Optional[str] = None
    code_snippet: Optional[str] = None
    tags: list[str] = []


class QuestionResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: Difficulty
    topic: Topic
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    constraints: Optional[str] = None
    tags: list[str] = []


class FeedbackRequest(BaseModel):
    question_id: str
    user_code: str
    language: str = "python"


class FeedbackResponse(BaseModel):
    question_id: str
    feedback: str
    suggestions: list[str] = []
    rating: Optional[int] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HintRequest(BaseModel):
    question_id: str
    user_code: Optional[str] = None


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
