from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ===== Usuarios =====
class UsuarioBase(BaseModel):
    nombre_usuario: str
    correo: EmailStr
    rol: str = Field("consulta", pattern="^(administrador|consulta)$")

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre_usuario: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol: Optional[str] = Field(None, pattern="^(administrador|consulta)$")

class UsuarioOut(UsuarioBase):
    id_usuario: int
    creado_en: datetime
    class Config:
        from_attributes = True

# ===== Productos =====
class ProductoBase(BaseModel):
    nombre: str
    categoria: Optional[str] = None
    marca: Optional[str] = None
    cantidad: int = 0
    precio_venta: float
    imagen_url: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    marca: Optional[str] = None
    cantidad: Optional[int] = None
    precio_venta: Optional[float] = None
    imagen_url: Optional[str] = None

class ProductoOut(ProductoBase):
    id_producto: int
    fecha_agregado: datetime
    class Config:
        from_attributes = True

# ===== Ventas =====
class VentaCreate(BaseModel):
    id_usuario: int
    id_producto: int
    cantidad_vendida: int

class VentaOut(BaseModel):
    id_venta: int
    id_usuario: int
    id_producto: int
    cantidad_vendida: int
    fecha_venta: datetime
    total_venta: float
    class Config:
        from_attributes = True

# ===== Movimientos =====
class MovimientoCreate(BaseModel):
    id_producto: int
    tipo_movimiento: str  # 'entrada' | 'salida'
    cantidad: int
    descripcion: Optional[str] = None

class MovimientoOut(BaseModel):
    id_movimiento: int
    id_producto: int
    tipo_movimiento: str
    cantidad: int
    fecha_movimiento: datetime
    descripcion: Optional[str] = None
    class Config:
        from_attributes = True

# ===== Reportes persistidos =====
class ResumenVendidosOut(BaseModel):
    id_producto: int
    nombre: str
    total_vendido: int
    actualizado_en: datetime
    class Config:
        from_attributes = True
