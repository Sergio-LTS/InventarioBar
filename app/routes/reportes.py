from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ..database import get_db
from .. import crud

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post("/rebuild", status_code=204)
async def rebuild(db: AsyncSession = Depends(get_db)):
    await crud.rebuild_resumenes_ventas(db)
    return

@router.get("/mas-vendidos")
async def mas_vendidos(limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.list_productos_mas_vendidos(db, limit)

@router.get("/menos-vendidos")
async def menos_vendidos(limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.list_productos_menos_vendidos(db, limit)

@router.get("/resumen")
async def resumen(desde: datetime | None = Query(default=None), hasta: datetime | None = Query(default=None), db: AsyncSession = Depends(get_db)):
    return await crud.resumen_ventas_periodo(db, desde, hasta)

@router.get("/reconciliacion")
async def reconciliacion(db: AsyncSession = Depends(get_db)):
    return await crud.reconciliacion_stock(db)
