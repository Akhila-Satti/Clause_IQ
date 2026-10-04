from pydantic import BaseModel, Field


class AgreementGenerationRequest(BaseModel):
    agreement_type: str = Field(
        min_length=1,
        max_length=100,
    )

    parties: str = Field(
        min_length=1,
        max_length=2000,
    )

    purpose: str = Field(
        min_length=1,
        max_length=2000,
    )

    location: str = Field(
        default="",
        max_length=500,
    )

    duration: str = Field(
        default="",
        max_length=500,
    )

    financial_terms: str = Field(
        default="",
        max_length=2000,
    )

    additional_requirements: str = Field(
        default="",
        max_length=5000,
    )


class AgreementGenerationResponse(BaseModel):
    agreement_type: str
    agreement: str