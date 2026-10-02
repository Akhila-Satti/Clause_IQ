from pydantic import BaseModel


class RiskResponse(BaseModel):
    category: str
    level: str
    score: int


class ClauseResponse(BaseModel):
    id: str
    section: str
    title: str
    category: str
    riskLevel: str
    text: str
    explanation: str
    summary: str
    risks: list[str]
    obligations: list[str]


class AnalysisResponse(BaseModel):
    summary: str
    overallScore: int
    risks: list[RiskResponse]
    recommendations: list[str]
    clauses: list[ClauseResponse]