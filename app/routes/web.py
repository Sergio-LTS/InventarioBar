# app/routes/web.py
import logging
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates

from ..database import get_db
from .. import crud, schemas
from ..services.supabase_storage import upload_image_get_public_url

logger = logging.getLogger("inventariobar")

router = APIRouter(tags=["web"])

# Directorio de templates (funciona igual local y en Render)
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Evita 'now is undefined' en Jinja:
templates.env.globals["now"] = lambda: datetime.now(timezone.utc)


# --------- Utilidades ---------
async def _try_upload(file: Optional[UploadFile], folder: str) -> Optional[str]:
    """
    Intenta subir a Supabase y devolver URL pública.
    Si faltan variables de entorno o falla cualquier cosa, devuelve None y loggea el warning.
    """
    if not file or not getattr(file, "filename", None):
        return None
    try:
        return await upload_image_get_public_url(file, folder=folder)
    except Exception as e:
        logger.warning("No se pudo subir a Supabase (%s): %s", folder, e)
        return None


def _parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        # input type="date" -> 'YYYY-MM-DD'
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None


# ---------- HOME ----------
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("web/home.html", {"request": request})


# ---------- PRODUCTOS ----------
@router.get("/web/productos", response_class=HTMLResponse)
async def pagina_productos(
    request: Request,
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = None,
    page: int = 1,
    msg: Optional[str] = None,
):
    page = max(page, 1)
    limit = 50
    offset = (page - 1) * limit

    productos = await crud.search_productos(db, q=q, limit=limit, offset=offset)

    return templates.TemplateResponse(
        "web/productos.html",
        {
            "request": request,
            "productos": productos,
            "q": q or "",
            "page": page,
            "msg": msg,
        },
    )


@router.post("/web/productos")
async def crear_producto_html(
    request: Request,
    db: AsyncSession = Depends(get_db),
    nombre: str = Form(...),
    categoria: str = Form(...),
    marca: str = Form(...),
    cantidad: int = Form(...),
    precio_venta: float = Form(...),
    imagen: Optional[UploadFile] = File(default=None),
):
    imagen_url = await _try_upload(imagen, folder="productos")

    data = schemas.ProductoCreate(
        nombre=nombre,
        categoria=categoria,
        marca=marca,
        cantidad=cantidad,
        precio_venta=precio_venta,
        imagen_url=imagen_url,
    )

    await crud.create_producto(db, data)
    logger.info("Producto creado: %s", nombre)
    return RedirectResponse(
        url="/web/productos?msg=Producto%20creado",
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/web/productos/{id_producto}/delete")
async def eliminar_producto_html(
    id_producto: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        await crud.delete_producto(db, id_producto)
        url = "/web/productos?msg=Producto%20eliminado"
    except Exception as e:
        logger.exception("Error al eliminar producto %s: %s", id_producto, e)
        url = f"/web/productos?msg=Error%20al%20eliminar:%20{str(e).replace(' ', '%20')}"
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


# ---------- USUARIOS ----------
@router.get("/web/usuarios", response_class=HTMLResponse)
async def pagina_usuarios(
    request: Request,
    db: AsyncSession = Depends(get_db),
    msg: Optional[str] = None,
):
    usuarios = await crud.list_usuarios(db)
    return templates.TemplateResponse(
        "web/usuarios.html",
        {"request": request, "usuarios": usuarios, "msg": msg},
    )


@router.post("/web/usuarios")
async def crear_usuario_html(
    request: Request,
    db: AsyncSession = Depends(get_db),
    nombre_usuario: str = Form(...),
    correo: str = Form(...),
    rol: str = Form(...),
    foto: Optional[UploadFile] = File(default=None),
):
    foto_url = await _try_upload(foto, folder="usuarios")

    data = schemas.UsuarioCreate(
        nombre_usuario=nombre_usuario,
        correo=correo,
        rol=rol,
        foto_url=foto_url,
    )
    await crud.create_usuario(db, data)
    logger.info("Usuario creado: %s", nombre_usuario)
    return RedirectResponse(
        url="/web/usuarios?msg=Usuario%20creado",
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/web/usuarios/{id_usuario}/delete")
async def eliminar_usuario_html(id_usuario: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_usuario(db, id_usuario)
        url = "/web/usuarios?msg=Usuario%20eliminado"
    except Exception as e:
        # Si hay ventas que referencian al usuario y la FK no es CASCADE, se informará aquí.
        logger.exception("Error al eliminar usuario %s: %s", id_usuario, e)
        url = f"/web/usuarios?msg=Error%20al%20eliminar:%20{str(e).replace(' ', '%20')}"
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


# ---------- VENTAS ----------
@router.get("/web/ventas", response_class=HTMLResponse)
async def pagina_ventas(
    request: Request,
    db: AsyncSession = Depends(get_db),
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    producto_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    msg: Optional[str] = None,
):
    dt_desde = _parse_date(desde)
    dt_hasta = _parse_date(hasta)

    # Datos para selects del formulario
    productos = await crud.list_productos(db)
    usuarios = await crud.list_usuarios(db)

    # Ventas filtradas
    ventas = await crud.list_ventas(
        db,
        desde=dt_desde,
        hasta=dt_hasta,
        producto_id=producto_id,
        usuario_id=usuario_id,
    )

    # Diccionarios para mostrar nombres
    map_prod = {p.id_producto: p for p in productos}
    map_user = {u.id_usuario: u for u in usuarios}

    # Resumen del periodo
    resumen = await crud.resumen_ventas_periodo(db, dt_desde, dt_hasta)

    return templates.TemplateResponse(
        "web/ventas.html",
        {
            "request": request,
            "productos": productos,
            "usuarios": usuarios,
            "ventas": ventas,
            "map_prod": map_prod,
            "map_user": map_user,
            "desde": desde or "",
            "hasta": hasta or "",
            "producto_id": producto_id,
            "usuario_id": usuario_id,
            "msg": msg,
            "resumen": resumen,
        },
    )


@router.post("/web/ventas")
async def crear_venta_html(
    request: Request,
    db: AsyncSession = Depends(get_db),
    id_usuario: int = Form(...),
    id_producto: int = Form(...),
    cantidad_vendida: int = Form(...),
):
    try:
        await crud.create_venta(
            db,
            schemas.VentaCreate(
                id_usuario=id_usuario,
                id_producto=id_producto,
                cantidad_vendida=cantidad_vendida,
            ),
        )
        url = "/web/ventas?msg=Venta%20registrada"
    except ValueError as e:
        # Mensajes de negocio: "Producto no existe", "Stock insuficiente", etc.
        url = f"/web/ventas?msg={str(e).replace(' ', '%20')}"
    except Exception as e:
        logger.exception("Error al crear venta: %s", e)
        url = "/web/ventas?msg=Error%20al%20crear%20venta"
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


# ---------- DASHBOARD (Top/Menos vendidos + resumen) ----------
@router.get("/web/dashboard", response_class=HTMLResponse)
async def pagina_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    top = await crud.list_productos_mas_vendidos(db, limit=10)
    bottom = await crud.list_productos_menos_vendidos(db, limit=10)
    resumen = await crud.resumen_ventas_periodo(db)
    return templates.TemplateResponse(
        "web/dashboard.html",
        {"request": request, "top": top, "bottom": bottom, "resumen": resumen},
    )


@router.post("/web/dashboard/rebuild")
async def rebuild_dashboard(db: AsyncSession = Depends(get_db)):
    await crud.rebuild_resumenes_ventas(db)
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)
