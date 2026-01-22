from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DetalleVentaBase(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVentaResponse(DetalleVentaBase):
    id_detalle: int
    class Config:
        from_attributes = True

class PagoVentaBase(BaseModel):
    metodo: str
    comprobante_url: Optional[str] = None
    estado: str
    fecha: Optional[datetime] = None

class PagoVentaCreate(PagoVentaBase):
    pass

class PagoVentaResponse(PagoVentaBase):
    id_pago: int
    id_venta: int
    class Config:
        from_attributes = True

class VentaBase(BaseModel):
    id_microempresa: int
    id_cliente: Optional[int] = None
    total: float
    estado: str
    tipo: str
    fecha: Optional[datetime] = None

class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]
    pagos: Optional[List[PagoVentaCreate]] = None

class VentaResponse(VentaBase):
    id_venta: int
    detalles: List[DetalleVentaResponse] = []
    pagos: List[PagoVentaResponse] = []
    class Config:
        from_attributes = True
