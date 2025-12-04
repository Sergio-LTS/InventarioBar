# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    raise RuntimeError("DATABASE_URL missing")

def normalize_db_url(url: str) -> str:
    # 1) Forzar driver asyncpg si viene 'postgres://'
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]

    # 2) Si ya es asyncpg, garantizar SSL compatible
    if "+asyncpg" in url:
        # Reemplazar sslmode=... por ssl=true (asyncpg NO usa sslmode)
        if "sslmode=" in url:
            url = url.replace("sslmode=require", "ssl=true") \
                     .replace("sslmode=verify-full", "ssl=true") \
                     .replace("sslmode=prefer", "ssl=true") \
                     .replace("sslmode=allow", "ssl=true") \
                     .replace("sslmode=disable", "ssl=true")
        # Si no hay parámetro ssl, añadirlo
        if "ssl=true" not in url and "ssl=" not in url:
            url += ("&" if "?" in url else "?") + "ssl=true"

    return url

DATABASE_URL = normalize_db_url(raw_url)

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_size=5,
    max_overflow=5,
)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
