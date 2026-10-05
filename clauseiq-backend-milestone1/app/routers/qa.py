from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.routers.auth import get_current_user

from app.schemas.question import (
    AskQuestionRequest,
    AskQuestionResponse,
)

from app.services.qa_service import ask_agreement

from app.services.retrieval_service import (
    retrieve_relevant_clauses,
)


router = APIRouter(
    prefix="/documents",
    tags=["Ask Agreement"],
)


@router.post(
    "/{document_id}/ask",
    response_model=AskQuestionResponse,
)
def ask_question(
    document_id: int,
    request: AskQuestionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    document = db.get(
        Document,
        document_id,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Make sure the document belongs to the logged-in user.
    if document.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this document.",
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    clauses = document.clauses

    if not clauses:
        raise HTTPException(
            status_code=400,
            detail="No analyzed clauses found for this document.",
        )

    relevant_clauses = retrieve_relevant_clauses(
        db=db,
        question=question,
        document_id=document_id,
        top_k=3,
    )

    if not relevant_clauses:
        raise HTTPException(
            status_code=404,
            detail=(
                "No relevant clauses were found "
                "for this question."
            ),
        )

    try:
        answer = ask_agreement(
            question=question,
            clauses=relevant_clauses,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Agreement question answering failed: {exc}"
            ),
        )

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "clause_id": str(clause.id),
                "section": clause.section,
                "title": clause.title,
                "category": clause.category,
                "text": clause.text,
            }
            for clause in relevant_clauses
        ],
    }


@router.post(
    "/{document_id}/retrieve",
)
def retrieve_clauses(
    document_id: int,
    request: AskQuestionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    document = db.get(
        Document,
        document_id,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Make sure the document belongs to the logged-in user.
    if document.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this document.",
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    relevant_clauses = retrieve_relevant_clauses(
        db=db,
        question=question,
        document_id=document_id,
        top_k=3,
    )

    return [
        {
            "id": str(clause.id),
            "section": clause.section,
            "title": clause.title,
            "category": clause.category,
            "text": clause.text,
        }
        for clause in relevant_clauses
    ]