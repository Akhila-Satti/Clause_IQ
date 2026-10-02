from pydantic import BaseModel


class ClauseQuestionRequest(BaseModel):
    question: str


class ClauseQuestionResponse(BaseModel):
    answer: str
    clause_id: str
    section: str
    title: str