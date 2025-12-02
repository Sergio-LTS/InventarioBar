# app/routes/reportes.py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .. import crud

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post("/rebuild", status_code=204)
async def rebuild_resumenes(db: AsyncSession = Depends(get_db)) -> Response:
    """
    Reconstruye tablas de resumen (más/menos vendidos) a partir de ventas actuales.
    """
    await crud.rebuild_resumenes_ventas(db)
    return Response(status_code=204)

@router.get("/mas-vendidos")
async def mas_vendidos(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Lee la tabla persistida de productos más vendidos.
    """
    rows = await crud.list_productos_mas_vendidos(db, limit=limit)
    return [
        {
            "id_producto": r.id_producto,
            "nombre": r.nombre,
            "total_vendido": int(r.total_vendido),
            "actualizado_en": getattr(r, "actualizado_en", None),
        }
        for r in rows
    ]

@router.get("/menos-vendidos")
async def menos_vendidos(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Lee la tabla persistida de productos menos vendidos.
    """
    rows = await crud.list_productos_menos_vendidos(db, limit=limit)
    return [
        {
            "id_producto": r.id_producto,
            "nombre": r.nombre,
            "total_vendido": int(r.total_vendido),
            "actualizado_en": getattr(r, "actualizado_en", None),
        }
        for r in rows
    ]
