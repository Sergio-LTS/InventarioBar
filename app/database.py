# app/database.py
import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()

RAW_DSN = (os.getenv("DATABASE_URL") or "").strip().strip('"').strip("'")
if not RAW_DSN:
    raise RuntimeError("DATABASE_URL no está definido")

def build_dsn_and_args(raw: str):
    """
    - Acepta DSN con o sin parámetros SSL.
    - Si detecta Render (host contiene 'render.com') o PG_SSL=true en el entorno,
      fuerza SSL sin romper asyncpg.
    - Si encuentra sslmode inválido, lo corrige a 'require'.
    - Para asyncpg, pasamos 'ssl=True' via connect_args (robusto).
    """
    s = urlsplit(raw)
    q = dict(parse_qsl(s.query, keep_blank_values=True))
    connect_args = {}

    # ¿Debemos forzar SSL? (Render o variable de entorno)
    force_ssl = ("render.com" in (s.hostname or "")) or (os.getenv("PG_SSL", "").lower() in {"1", "true", "yes"})

    # Normalizamos si vienen params raros
    if "ssl" in q:
        # asyncpg entiende ssl=true
        if q["ssl"].lower() in {"true", "1", "yes"}:
            connect_args["ssl"] = True
    elif "sslmode" in q:
        # asyncpg acepta sslmode con valores válidos; si es raro, lo seteo a require
        valid = {"disable","allow","prefer","require","verify-ca","verify-full"}
        if q["sslmode"] not in valid:
            q["sslmode"] = "require"
        if q["sslmode"] in {"require","verify-ca","verify-full","prefer","allow"}:
            # Por seguridad, fuerza ssl=True si no es disable
            connect_args["ssl"] = True
    elif force_ssl:
        # Si no vino nada y queremos SSL (Render), añadimos sslmode=require
        q["sslmode"] = "require"
        connect_args["ssl"] = True

    new_dsn = urlunsplit((s.scheme, s.netloc, s.path, urlencode(q), s.fragment))
    return new_dsn, connect_args

DSN, CONNECT_ARGS = build_dsn_and_args(RAW_DSN)

engine = create_async_engine(
    DSN,
    echo=False,
    pool_pre_ping=True,
    connect_args=CONNECT_ARGS
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
