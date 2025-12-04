# app/crud.py
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, case, or_, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from .models import ProductoMasVendido as PMV, ProductoMenosVendido as PMeV
from types import SimpleNamespace

# =============== USUARIOS ===============
async def create_usuario(db: AsyncSession, data: schemas.UsuarioCreate):
    obj = models.Usuario(
        nombre_usuario=data.nombre_usuario,
        correo=data.correo,
        rol=data.rol,
        foto_url=data.foto_url,
    )
    db.add(obj)
    try:
        await db.commit()
        await db.refresh(obj)
        return obj
    except IntegrityError:
        await db.rollback()
        raise ValueError("El correo ya está registrado")

async def list_usuarios(db: AsyncSession):
    res = await db.execute(select(models.Usuario).order_by(models.Usuario.id_usuario))
    return res.scalars().all()

async def get_usuario(db: AsyncSession, usuario_id: int):
    return await db.get(models.Usuario, usuario_id)

async def update_usuario(db: AsyncSession, usuario_id: int, data: schemas.UsuarioUpdate):
    obj = await db.get(models.Usuario, usuario_id)
    if not obj:
        return None
    payload = data.model_dump(exclude_unset=True)
    for k, v in payload.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete_usuario(db: AsyncSession, usuario_id: int):
    obj = await db.get(models.Usuario, usuario_id)
    if not obj:
        return None
    await db.delete(obj)
    await db.commit()
    return True


# =============== PRODUCTOS ===============
async def list_productos(db: AsyncSession):
    res = await db.execute(select(models.Producto).order_by(models.Producto.id_producto))
    return res.scalars().all()

async def search_productos(db: AsyncSession, q: Optional[str], limit: int = 50, offset: int = 0):
    stmt = select(models.Producto).order_by(models.Producto.id_producto)
    if q:
        iq = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(models.Producto.nombre).ilike(iq),
                func.lower(models.Producto.categoria).ilike(iq),
                func.lower(models.Producto.marca).ilike(iq),
            )
        )
    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    return res.scalars().all()

async def get_producto(db: AsyncSession, producto_id: int):
    return await db.get(models.Producto, producto_id)

