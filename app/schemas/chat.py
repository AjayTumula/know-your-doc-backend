from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    question: str
    top_k: int = 3

class Answer(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
