import re

from sqlalchemy.orm import Session

from app.models.clause import Clause
from pgvector.sqlalchemy import Vector
from app.services.embedding_service import generate_embedding


def tokenize(text: str) -> set[str]:
    """
    Convert text into simple normalized keywords.

    Kept as a fallback retrieval mechanism.
    """
    return set(
        re.findall(
            r"\b[a-zA-Z0-9]{3,}\b",
            text.lower(),
        )
    )


def score_clause(
    question: str,
    clause: Clause,
) -> int:
    """
    Calculate a simple keyword relevance score.

    This is used only as a fallback when vector
    retrieval does not return useful results.
    """

    question_words = tokenize(question)

    clause_text = " ".join(
        [
            clause.section or "",
            clause.title or "",
            clause.category or "",
            clause.text or "",
            clause.summary or "",
        ]
    )

    clause_words = tokenize(clause_text)

    if not question_words or not clause_words:
        return 0

    matches = question_words.intersection(clause_words)

    score = len(matches)

    title_words = tokenize(clause.title or "")
    category_words = tokenize(clause.category or "")

    score += len(
        question_words.intersection(title_words)
    ) * 3

    score += len(
        question_words.intersection(category_words)
    ) * 2

    return score


def retrieve_relevant_clauses(
    db: Session,
    question: str,
    document_id: int,
    top_k: int = 3,
) -> list[Clause]:
    """
    Retrieve semantically relevant clauses using
    PostgreSQL pgvector cosine distance.
    """

    if not question.strip():
        return []

    question_embedding = generate_embedding(question)

    clauses = (
        db.query(Clause)
        .filter(
            Clause.document_id == document_id,
            Clause.embedding.is_not(None),
        )
        .order_by(
            Clause.embedding.cosine_distance(
                question_embedding
            )
        )
        .limit(top_k)
        .all()
    )

    if clauses:
        return clauses

    return retrieve_keyword_clauses(
        db=db,
        question=question,
        document_id=document_id,
        top_k=top_k,
    )
def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.
    """

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding dimensions do not match."
        )

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(
        a * a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b * b
        for b in vector_b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def retrieve_keyword_clauses(
    db: Session,
    question: str,
    document_id: int,
    top_k: int = 3,
) -> list[Clause]:
    """
    Fallback keyword-based retrieval.
    """

    clauses = (
        db.query(Clause)
        .filter(
            Clause.document_id == document_id,
        )
        .all()
    )

    scored_clauses = []

    for clause in clauses:
        score = score_clause(
            question,
            clause,
        )

        if score > 0:
            scored_clauses.append(
                (score, clause)
            )

    scored_clauses.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        clause
        for _, clause in scored_clauses[:top_k]
    ]