import os
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, UploadFile, HTTPException, Query, Form
from sqlalchemy import select, any_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document, ProcessingStatus
from app.schemas import DocumentResponse, DocumentDetail
from app.services.pdf_processor import extract_text_from_pdf
from app.config import settings

router = APIRouter()


ALLOWED_CONTENT_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}


def normalize_tags(tags: list[str] = Form(default=[])) -> list[str]:
    """Normalize tags to lowercase and remove duplicates."""
    return list({tag.strip().lower() for tag in tags if tag.strip()})


NormalizedTags = Annotated[list[str], Depends(normalize_tags)]


@router.post("/documents")
async def upload_document(
    file: UploadFile,
    tags: NormalizedTags,
    db: AsyncSession = Depends(get_db)
):
    safe_filename = os.path.basename(file.filename)
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Validate file type
    file_ext = os.path.splitext(safe_filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # verify the final path is inside UPLOAD_DIR
    if not os.path.abspath(file_path).startswith(os.path.abspath(settings.UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="Invalid filename")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    file_size = len(content)
    text_content, page_count = await extract_text_from_pdf(file_path)

    document = Document(
        filename=safe_filename,
        content=text_content,
        file_size=file_size,
        page_count=page_count,
        tags=tags,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    processing_status = ProcessingStatus(
        document_id=document.id,
        status="completed",
        processed_at=datetime.utcnow(),
    )
    db.add(processing_status)
    await db.commit()

    return {"id": document.id, "filename": document.filename, "tags": document.tags}


@router.get("/documents")
async def list_documents(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).options(joinedload(Document.processing_status))

    if tag:
        query = query.where(tag.lower() == any_(Document.tags))

    result = await db.execute(query)
    documents = result.scalars().all()

    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_size=doc.file_size,
            page_count=doc.page_count,
            tags=doc.tags or [],
            status=doc.processing_status.status if doc.processing_status else "unknown",
            created_at=doc.created_at,
        )
        for doc in documents
    ]


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .options(joinedload(Document.processing_status))
        .where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentDetail(
        id=document.id,
        filename=document.filename,
        content=document.content,
        file_size=document.file_size,
        page_count=document.page_count,
        tags=document.tags or [],
        status=document.processing_status.status if document.processing_status else "unknown",
        created_at=document.created_at,
    )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .options(joinedload(Document.processing_status))
        .where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = os.path.join(settings.UPLOAD_DIR, document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    if document.processing_status:
        await db.delete(document.processing_status)

    await db.delete(document)
    await db.commit()

    return {"message": "Document deleted"}
