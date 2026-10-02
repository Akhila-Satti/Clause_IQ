from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    name: str
    type: str
    size: int
    uploadedAt: datetime
    status: str

    model_config = {"from_attributes": True}
