# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import text

from .database import async_engine  # << usamos el engine asíncrono
from .routes import usuarios, productos, ventas, movimientos, reportes
from .routes.web import router as web_router  # << router HTML (Jinja2)

app = FastAPI(title="Inventario de Bar - InventarioBar")

# Archivos estáticos (CSS, imágenes del front)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers de API
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(movimientos.router)
app.include_router(reportes.router)

# Router web (plantillas Jinja2)
app.include_router(web_router)

# Redirección de raíz a la vista HTML
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/web/")

# Salud
@app.get("/health")
async def health():
    return {"status": "ok"}

# Crear columnas de imágenes si no existen (productos.imagen_url y usuarios.avatar_url)
@app.on_event("startup")
async def ensure_columns():
    SessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        await session.execute(text("ALTER TABLE IF EXISTS productos ADD COLUMN IF NOT EXISTS imagen_url TEXT;"))
        await session.execute(text("ALTER TABLE IF EXISTS usuarios  ADD COLUMN IF NOT EXISTS avatar_url  TEXT;"))
        await session.commit()
