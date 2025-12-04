# app/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func, String
import sqlalchemy as sa
from .database import Base

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
    activo = sa.Column(sa.Boolean, nullable=False, server_default=sa.true())
ventas = relationship("Venta", back_populates="usuario")

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
    activo = sa.Column(sa.Boolean, nullable=False, server_default=sa.true())
ventas = relationship("Venta", back_populates="producto")

class Venta(Base):
    __tablename__ = "ventas"

    id_venta = sa.Column(sa.Integer, primary_key=True, index=True)
    id_usuario = sa.Column(
        sa.Integer,
        sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_producto = sa.Column(
        sa.Integer,
        sa.ForeignKey("productos.id_producto", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cantidad_vendida = sa.Column(sa.Integer, nullable=False)
    total_venta = sa.Column(sa.Numeric(10, 2), nullable=False)
    fecha_venta = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)

    usuario = relationship("Usuario", passive_deletes=True)
    producto = relationship("Producto", passive_deletes=True)

class InventarioMovimiento(Base):
    __tablename__ = "inventario_movimientos"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto", ondelete="CASCADE"), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)  # 'entrada'|'salida'
    cantidad = Column(Integer, nullable=False)
    descripcion = Column(String(200))
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

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