# app/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func, String


class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre_usuario: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="consulta")
    foto_url = Column(String, nullable=True)
    creado_en: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Producto(Base):
    __tablename__ = "productos"
    id_producto: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    precio_venta: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    imagen_url = Column(String, nullable=True)
    fecha_agregado: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Venta(Base):
    __tablename__ = "ventas"
    id_venta: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    id_producto: Mapped[int] = mapped_column(ForeignKey("productos.id_producto"), nullable=False)
    cantidad_vendida: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_venta: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    total_venta: Mapped[float] = mapped_column(Float, nullable=False, default=0)

class InventarioMovimiento(Base):
    __tablename__ = "inventario_movimientos"
    id_movimiento: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_producto: Mapped[int] = mapped_column(ForeignKey("productos.id_producto"), nullable=False)
    tipo_movimiento: Mapped[str] = mapped_column(String(10), nullable=False)  # 'entrada'/'salida'
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_movimiento: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    descripcion: Mapped[str] = mapped_column(String(255), nullable=True)

class ProductoMasVendido(Base):
    __tablename__ = "productos_mas_vendidos"
    id_producto: Mapped[int] = mapped_column(ForeignKey("productos.id_producto"), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    total_vendido: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actualizado_en: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ProductoMenosVendido(Base):
    __tablename__ = "productos_menos_vendidos"
    id_producto: Mapped[int] = mapped_column(ForeignKey("productos.id_producto"), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    total_vendido: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actualizado_en: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())