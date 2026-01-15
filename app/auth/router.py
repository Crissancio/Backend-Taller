from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth import schemas, service
from app.core.security import verify_password, hash_password
from app.core.email_utils import send_recovery_email
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, ALGORITHM

from app.users.schemas import UsuarioResponse
from app.auth.schemas import RegistroUsuario
from fastapi import Form
from pydantic import BaseModel


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# ---------- REGISTRO USUARIO BASE ----------

# El registro de usuario base debe estar solo en /usuarios (módulo users)
from app.core.dependencies import get_current_user

# ---------- REGISTRO ----------
@router.post("/register/vendedor", response_model=UsuarioResponse)
def registrar_vendedor(data: schemas.RegistroVendedor, db: Session = Depends(get_db)):
    return service.crear_vendedor(db, data)

@router.post("/register/admin", response_model=UsuarioResponse)
def registrar_admin(data: schemas.RegistroAdminMicroempresa, db: Session = Depends(get_db)):
    return service.crear_admin_microempresa(db, data)

# ---------- ASIGNAR MICROEMPRESA A ADMIN ----------
@router.put("/admin/{id_usuario}/asignar-microempresa")
def asignar_microempresa(id_usuario: int, id_microempresa: int, db: Session = Depends(get_db)):
    return service.asignar_microempresa_a_admin(db, id_usuario, id_microempresa)

@router.post("/register/superadmin", response_model=UsuarioResponse)
def registrar_superadmin(data: schemas.RegistroSuperAdmin, db: Session = Depends(get_db)):
    return service.crear_superadmin(db, data)





# ---------- RECUPERACIÓN DE CONTRASEÑA ----------

# Endpoint para solicitar recuperación de contraseña (sin envío de correo temporalmente)
@router.post("/recover")
def recover(data: schemas.RecuperacionRequest):
    token = service.generar_token_recuperacion(data.email)
    return {"reset_token": token}


@router.put("/admin/{id_usuario}/asignar-microempresa")
def asignar_microempresa(id_usuario: int, id_microempresa: int, db: Session = Depends(get_db)):
    return service.asignar_microempresa_a_admin(db, id_usuario, id_microempresa)

# --- CRUD SUPERADMIN ---


class RecuperarPasswordRequest(BaseModel):
    token: str
    nueva_password: str

@router.post("/reset-password")
def reset_password(data: RecuperarPasswordRequest = Body(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    usuario = db.query(service.Usuario).filter_by(email=email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.password_hash = hash_password(data.nueva_password)
    db.commit()
    return {"detail": "Contraseña actualizada correctamente"}