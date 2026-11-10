from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document

router = APIRouter()


@router.get("/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """Get all unique tags from all documents."""
    result = await db.execute(
        select(func.unnest(Document.tags).label("tag")).distinct()
    )
    tags = [row[0] for row in result.fetchall()]
    return sorted(tags)