async def create_producto(db: AsyncSession, data: schemas.ProductoCreate):
    obj = models.Producto(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def update_producto(db: AsyncSession, producto_id: int, data: schemas.ProductoUpdate):
    obj = await db.get(models.Producto, producto_id)
    if not obj:
        return None
    payload = data.model_dump(exclude_unset=True)
    for k, v in payload.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete_producto(db: AsyncSession, producto_id: int):
    obj = await db.get(models.Producto, producto_id)
    if not obj:
        return None
    await db.delete(obj)
    await db.commit()
    return True


# =============== VENTAS ===============
async def create_venta(db: AsyncSession, data: schemas.VentaCreate):
    producto = await db.get(models.Producto, data.id_producto)
    if not producto:
        raise ValueError("Producto no existe")

    if producto.cantidad < data.cantidad_vendida:
        raise ValueError("Stock insuficiente")

    usuario = await db.get(models.Usuario, data.id_usuario)
    if not usuario:
        raise ValueError("Usuario no existe")

    # Actualiza stock
    producto.cantidad -= data.cantidad_vendida

    total = round(producto.precio_venta * data.cantidad_vendida, 2)
    venta = models.Venta(
        id_usuario=data.id_usuario,
        id_producto=data.id_producto,
        cantidad_vendida=data.cantidad_vendida,
        total_venta=total,
    )
    db.add(venta)

    # Registrar movimiento de salida
    mov = models.InventarioMovimiento(
        id_producto=data.id_producto,
        tipo_movimiento="salida",
        cantidad=data.cantidad_vendida,
        descripcion="venta",
    )
    db.add(mov)

    # Asegura asignación de ID antes del commit (útil para logs/depuración)
    await db.flush()

    await db.commit()
    await db.refresh(venta)
    return venta
async def list_ventas(
    db: AsyncSession,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    producto_id: int | None = None,
    usuario_id: int | None = None,
    solo_activos: bool = False,   # <--- parámetro opcional
):
    stmt = select(models.Venta)
    if solo_activos:
        stmt = (
            stmt.join(models.Producto, models.Producto.id_producto == models.Venta.id_producto)
                .join(models.Usuario, models.Usuario.id_usuario == models.Venta.id_usuario)
                .where(models.Producto.activo.is_(True), models.Usuario.activo.is_(True))
        )

    if desde:
        stmt = stmt.where(models.Venta.fecha_venta >= desde)
    if hasta:
        stmt = stmt.where(models.Venta.fecha_venta <= hasta)
    if producto_id:
        stmt = stmt.where(models.Venta.id_producto == producto_id)
    if usuario_id:
        stmt = stmt.where(models.Venta.id_usuario == usuario_id)

    res = await db.execute(stmt.order_by(models.Venta.id_venta.desc()))
    return res.scalars().all()

async def get_venta(db: AsyncSession, venta_id: int):
    return await db.get(models.Venta, venta_id)


# =============== MOVIMIENTOS ===============
async def create_movimiento(db: AsyncSession, data: schemas.MovimientoCreate):
    producto = await db.get(models.Producto, data.id_producto)
    if not producto:
        raise ValueError("Producto no existe")

    if data.tipo_movimiento == "entrada":
        producto.cantidad += data.cantidad
    elif data.tipo_movimiento == "salida":
        if producto.cantidad < data.cantidad:
            raise ValueError("Stock insuficiente para salida")
        producto.cantidad -= data.cantidad
    else:
        raise ValueError("tipo_movimiento inválido (use 'entrada' o 'salida')")

    mov = models.InventarioMovimiento(
        id_producto=data.id_producto,
        tipo_movimiento=data.tipo_movimiento,
        cantidad=data.cantidad,
        descripcion=data.descripcion,
    )
    db.add(mov)
    await db.commit()
    await db.refresh(mov)
    return mov

async def list_movimientos(db: AsyncSession, producto_id: int | None = None):
    stmt = select(models.InventarioMovimiento)
    if producto_id:
        stmt = stmt.where(models.InventarioMovimiento.id_producto == producto_id)
    res = await db.execute(stmt.order_by(models.InventarioMovimiento.id_movimiento.desc()))
    return res.scalars().all()


# =============== RESÚMENES PERSISTIDOS ===============
async def rebuild_resumenes_ventas(db: AsyncSession):
    # Limpia tablas
    await db.execute(delete(PMV))
    await db.execute(delete(PMeV))
    await db.commit()

    agg = (
        select(
            models.Venta.id_producto,
            models.Producto.nombre,
            func.sum(models.Venta.cantidad_vendida).label("total_vendido"),
        )
        .join(models.Producto, models.Producto.id_producto == models.Venta.id_producto)
        .group_by(models.Venta.id_producto, models.Producto.nombre)
    )
    rows = (await db.execute(agg)).all()

    for r in rows:
        db.add(PMV(id_producto=r.id_producto, nombre=r.nombre, total_vendido=int(r.total_vendido)))
        db.add(PMeV(id_producto=r.id_producto, nombre=r.nombre, total_vendido=int(r.total_vendido)))

    await db.commit()

async def list_productos_mas_vendidos(db: AsyncSession, limit: int = 10):
    p = models.Producto
    v = models.Venta
    stmt = (
        select(
            p.id_producto,
            p.nombre,
            func.coalesce(func.sum(v.cantidad_vendida), 0).label("total_vendido"),
        )
        .join(v, v.id_producto == p.id_producto, isouter=True)
        .group_by(p.id_producto, p.nombre)
        .order_by(text("total_vendido DESC"))
        .limit(limit)
    )
    res = await db.execute(stmt)
    rows = res.all()
    return [
        SimpleNamespace(id_producto=idp, nombre=nom, total_vendido=tot or 0)
        for (idp, nom, tot) in rows
    ]

async def list_productos_menos_vendidos(db: AsyncSession, limit: int = 10):
    p = models.Producto
    v = models.Venta
    stmt = (
        select(
            p.id_producto,
            p.nombre,
            func.coalesce(func.sum(v.cantidad_vendida), 0).label("total_vendido"),
        )
        .join(v, v.id_producto == p.id_producto, isouter=True)
        .group_by(p.id_producto, p.nombre)
        .order_by(text("total_vendido ASC"))
        .limit(limit)
    )
    res = await db.execute(stmt)
    rows = res.all()
    return [
        SimpleNamespace(id_producto=idp, nombre=nom, total_vendido=tot or 0)
        for (idp, nom, tot) in rows
    ]


# =============== REPORTES EXTRA ===============
async def resumen_ventas_periodo(db: AsyncSession, desde=None, hasta=None):
        v = models.Venta
        stmt = select(
            func.count(v.id_venta).label("n_ventas"),
            func.coalesce(func.sum(v.cantidad_vendida), 0).label("unidades"),
            func.coalesce(func.sum(v.total_venta), 0.0).label("monto"),
        )
        if desde is not None:
            stmt = stmt.where(v.fecha_venta >= desde)
        if hasta is not None:
            stmt = stmt.where(v.fecha_venta <= hasta)

        res = await db.execute(stmt)
        n_ventas, unidades, monto = res.one()

        total_ventas = int(n_ventas or 0)
        unidades_vendidas = int(unidades or 0)
        monto_total = float(monto or 0.0)
        ticket_promedio = float(monto_total / total_ventas) if total_ventas > 0 else 0.0

        return {
            "total_ventas": total_ventas,
            "unidades_vendidas": unidades_vendidas,
            "monto_total": monto_total,
            "ticket_promedio": ticket_promedio,
        }