# app/routes/web.py
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from .. import models
from ..supabase_client import upload_image_to_supabase

router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/web/productos")
async def pagina_productos(request: Request, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Producto).order_by(models.Producto.id_producto))
    productos = list(res.scalars().all())
    return templates.TemplateResponse("web/productos.html", {"request": request, "productos": productos})

@router.post("/web/productos/nuevo")
async def web_crear_producto(
    request: Request,
    nombre: str = Form(...),
    categoria: str = Form(...),
    marca: str = Form(...),
    cantidad: int = Form(...),
    precio_venta: float = Form(...),
    imagen: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    url = None
    if imagen:
        url = await upload_image_to_supabase(imagen, folder="productos")

    obj = models.Producto(
        nombre=nombre, categoria=categoria, marca=marca,
        cantidad=cantidad, precio_venta=precio_venta,
        imagen_url=url
    )
    db.add(obj)
    await db.commit()
    return RedirectResponse(url="/web/productos", status_code=303)

@router.get("/web/usuarios")
async def pagina_usuarios(request: Request, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Usuario).order_by(models.Usuario.id_usuario))
    usuarios = list(res.scalars().all())
    return templates.TemplateResponse("web/usuarios.html", {"request": request, "usuarios": usuarios})

@router.post("/web/usuarios/nuevo")
async def web_crear_usuario(
    request: Request,
    nombre: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(...),
    rol: str = Form(...),
    foto: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    foto_url = None
    if foto:
        foto_url = await upload_image_to_supabase(foto, folder="usuarios")

    obj = models.Usuario(
        nombre=nombre, correo=correo, contrasena=contrasena,
        rol=rol, foto_url=foto_url
    )
    db.add(obj)
    await db.commit()
    return RedirectResponse(url="/web/usuarios", status_code=303)
