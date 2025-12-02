from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("/", response_model=schemas.ProductoOut, status_code=201)
async def crear_producto(payload: schemas.ProductoCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_producto(db, payload)

@router.get("/", response_model=list[schemas.ProductoOut])
async def listar_productos(db: AsyncSession = Depends(get_db)):
    return await crud.list_productos(db)

@router.get("/{producto_id}", response_model=schemas.ProductoOut)
async def obtener_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_producto(db, producto_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return obj

@router.put("/{producto_id}", response_model=schemas.ProductoOut)
async def actualizar_producto(producto_id: int, payload: schemas.ProductoUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.update_producto(db, producto_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return obj

@router.delete("/{producto_id}", response_model=schemas.ProductoOut)
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.delete_producto(db, producto_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return obj