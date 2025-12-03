# app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Literal, Optional


# ====== USUARIOS ======
class UsuarioBase(BaseModel):
    nombre_usuario: str
    correo: EmailStr
    rol: str
    foto_url: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre_usuario: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol: Optional[str] = None
    foto_url: Optional[str] = None

class UsuarioOut(UsuarioBase):
    id_usuario: int
    class Config:
        from_attributes = True


# ====== PRODUCTOS ======
class ProductoBase(BaseModel):
    nombre: str
    categoria: str
    marca: str
    cantidad: int = Field(ge=0)
    precio_venta: float = Field(ge=0)
    imagen_url: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    marca: Optional[str] = None
    cantidad: Optional[int] = Field(default=None, ge=0)
    precio_venta: Optional[float] = Field(default=None, ge=0)
    imagen_url: Optional[str] = None

class ProductoOut(ProductoBase):
    id_producto: int
    class Config:
        from_attributes = True


# ====== VENTAS ======
class VentaCreate(BaseModel):
    id_usuario: int
    id_producto: int
    cantidad_vendida: int = Field(ge=1)

class VentaOut(BaseModel):
    id_venta: int
    id_usuario: int
    id_producto: int
    cantidad_vendida: int
    total_venta: float
    class Config:
        from_attributes = True


# ====== MOVIMIENTOS ======
class MovimientoBase(BaseModel):
    id_producto: int
    tipo_movimiento: Literal["entrada", "salida"]
    cantidad: int
    descripcion: Optional[str] = None

class MovimientoCreate(MovimientoBase):
    pass

class MovimientoOut(MovimientoBase):
    id_movimiento: int
    fecha_movimiento: datetime

    class Config:
        from_attributes = True
