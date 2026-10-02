
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.clause import Clause
from app.models.document_chunk import DocumentChunk


def build_analysis(
    db: Session,
    document_id: int,
    clauses: list[Clause],
    summary: str = "",
    recommendations: list[str] | None = None,
) -> Analysis:

    weights = {
        "LOW": 25,
        "MEDIUM": 55,
        "HIGH": 80,
        "CRITICAL": 95,
    }

    if clauses:
        overall = round(
            sum(
                weights.get(c.risk_level, 25)
                for c in clauses
            )
            / len(clauses)
        )
    else:
        overall = 0

    categories = defaultdict(list)

    for clause in clauses:
        categories[clause.category].append(
            weights.get(clause.risk_level, 25)
        )

    risks = [
        {
            "category": category,
            "level": _level_from_score(
                round(sum(scores) / len(scores))
            ),
            "score": round(sum(scores) / len(scores)),
        }
        for category, scores in categories.items()
    ]

    analysis = Analysis(
        document_id=document_id,
        overall_score=overall,
        risks=risks,
        summary=summary,
        recommendations=recommendations or [],
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


def _level_from_score(score: int) -> str:
    if score >= 90:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"