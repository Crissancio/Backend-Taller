from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    nombre: str
    documento: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None

class ClienteCreate(ClienteBase):
    id_microempresa: int

class ClienteUpdate(ClienteBase):
    estado: Optional[bool] = None

class ClienteResponse(ClienteBase):
    id_cliente: int
    id_microempresa: int
    fecha_creacion: datetime
    estado: bool

    class Config:
        from_attributes = True
