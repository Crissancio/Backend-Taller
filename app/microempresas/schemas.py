from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- MICROEMPRESAS ---
class MicroempresaBase(BaseModel):
    nombre: str
    nit: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    moneda: Optional[str] = "BOB"

class MicroempresaCreate(MicroempresaBase):
    pass

class MicroempresaResponse(MicroempresaBase):
    id_microempresa: int
    estado: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True

# --- SUSCRIPCIONES ---
class SuscripcionCreate(BaseModel):
    id_plan: int

class SuscripcionResponse(BaseModel):
    id_suscripcion: int
    id_microempresa: int
    plan: str
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: bool

    class Config:
        from_attributes = True
