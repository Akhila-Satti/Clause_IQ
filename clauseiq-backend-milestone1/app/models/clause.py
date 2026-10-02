from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE")
    )

    section: Mapped[str] = mapped_column(
        String(100),
        default="",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        default="",
    )

    category: Mapped[str] = mapped_column(
        String(100),
        default="General",
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        default="LOW",
    )

    text: Mapped[str] = mapped_column(Text)

    # Gemini analysis
    summary: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    risks: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    obligations: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    # Vector embedding used for semantic retrieval
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    document = relationship(
        "Document",
        back_populates="clauses",
    )