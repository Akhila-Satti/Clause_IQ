from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE")
    )

    overall_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    risks: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    recommendations: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    document = relationship(
        "Document",
        back_populates="analyses",
    )