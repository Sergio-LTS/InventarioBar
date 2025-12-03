# app/routes/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=list[schemas.UsuarioOut])
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Usuario).order_by(models.Usuario.id_usuario))
    return list(res.scalars().all())

@router.post("/", response_model=schemas.UsuarioOut, status_code=201)
async def crear_usuario(payload: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    obj = models.Usuario(**payload.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{id_usuario}", response_model=schemas.UsuarioOut)
async def actualizar_usuario(id_usuario: int, payload: schemas.UsuarioUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Usuario).where(models.Usuario.id_usuario == id_usuario))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{id_usuario}", status_code=204)
async def eliminar_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Usuario).where(models.Usuario.id_usuario == id_usuario))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.delete(obj)
    await db.commit()
    return None
