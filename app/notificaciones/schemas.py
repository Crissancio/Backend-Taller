# schemas.py para notificaciones

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# --- SCHEMAS EXTENDIDOS DE NOTIFICACION ---
class NotificacionBase(BaseModel):
    id_microempresa: int
    id_usuario: int
    tipo_evento: str
    canal: str  # IN_APP, EMAIL, WHATSAPP
    mensaje: str
    leido: Optional[bool] = False
    enviado: Optional[bool] = False

class NotificacionCreate(NotificacionBase):
    pass

class NotificacionUpdate(BaseModel):
    leido: Optional[bool] = None
    mensaje: Optional[str] = None
    enviado: Optional[bool] = None

class NotificacionResponse(NotificacionBase):
    id_notificacion: int
    fecha_creacion: Optional[datetime] = None
    class Config:
        from_attributes = True


# --- NUEVO: Schemas para PreferenciaNotificacion ---
class PreferenciaNotificacionBase(BaseModel):
    id_usuario: int
    tipo_evento: str
    canal: str
    activo: Optional[bool] = True

class PreferenciaNotificacionCreate(PreferenciaNotificacionBase):
    pass

class PreferenciaNotificacionUpdate(BaseModel):
    activo: Optional[bool] = None

class PreferenciaNotificacionResponse(PreferenciaNotificacionBase):
    id_preferencia: int
    class Config:
        from_attributes = True


# --- NUEVO: Schemas para EventoSistema ---
class EventoSistemaBase(BaseModel):
    id_microempresa: int
    tipo_evento: str
    referencia_id: Optional[int] = None
    descripcion: str

class EventoSistemaCreate(EventoSistemaBase):
    pass

class EventoSistemaResponse(EventoSistemaBase):
    id_evento: int
    fecha_evento: datetime
    class Config:
        from_attributes = True


# --- NUEVO: Schemas para notificacion_preferencia ---
class NotificacionPreferenciaBase(BaseModel):
    id_usuario: int
    tipo_evento: str
    recibir_app: Optional[bool] = True
    recibir_email: Optional[bool] = False
    recibir_whatsapp: Optional[bool] = False
    activo: Optional[bool] = True

class NotificacionPreferenciaCreate(NotificacionPreferenciaBase):
    pass

class NotificacionPreferenciaUpdate(BaseModel):
    recibir_app: Optional[bool] = None
    recibir_email: Optional[bool] = None
    recibir_whatsapp: Optional[bool] = None
    activo: Optional[bool] = None

class NotificacionPreferenciaResponse(NotificacionPreferenciaBase):
    id_preferencia: int
    class Config:
        from_attributes = True


# --- NUEVO: Schemas para notificacion_email_log ---
class NotificacionEmailLogBase(BaseModel):
    id_notificacion: int
    email_destino: Optional[str] = None
    estado: Optional[str] = None
    fecha_envio: Optional[datetime] = None

class NotificacionEmailLogCreate(NotificacionEmailLogBase):
    pass

class NotificacionEmailLogResponse(NotificacionEmailLogBase):
    id_log: int
    class Config:
        from_attributes = True
