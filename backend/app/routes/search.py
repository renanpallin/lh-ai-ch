from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, any_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document
from app.schemas import SearchResult

router = APIRouter()


@router.get("/search")
async def search_documents(
    q: str,
    tag: Optional[str] = Query(None, description="Filter by tag"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).where(Document.content.ilike(f"%{q}%"))

    if tag:
        query = query.where(tag.lower() == any_(Document.tags))

    result = await db.execute(query)
    documents = result.scalars().all()

    return [
        SearchResult(
            id=doc.id,
            filename=doc.filename,
            snippet=doc.content[:200] + "..." if doc.content and len(doc.content) > 200 else (doc.content or ""),
        )
        for doc in documents
    ]
