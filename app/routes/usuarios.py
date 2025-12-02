from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=schemas.UsuarioOut, status_code=201)
async def crear_usuario(payload: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_usuario(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[schemas.UsuarioOut])
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    return await crud.list_usuarios(db)

@router.get("/{usuario_id}", response_model=schemas.UsuarioOut)
async def obtener_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_usuario(db, usuario_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return obj

@router.put("/{usuario_id}", response_model=schemas.UsuarioOut)
async def actualizar_usuario(usuario_id: int, payload: schemas.UsuarioUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.update_usuario(db, usuario_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return obj

@router.delete("/{usuario_id}", response_model=schemas.UsuarioOut)
async def eliminar_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.delete_usuario(db, usuario_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return obj