# app/routes/uploads.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from .. import models, schemas
from ..utils.supabase import upload_to_supabase

router = APIRouter(prefix="/upload", tags=["Uploads"])

@router.post("/productos/{id_producto}/imagen", response_model=schemas.ProductoOut)
async def subir_imagen_producto(
    id_producto: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Buscar producto
    res = await db.execute(
        select(models.Producto).where(models.Producto.id_producto == id_producto)
    )
    prod = res.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no existe")

    # Subir a Supabase
    data = await file.read()
    url = await upload_to_supabase(
        data,
        filename=file.filename,
        folder="productos",
        content_type=file.content_type,
    )

    # Guardar URL en DB
    prod.imagen_url = url
    await db.commit()
    await db.refresh(prod)
    return prod


@router.post("/usuarios/{id_usuario}/foto", response_model=schemas.UsuarioOut)
async def subir_foto_usuario(
    id_usuario: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(models.Usuario).where(models.Usuario.id_usuario == id_usuario)
    )
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no existe")

    data = await file.read()
    url = await upload_to_supabase(
        data,
        filename=file.filename,
        folder="usuarios",
        content_type=file.content_type,
    )

    user.foto_url = url
    await db.commit()
    await db.refresh(user)
    return user
