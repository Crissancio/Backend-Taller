# schemas.py para notificaciones

from pydantic import BaseModel, Field
from typing import Optional

class NotificacionBase(BaseModel):
    id_microempresa: int
    id_usuario: int
    tipo: Optional[str] = None
    mensaje: str
    leido: Optional[bool] = False

class NotificacionCreate(NotificacionBase):
    pass

class NotificacionUpdate(BaseModel):
    leido: Optional[bool] = None
    mensaje: Optional[str] = None
    tipo: Optional[str] = None

class NotificacionResponse(NotificacionBase):
    id_notificacion: int
    fecha_creacion: str
    class Config:
        from_attributes = True
