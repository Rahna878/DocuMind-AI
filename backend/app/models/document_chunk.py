import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document import Document


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(768), nullable=True
    )
    page_number: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Prevent duplicate chunk indices for the same document
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
    )

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document", back_populates="chunks"
    )
