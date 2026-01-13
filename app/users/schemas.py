from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    estado: bool

    class Config:
        from_attributes = True
