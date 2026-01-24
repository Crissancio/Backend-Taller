from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.proveedores.schemas import ProveedorResponse # Importar esquema de proveedor

# --------- DetalleCompra (Mover arriba) ---------
class DetalleCompraCreate(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float

class DetalleCompraResponse(BaseModel):
    id_detalle_compra: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    class Config:
        from_attributes = True

# --------- Compra ---------
class CompraCreate(BaseModel):
    id_microempresa: int
    id_proveedor: int
    observacion: Optional[str] = None
    metodo_pago: str # EFECTIVO, QR, ETC
    detalles: List[DetalleCompraCreate] # ✅ AHORA ACEPTA DETALLES

class CompraResponse(BaseModel):
    id_compra: int
    fecha: datetime
    total: float
    estado: str
    observacion: Optional[str] = None
    
    # ✅ ESTO HACE QUE APAREZCA EL NOMBRE EN LA LISTA
    proveedor: Optional[ProveedorResponse] = None 

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
    monto: float
    fecha: datetime
    class Config:
        from_attributes = True