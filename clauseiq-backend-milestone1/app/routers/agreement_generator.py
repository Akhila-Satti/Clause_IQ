from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User
from app.routers.auth import get_current_user

from app.schemas.agreement_generator import (
    AgreementGenerationRequest,
    AgreementGenerationResponse,
)

from app.services.agreement_generator_service import (
    generate_agreement,
)


router = APIRouter(
    prefix="/agreements",
    tags=["Agreement Generator"],
)


@router.post(
    "/generate",
    response_model=AgreementGenerationResponse,
)
def generate_agreement_route(
    request: AgreementGenerationRequest,
    user: User = Depends(get_current_user),
):
    try:
        agreement = generate_agreement(
            agreement_type=request.agreement_type,
            parties=request.parties,
            purpose=request.purpose,
            location=request.location,
            duration=request.duration,
            financial_terms=request.financial_terms,
            additional_requirements=request.additional_requirements,
            user=user,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Agreement generation failed: {exc}",
        )

    return {
        "agreement_type": request.agreement_type,
        "agreement": agreement,
    }