from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.clause import Clause
from app.models.document import Document
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse
from app.schemas.document import DocumentResponse
from app.services.analysis_service import build_analysis
from app.services.clause_service import segment_clauses
from app.services.embedding_service import generate_embedding
from app.services.document_service import ALLOWED_TYPES, extract_text
from app.schemas.clause_assistant import (
    ClauseQuestionRequest,
    ClauseQuestionResponse,
)
from app.services.clause_assistant_service import ask_about_clause


router = APIRouter(prefix="/documents", tags=["Documents"])


def _document_response(document: Document) -> dict:
    return {
        "id": str(document.id),
        "name": document.filename,
        "type": document.file_type,
        "size": document.file_size,
        "uploadedAt": document.created_at,
        "status": document.status,
    }


def _analysis_response(analysis: Analysis, clauses: list[Clause]) -> dict:
    return {
        "summary": analysis.summary or "",
        "overallScore": analysis.overall_score,
        "risks": analysis.risks or [],
        "recommendations": analysis.recommendations or [],
        "clauses": [
            {
                "id": str(c.id),
                "section": c.section,
                "title": c.title,
                "category": c.category,
                "riskLevel": c.risk_level,
                "text": c.text,
                "explanation": c.explanation,
                "summary": c.summary or "",
                "risks": c.risks or [],
                "obligations": c.obligations or [],
            }
            for c in clauses
        ],
    }


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Supported file types are PDF, DOCX and TXT.",
        )

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    content = await file.read()

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File is larger than {settings.max_file_size_mb} MB.",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid4().hex}{extension}"
    path = upload_dir / stored_name
    path.write_bytes(content)

    try:
        extracted_text = extract_text(path, extension)
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail=f"Could not extract document text: {exc}",
        )

    document = Document(
        filename=file.filename or stored_name,
        file_type=ALLOWED_TYPES[extension],
        file_size=len(content),
        file_path=str(path),
        extracted_text=extracted_text,
        status="processed",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    clause_data = segment_clauses(extracted_text)

    clause_models = []

    for item in clause_data:
        embedding_text = "\n".join(
            [
                item.section or "",
                item.title or "",
                item.category or "",
                item.text or "",
            ]
        )

        try:
            embedding = generate_embedding(embedding_text)

        except Exception as exc:
            db.rollback()

            document.status = "embedding_failed"
            db.add(document)
            db.commit()

            raise HTTPException(
                status_code=502,
                detail=f"Embedding generation failed: {exc}",
            )

        clause = Clause(
            document_id=document.id,
            section=item.section,
            title=item.title,
            category=item.category,
            risk_level=item.risk_level,
            text=item.text,
            summary="",
            explanation=item.explanation,
            risks=[],
            obligations=[],
            embedding=embedding,
        )

        db.add(clause)
        clause_models.append(clause)

    db.commit()

    analysis = build_analysis(
        db,
        document.id,
        clause_models,
        summary="Document analyzed using ClauseIQ's rule-based clause analysis.",
        recommendations=[],
    )

    document.status = "analyzed"
    db.add(document)
    db.commit()
    db.refresh(document)

    return _document_response(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [_document_response(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return _document_response(document)


@router.get("/{document_id}/clauses")
def get_clauses(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return [
        {
            "id": str(c.id),
            "section": c.section,
            "title": c.title,
            "category": c.category,
            "riskLevel": c.risk_level,
            "text": c.text,
            "summary": c.summary or "",
            "explanation": c.explanation or "",
            "risks": c.risks or [],
            "obligations": c.obligations or [],
        }
        for c in document.clauses
    ]


@router.post(
    "/{document_id}/clauses/{clause_id}/ask",
    response_model=ClauseQuestionResponse,
)
def ask_clause_question(
    document_id: int,
    clause_id: int,
    request: ClauseQuestionRequest,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    clause = (
        db.query(Clause)
        .filter(
            Clause.id == clause_id,
            Clause.document_id == document_id,
        )
        .first()
    )

    if not clause:
        raise HTTPException(
            status_code=404,
            detail="Clause not found for this document",
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    try:
        answer = ask_about_clause(
            question=request.question,
            section=clause.section,
            title=clause.title,
            clause_text=clause.text,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Clause analysis failed: {exc}",
        )

    return {
        "answer": answer,
        "clause_id": str(clause.id),
        "section": clause.section,
        "title": clause.title,
    }


@router.get(
    "/{document_id}/analysis",
    response_model=AnalysisResponse,
)
def get_analysis(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(Analysis)
        .filter(Analysis.document_id == document_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return _analysis_response(
        analysis,
        document.clauses,
    )