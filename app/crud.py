# app/crud.py (async)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, delete
from sqlalchemy.exc import IntegrityError
from . import models, schemas

# ===== USUARIOS =====
async def create_usuario(db: AsyncSession, data: schemas.UsuarioCreate):
    obj = models.Usuario(
        nombre_usuario=data.nombre_usuario,
        correo=data.correo,
        rol=data.rol,
        foto_url=getattr(data, "foto_url", None),
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
    return obj

# ===== PRODUCTOS =====
async def list_productos(db: AsyncSession):
    res = await db.execute(select(models.Producto).order_by(models.Producto.id_producto))
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
    return obj

# ===== VENTAS =====
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

    await db.commit()
    await db.refresh(venta)
    return venta

async def list_ventas(db: AsyncSession, desde=None, hasta=None, producto_id: int | None = None, usuario_id: int | None = None):
    stmt = select(models.Venta)
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

# ===== MOVIMIENTOS =====
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

# ===== RESÚMENES PERSISTIDOS =====
from .models import ProductoMasVendido as PMV, ProductoMenosVendido as PMeV

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
    res = await db.execute(select(PMV).order_by(PMV.total_vendido.desc()).limit(limit))
    return res.scalars().all()

async def list_productos_menos_vendidos(db: AsyncSession, limit: int = 10):
    res = await db.execute(select(PMeV).order_by(PMeV.total_vendido.asc()).limit(limit))
    return res.scalars().all()

# ===== REPORTES ADICIONALES =====
from datetime import datetime
async def resumen_ventas_periodo(db: AsyncSession, desde: datetime | None = None, hasta: datetime | None = None):
    q_stmt = select(models.Venta)
    if desde:
        q_stmt = q_stmt.where(models.Venta.fecha_venta >= desde)
    if hasta:
        q_stmt = q_stmt.where(models.Venta.fecha_venta <= hasta)
    ventas = (await db.execute(q_stmt)).scalars().all()

    total_unidades = sum(v.cantidad_vendida for v in ventas)
    total_ventas = round(sum(v.total_venta for v in ventas), 2)
    ticket_prom = round(total_ventas / len(ventas), 2) if ventas else 0.0

    agg = (
        select(
            models.Venta.id_producto,
            models.Producto.nombre,
            func.sum(models.Venta.cantidad_vendida).label("unidades"),
            func.sum(models.Venta.total_venta).label("monto"),
        )
        .join(models.Producto, models.Producto.id_producto == models.Venta.id_producto)
    )
    if desde:
        agg = agg.where(models.Venta.fecha_venta >= desde)
    if hasta:
        agg = agg.where(models.Venta.fecha_venta <= hasta)
    agg = agg.group_by(models.Venta.id_producto, models.Producto.nombre).order_by(func.sum(models.Venta.total_venta).desc())

    por_producto = [
        {"id_producto": r.id_producto, "nombre": r.nombre, "unidades": int(r.unidades), "monto": float(round(r.monto, 2))}
        for r in (await db.execute(agg)).all()
    ]

    return {
        "total_unidades": int(total_unidades),
        "total_ventas": float(total_ventas),
        "ventas_count": len(ventas),
        "ticket_promedio": float(ticket_prom),
        "por_producto": por_producto,
    }

async def reconciliacion_stock(db: AsyncSession):
    subq = (
        select(
            models.InventarioMovimiento.id_producto.label("id_producto"),
            func.sum(
                case(
                    (models.InventarioMovimiento.tipo_movimiento == "entrada", models.InventarioMovimiento.cantidad),
                    else_=-models.InventarioMovimiento.cantidad,
                )
            ).label("stock_por_movs")
        )
        .group_by(models.InventarioMovimiento.id_producto)
        .subquery()
    )
    stmt = (
        select(
            models.Producto.id_producto,
            models.Producto.nombre,
            models.Producto.cantidad.label("stock_actual"),
            func.coalesce(subq.c.stock_por_movs, 0).label("stock_por_movimientos"),
        )
        .outerjoin(subq, subq.c.id_producto == models.Producto.id_producto)
        .order_by(models.Producto.id_producto)
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "id_producto": r.id_producto,
            "nombre": r.nombre,
            "stock_actual": int(r.stock_actual),
            "stock_por_movimientos": int(r.stock_por_movimientos),
            "diferencia": int(r.stock_actual - r.stock_por_movimientos),
            "nota": "Registra una 'entrada' inicial para cuadrar si acabas de crear el producto con stock inicial.",
        }
        for r in rows
    ]
