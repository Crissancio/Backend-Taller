# schemas.py para el módulo de compras
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --------- Compra ---------
class CompraCreate(BaseModel):
	id_microempresa: Optional[int] = None  # Solo si no hay usuario logueado
	id_proveedor: int
	observacion: Optional[str] = None

class CompraResponse(BaseModel):
	id_compra: int
	fecha: datetime
	total: float
	estado: str
	observacion: Optional[str] = None
	class Config:
		from_attributes = True



# --------- DetalleCompra ---------
class DetalleCompraCreate(BaseModel):
	id_producto: int
	cantidad: int
	precio_unitario: float

class DetalleCompraResponse(BaseModel):
	id_detalle_compra: int
	id_compra: int
	id_producto: int
	cantidad: int
	precio_unitario: float
	subtotal: float
	class Config:
		from_attributes = True



# --------- PagoCompra ---------
class PagoCompraCreate(BaseModel):
	id_metodo_pago: Optional[int] = None
	monto: float
	comprobante_url: Optional[str] = None

class PagoCompraResponse(BaseModel):
	id_pago: int
	id_compra: int
	id_metodo_pago: Optional[int] = None
	monto: float
	comprobante_url: Optional[str] = None
	fecha: datetime
	class Config:
		from_attributes = True
