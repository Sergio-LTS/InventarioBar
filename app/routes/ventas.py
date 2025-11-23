from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/", response_model=schemas.VentaOut, status_code=201)
async def crear_venta(payload: schemas.VentaCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_venta(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[schemas.VentaOut])
async def listar_ventas(
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    producto_id: int | None = Query(default=None),
    usuario_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await crud.list_ventas(db, desde, hasta, producto_id, usuario_id)

@router.get("/{venta_id}", response_model=schemas.VentaOut)
async def obtener_venta(venta_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_venta(db, venta_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return obj
