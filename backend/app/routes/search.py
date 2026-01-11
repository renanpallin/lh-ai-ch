from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document
from app.schemas import SearchResult

router = APIRouter()


@router.get("/search")
async def search_documents(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document).where(Document.content.ilike(f"%{q}%"))
    )
    documents = result.scalars().all()

    return [
        SearchResult(
            id=doc.id,
            filename=doc.filename,
            snippet=doc.content[:200] + "..." if doc.content and len(doc.content) > 200 else (doc.content or ""),
        )
        for doc in documents
    ]
