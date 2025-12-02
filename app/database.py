# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

load_dotenv()

# Acepta url sync y la convierte a async por si acaso
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL en variables de entorno")

async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# (Opcional) creación de tablas al inicio si lo necesitas:
# async def init_models():
#     from . import models  # asegura que se declaren
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
