from pydantic import BaseModel


class SourceClause(BaseModel):
    clause_id: str
    section: str
    title: str
    category: str
    text: str


class AskQuestionRequest(BaseModel):
    question: str


class AskQuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceClause]