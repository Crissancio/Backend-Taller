from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SuscripcionBase(BaseModel):
    id_microempresa: int
    id_plan: int

class SuscripcionCreate(SuscripcionBase):
    fecha_fin: Optional[datetime] = None

class SuscripcionResponse(SuscripcionBase):
    id_suscripcion: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    estado: bool
    class Config:
        from_attributes = True
