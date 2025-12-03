# app/routes/productos.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from .. import models, schemas
from ..supabase_client import upload_image_to_supabase

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=list[schemas.ProductoOut])
async def listar_productos(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Producto).order_by(models.Producto.id_producto))
    return list(res.scalars().all())

@router.post("/", response_model=schemas.ProductoOut, status_code=201)
async def crear_producto(payload: schemas.ProductoCreate, db: AsyncSession = Depends(get_db)):
    obj = models.Producto(**payload.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.post("/con-imagen", response_model=schemas.ProductoOut, status_code=201)
async def crear_producto_con_imagen(
    nombre: str = Form(...),
    categoria: str = Form(...),
    marca: str = Form(...),
    cantidad: int = Form(...),
    precio_venta: float = Form(...),
    imagen: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    url = await upload_image_to_supabase(imagen, folder="productos")
    obj = models.Producto(
        nombre=nombre, categoria=categoria, marca=marca,
        cantidad=cantidad, precio_venta=precio_venta,
        imagen_url=url
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{id_producto}", response_model=schemas.ProductoOut)
async def actualizar_producto(id_producto: int, payload: schemas.ProductoUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Producto).where(models.Producto.id_producto == id_producto))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{id_producto}", status_code=204)
async def eliminar_producto(id_producto: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Producto).where(models.Producto.id_producto == id_producto))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    await db.delete(obj)
    await db.commit()
    return None
