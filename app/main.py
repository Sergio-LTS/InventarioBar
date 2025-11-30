# app/main.py
from fastapi import FastAPI, Request
from .models import Base
from .database import engine
from .routes import usuarios, productos, ventas, movimientos, reportes
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .routes import web as web_routes


app = FastAPI(title="Inventario de Bar logica de calculadora de Da vinci")


app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(movimientos.router)
app.include_router(reportes.router)
app.include_router(web_routes.router)

@app.get("/")
async def root():
    return {"Calculadora de da vinci"}

@app.get("/health")
async def health():
    return {"status": "ok"}

#@app.on_event("startup")
#async def create_tables_once():
#    async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.create_all)

