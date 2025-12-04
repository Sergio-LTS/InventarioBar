# app/init_db.py
import asyncio
from app.database import engine, Base

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas/actualizadas en la BD remota (Render).")

if __name__ == "__main__":
    asyncio.run(main())
