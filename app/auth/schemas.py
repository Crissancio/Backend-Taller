from pydantic import BaseModel, EmailStr

# -------- REGISTROS --------
class RegistroBase(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class RegistroVendedor(RegistroBase):
    id_microempresa: int

class RegistroAdminMicroempresa(RegistroBase):
    id_microempresa: int

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
