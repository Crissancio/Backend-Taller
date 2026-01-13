
from typing import Optional
from pydantic import BaseModel, EmailStr

class RegistroUsuario(BaseModel):
    nombre: str
    email: EmailStr
    password: str

# -------- REGISTROS --------
class RegistroBase(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class RegistroVendedor(RegistroBase):
    id_microempresa: Optional[int] = None  # Ahora es opcional

from typing import Optional

class RegistroAdminMicroempresa(RegistroBase):
    id_microempresa: Optional[int] = None  # Ahora es opcional

class RegistroSuperAdmin(RegistroBase):
    pass

# -------- LOGIN --------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -------- RECUPERACIÓN --------
class RecuperacionRequest(BaseModel):
    email: EmailStr
