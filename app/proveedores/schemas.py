# schemas.py para el módulo de proveedores
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --------- Proveedor ---------
class ProveedorBase(BaseModel):
	nombre: str
	contacto: Optional[str] = None
	email: Optional[str] = None

class ProveedorCreate(ProveedorBase):
	id_microempresa: int

class ProveedorUpdate(BaseModel):
	nombre: Optional[str] = None
	contacto: Optional[str] = None
	email: Optional[str] = None

class ProveedorResponse(BaseModel):
	id_proveedor: int
	nombre: str
	contacto: Optional[str] = None
	email: Optional[str] = None
	estado: bool
	fecha_registro: datetime
	class Config:
		from_attributes = True


# --------- ProveedorMetodoPago ---------
class ProveedorMetodoPagoCreate(BaseModel):
	tipo: str
	descripcion: Optional[str] = None
	datos_pago: Optional[str] = None
	qr_imagen: Optional[str] = None

class ProveedorMetodoPagoResponse(BaseModel):
	id_metodo_pago: int
	id_proveedor: int
	tipo: str
	descripcion: Optional[str] = None
	datos_pago: Optional[str] = None
	qr_imagen: Optional[str] = None
	activo: bool
	class Config:
		from_attributes = True


# --------- ProveedorProducto ---------
class ProveedorProductoCreate(BaseModel):
	id_producto: int
	precio_referencia: Optional[float] = None

class ProveedorProductoResponse(BaseModel):
	id_proveedor: int
	id_producto: int
	precio_referencia: Optional[float] = None
	activo: bool
	class Config:
		from_attributes = True
