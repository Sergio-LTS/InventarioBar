# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import usuarios, productos, ventas, movimientos, reportes
from .routes import web as web_routes

app = FastAPI(title="Inventario de Bar")

# Routers API
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(movimientos.router)
app.include_router(reportes.router)

# Router Web (Jinja)
app.include_router(web_routes.router)

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"Inventario Bar": "OK"}

@app.get("/health")
async def health():
    return {"status": "ok"}
