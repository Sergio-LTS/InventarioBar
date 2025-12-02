# app/routes/web.py
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from .. import crud, schemas, models
from ..supabase_client import upload_image

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/web", tags=["Web"])

# -------------------------
# Página: Productos (lista)
# -------------------------
@router.get("/productos")
async def pagina_productos(request: Request, db: AsyncSession = Depends(get_db)):
    productos = await crud.list_productos(db)
    return templates.TemplateResponse(
        "productos.html",
        {"request": request, "productos": productos},
    )

# ---------------------------------
# Form POST: Crear producto (web)
# ---------------------------------
@router.post("/productos/nuevo")
async def crear_producto_web(
    request: Request,
    nombre: str = Form(...),
    categoria: str | None = Form(None),
    marca: str | None = Form(None),
    cantidad: int = Form(...),
    precio_venta: float = Form(...),
    imagen: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    # Subir imagen (opcional) a Supabase y obtener URL
    imagen_url = None
    if imagen and imagen.filename:
        imagen_url = await upload_image(imagen)  # usa tu cliente actual

    data = schemas.ProductoCreate(
        nombre=nombre,
        categoria=categoria,
        marca=marca,
        cantidad=cantidad,
        precio_venta=precio_venta,
        imagen_url=imagen_url,
    )
    await crud.create_producto(db, data)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_302_FOUND)

# -------------------------
# Página: Ventas (con fotos)
# -------------------------
@router.get("/ventas")
async def pagina_ventas(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Lista de ventas uniendo Venta + Producto + Usuario
    para mostrar imagen del producto y foto del usuario.
    """
    stmt = (
        select(models.Venta, models.Producto, models.Usuario)
        .join(models.Producto, models.Producto.id_producto == models.Venta.id_producto)
        .join(models.Usuario, models.Usuario.id_usuario == models.Venta.id_usuario)
        .order_by(models.Venta.id_venta.desc())
    )

    rows = (await db.execute(stmt)).all()

    ventas = []
    for v, p, u in rows:
        ventas.append({
            "id_venta": v.id_venta,
            "fecha_venta": v.fecha_venta,
            "cantidad_vendida": v.cantidad_vendida,
            "total_venta": v.total_venta,
            "producto_nombre": p.nombre,
            "producto_imagen": p.imagen_url,    # <- columna que ya agregaste
            "usuario_nombre": u.nombre_usuario,
            "usuario_foto": u.foto_url,         # <- columna que ya agregaste
        })

    return templates.TemplateResponse(
        "ventas.html",
        {"request": request, "ventas": ventas},
    )
