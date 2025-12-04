# app/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..database import get_db

router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    return {"ok": True}

@router.get("/health/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    q = text("""
        select
          current_database() as db,
          current_user as usr,
          inet_server_addr()::text as host,
          inet_server_port()::int as port,
          current_setting('search_path') as search_path
    """)
    res = await db.execute(q)
    row = res.mappings().first()
    return dict(row)
