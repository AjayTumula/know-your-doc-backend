from fastapi import APIRouter
from app.schemas.chat import Question, Answer
import random

router = APIRouter()

@router.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    responses = [
        "Our policy provides 15 days of paid leave annually.",
        "New hires receive equipment and onboarding materials in the first week.",
        "Health insurance covers medical, dental, and vision.",
        "Remote work is allowed 3 days per week.",
        "Expenses must be submitted within 30 days."
    ]
    return Answer(
        answer=random.choice(responses),
        sources=["Employee Handbook.pdf", "PolicyDoc.txt"],
        confidence=0.92
    )
