# app/main.py
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers API y Web
from .routes import usuarios, productos, ventas, movimientos, reportes
from .routes import web, health  # <-- home HTML y health header-check

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Inventario de Bar")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Routers API
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(movimientos.router)
app.include_router(reportes.router)
app.include_router(web.router)
app.include_router(health.router)


