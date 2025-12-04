# app/main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import usuarios, productos, ventas, movimientos, reportes
from .routes import web, health

app = FastAPI(title="Inventario de Bar")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(movimientos.router)
app.include_router(reportes.router)
app.include_router(web.router)
app.include_router(health.router)
