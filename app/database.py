# app/database.py
import os
import logging
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
logger = logging.getLogger("db")

raw = os.getenv("DATABASE_URL")
if not raw:
    raise RuntimeError("DATABASE_URL missing")

# Forzar driver asyncpg
if raw.startswith("postgres://"):
    raw = "postgresql+asyncpg://" + raw[len("postgres://"):]
if raw.startswith("postgresql://") and "+asyncpg" not in raw:
    raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)

# Quitar por completo los parámetros (?...).
p = urlparse(raw)
clean_url = urlunparse(p._replace(query=""))

def _mask(u: str) -> str:
    up = urlparse(u)
    host = up.hostname or "?"
    db = (up.path or "/").lstrip("/")
    return f"postgresql+asyncpg://***:***@{host}/{db}"

logger.info("database.py cargado: %s", __file__)
logger.info("DB URL (sanitized, sin query): %s", _mask(clean_url))

engine = create_async_engine(
    clean_url,
    future=True,
    echo=False,
    pool_size=5,
    max_overflow=5,
    connect_args={"ssl": True},  # <-- TLS forzado aquí, no en la URL
)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
