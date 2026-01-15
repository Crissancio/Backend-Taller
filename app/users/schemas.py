from typing import Optional
from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
class UsuarioCreate(UsuarioBase):
    password: str
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    estado: Optional[bool] = None
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioResponse(UsuarioBase):

    id_usuario: int
    estado: bool
    rol: str
    id_microempresa: Optional[int] = None

    class Config:
        from_attributes = True
