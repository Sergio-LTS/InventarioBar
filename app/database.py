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

# --- Normaliza driver: postgres -> postgresql+asyncpg
if raw.startswith("postgres://"):
    raw = "postgresql+asyncpg://" + raw[len("postgres://"):]
if raw.startswith("postgresql://") and "+asyncpg" not in raw:
    raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)

# --- Quita cualquier query (?sslmode=...) para evitar el error de asyncpg
p = urlparse(raw)
clean_url = urlunparse(p._replace(query=""))
host = p.hostname or ""

def _mask(u: str) -> str:
    up = urlparse(u)
    return f"postgresql+asyncpg://***:***@{up.hostname}/{(up.path or '/').lstrip('/')}"

def _parse_bool(s: str | None):
    if s is None:
        return None
    v = s.strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return None  # auto

# DB_SSL controla TLS:
#   - "true"/"false" -> fuerza
#   - "auto" (o no definida) -> usa TLS si el host NO es localhost
DB_SSL = os.getenv("DB_SSL", "auto")
flag = _parse_bool(DB_SSL)

use_ssl = False
if flag is None:               # auto
    use_ssl = host not in ("localhost", "127.0.0.1")
else:
    use_ssl = flag

connect_args = {}
if use_ssl:
    # NUNCA usar "sslmode" con asyncpg. Solo "ssl=True" o un contexto SSL.
    connect_args["ssl"] = True

logger.info("DB URL (sanitized): %s | SSL=%s", _mask(clean_url), use_ssl)

engine = create_async_engine(
    clean_url,
    future=True,
    echo=False,
    pool_size=5,
    max_overflow=5,
    connect_args=connect_args,
)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
