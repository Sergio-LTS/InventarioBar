from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])

@router.post("/", response_model=schemas.MovimientoOut, status_code=201)
async def crear_movimiento(payload: schemas.MovimientoCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_movimiento(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[schemas.MovimientoOut])
async def listar_movimientos(producto_id: int | None = Query(default=None), db: AsyncSession = Depends(get_db)):
    return await crud.list_movimientos(db, producto_id)