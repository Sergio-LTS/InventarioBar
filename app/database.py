# app/database.py
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://sergio:12345@localhost/inventariobar"
)

def normalize_dsn(dsn: str):
    """
    Acepta:
      - postgresql://...  -> lo convierte a postgresql+asyncpg://...
      - ?ssl=true         -> fuerza connect_args={"ssl": True}
      - ?sslmode=require  -> idem, y se quita del DSN para que asyncpg no se queje
    """
    u = urlparse(dsn)
    scheme = u.scheme
    if scheme == "postgresql":
        scheme = "postgresql+asyncpg"

    q = parse_qs(u.query)
    connect_args = {}

    ssl_true = (q.get("ssl", [""])[0] == "true")
    sslmode = q.get("sslmode", [""])[0]
    if ssl_true or sslmode in {"require", "verify-ca", "verify-full"}:
        connect_args["ssl"] = True
        q.pop("ssl", None)
        q.pop("sslmode", None)

    new_query = urlencode({k: v[0] for k, v in q.items()})
    new_u = u._replace(scheme=scheme, query=new_query)
    clean_dsn = urlunparse(new_u)
    return clean_dsn, connect_args

DSN, CONNECT_ARGS = normalize_dsn(DATABASE_URL)

engine = create_async_engine(
    DSN,
    pool_pre_ping=True,
    connect_args=CONNECT_ARGS
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
