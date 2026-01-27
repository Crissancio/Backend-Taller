from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# --- RUBRO ---
class RubroBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = None

    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre del rubro es obligatorio y no puede estar vacío')
        return v

class RubroCreate(RubroBase):
    activo: Optional[bool] = True

class RubroUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El nombre del rubro no puede estar vacío')
        return v

class RubroResponse(RubroBase):
    id_rubro: int
    activo: bool

    class Config:
        from_attributes = True

# --- MICROEMPRESAS ---
class MicroempresaBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    nit: str = Field(..., min_length=1)
    correo_contacto: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    tipo_atencion: str = Field(..., min_length=1)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    dias_atencion: Optional[str] = None
    horario_atencion: Optional[str] = None
    moneda: str = Field("BOB", min_length=1)
    logo: Optional[str] = None
    id_rubro: int

    @validator('nombre', 'nit', 'tipo_atencion', 'moneda')
    def no_vacio(cls, v):
        if not v or not str(v).strip():
            raise ValueError('Campo obligatorio y no puede estar vacío')
        return v

class MicroempresaCreate(MicroempresaBase):
    pass

class MicroempresaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    nit: Optional[str] = Field(None, min_length=1)
    correo_contacto: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    tipo_atencion: Optional[str] = Field(None, min_length=1)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    dias_atencion: Optional[str] = None
    horario_atencion: Optional[str] = None
    moneda: Optional[str] = None
    logo: Optional[str] = None
    id_rubro: Optional[int] = None

    @validator('nombre', 'nit', 'tipo_atencion', 'moneda')
    def no_vacio(cls, v):
        if v is not None and not str(v).strip():
            raise ValueError('Campo no puede estar vacío')
        return v

class MicroempresaResponse(MicroempresaBase):
    id_microempresa: int
    estado: bool
    fecha_registro: datetime
    rubro: Optional[RubroResponse] = None

    class Config:
        from_attributes = True