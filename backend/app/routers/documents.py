"""
Document management and ingestion endpoints.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.organization import Organization
from app.models.user import User
from app.services.document_processor import (
    DocumentProcessingError,
    chunk_text,
    extract_text,
    validate_file,
)
from app.services.ollama_service import get_embedding
from app.services.storage_service import delete_upload_file, save_upload_file

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str
    created_at: str
    page_count: Optional[int] = None
    chunks_count: Optional[int] = None

    class Config:
        from_attributes = True


def get_or_create_default_context(db: Session) -> tuple[uuid.UUID, uuid.UUID]:
    """Retrieve or initialize default Organization and User records for local development."""
    # Find existing org or create one
    org = db.execute(select(Organization).limit(1)).scalar_one_or_none()
    if not org:
        org = Organization(
            id=uuid.uuid4(),
            name="Default Workspace",
            slug="default-workspace",
        )
        db.add(org)
        db.flush()

    # Find existing user or create one
    user = db.execute(select(User).limit(1)).scalar_one_or_none()
    if not user:
        user = User(
            id=uuid.uuid4(),
            email="developer@documind.local",
            hashed_password="not_used_in_local_dev",
            full_name="DocuMind Developer",
            is_active=True,
        )
        db.add(user)
        db.flush()

    return org.id, user.id


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """Return all uploaded documents ordered by creation time descending."""
    docs = db.execute(
        select(Document).order_by(Document.created_at.desc())
    ).scalars().all()

    result = []
    for doc in docs:
        result.append(
            DocumentResponse(
                id=str(doc.id),
                filename=doc.filename,
                file_type=doc.file_type,
                status=doc.status,
                created_at=doc.created_at.isoformat(),
                chunks_count=len(doc.chunks) if doc.chunks else 0,
            )
        )
    return result


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Ingest a PDF or TXT document:

    1. Validate file extension and size.
    2. Securely persist raw file to disk using UUID storage key.
    3. Extract text from pages.
    4. Chunk text with overlapping character windows.
    5. Generate embeddings for each chunk via Ollama.
    6. Save Document and DocumentChunk records into DB.
    """
    filename = file.filename or "unknown"
    file_bytes = await file.read()
    file_size = len(file_bytes)

    # 1. Validate
    try:
        file_type = validate_file(filename, file_size, file_bytes)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # 2. Save file safely
    storage_key, _ = save_upload_file(file_bytes, file_type)

    document = None
    try:
        org_id, user_id = get_or_create_default_context(db)

        # 3. Create Document record in processing state
        document = Document(
            id=uuid.uuid4(),
            organization_id=org_id,
            uploaded_by=user_id,
            filename=filename,
            file_type=file_type,
            storage_key=storage_key,
            status="processing",
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # 4. Extract text
        pages = extract_text(file_bytes, file_type)

        # 5. Chunk text
        chunks_data = chunk_text(pages)
        if not chunks_data:
            raise DocumentProcessingError("Document yielded zero text chunks.")

        # 6. Generate embeddings and save chunks
        created_chunks = []
        for c in chunks_data:
            # Generate 768-dim vector using nomic-embed-text via Ollama
            embedding_vector = await get_embedding(c["content"])

            chunk_record = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document.id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                embedding=embedding_vector,
                page_number=c["page_number"],
            )
            created_chunks.append(chunk_record)

        db.add_all(created_chunks)
        document.status = "ready"
        db.commit()
        db.refresh(document)

        return DocumentResponse(
            id=str(document.id),
            filename=document.filename,
            file_type=document.file_type,
            status=document.status,
            created_at=document.created_at.isoformat(),
            chunks_count=len(created_chunks),
        )

    except Exception as exc:
        db.rollback()
        # Mark status as failed if document record was created
        if document and document.id:
            try:
                document.status = "failed"
                db.add(document)
                db.commit()
            except Exception:
                db.rollback()
        # Clean up file on disk if processing totally failed
        delete_upload_file(storage_key)

        detail_msg = str(exc) if isinstance(exc, DocumentProcessingError) else f"Ingestion error: {exc}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            if not isinstance(exc, DocumentProcessingError)
            else status.HTTP_400_BAD_REQUEST,
            detail=detail_msg,
        )

