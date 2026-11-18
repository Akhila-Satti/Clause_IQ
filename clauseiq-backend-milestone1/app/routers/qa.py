
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

from app.services.personalization_service import (
    build_personalization_context,
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
    print("\n========== ASK AGREEMENT ==========", flush=True)
    print("Endpoint reached", flush=True)
    print("Authenticated User ID:", user.id, flush=True)

    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # Verify document ownership.
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

    # Retrieve relevant agreement clauses.
    try:
        relevant_clauses = retrieve_relevant_clauses(
            db=db,
            question=question,
            document_id=document_id,
            top_k=3,
        )

        if not relevant_clauses:
            raise HTTPException(
                status_code=404,
                detail="No relevant clauses were found for this question.",
            )

        # =====================================
        # PERSONALIZATION CONTEXT
        # =====================================

        print("\n========== PERSONALIZATION DEBUG ==========", flush=True)

        print("USER ID:", user.id, flush=True)
        print("CONSENT:", user.personalization_consent, flush=True)
        print("AGE:", user.age, flush=True)
        print("OCCUPATION:", user.occupation, flush=True)
        print("INCOME:", user.income, flush=True)
        print("LOCATION:", user.location, flush=True)

        personalization_context = build_personalization_context(user)

        print(
            "GENERATED CONTEXT:",
            repr(personalization_context),
            flush=True,
        )

        print("CONTEXT GENERATED:", bool(personalization_context), flush=True)

        print("============================================\n", flush=True)

        # =====================================
        # SEND CONTEXT TO LLM
        # =====================================

        print("Sending question and personalization to QA service...", flush=True)

        answer = ask_agreement(
            question=question,
            clauses=relevant_clauses,
            personalization_context=personalization_context,
        )

        if not answer or not answer.strip():
            raise ValueError("AI returned an empty answer.")

        print("AI answer generated successfully.", flush=True)
        print("====================================\n", flush=True)

    except HTTPException:
        raise

    except Exception as exc:
        print("ASK AGREEMENT ERROR:", repr(exc), flush=True)

        raise HTTPException(
            status_code=502,
            detail=f"Agreement question answering failed: {exc}",
        ) from exc

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
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

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
