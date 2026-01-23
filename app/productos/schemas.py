# schemas.py para productos y categorías

from pydantic import BaseModel, Field
from typing import Optional

class CategoriaBase(BaseModel):
    id_microempresa: Optional[int] = None
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    activo: Optional[bool] = True

from datetime import datetime

class CategoriaResponse(CategoriaBase):
    id_categoria: int
    activo: bool
    fecha_creacion: datetime
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    precio_venta: float
    costo_compra: Optional[float] = None
    codigo: Optional[str] = None
    imagen: Optional[str] = None
    estado: Optional[bool] = True
    id_categoria: int
    id_microempresa: Optional[int] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id_producto: int
    fecha_creacion: datetime
    class Config:
        from_attributes = True
