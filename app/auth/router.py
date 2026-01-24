from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth import schemas, service

from app.core.security import verify_password, hash_password
from app.core.email_utils import send_recovery_email
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.dependencies import get_user_role

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
def registrar_vendedor(data: schemas.RegistroVendedor, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Usar el email como contraseña por defecto
    password_defecto = data.email
    # Obtener el id_microempresa del admin autenticado
    rol = get_user_role(user, db)
    id_microempresa = None
    if rol == "adminmicroempresa" and hasattr(user, 'admin_microempresa') and user.admin_microempresa:
        id_microempresa = user.admin_microempresa.id_microempresa
    else:
        raise HTTPException(status_code=403, detail="Solo un adminmicroempresa puede registrar vendedores")
    # Construir el objeto de registro
    vendedor_data = schemas.RegistroVendedor(
        nombre=data.nombre,
        email=data.email,
        password=password_defecto,
        id_microempresa=id_microempresa
    )
    nuevo_usuario = service.crear_vendedor(db, vendedor_data)
    # Construir respuesta con rol
    return {
        "id_usuario": nuevo_usuario.id_usuario,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email,
        "estado": nuevo_usuario.estado,
        "rol": "vendedor"
    }

@router.post("/register/admin", response_model=UsuarioResponse)
def registrar_admin(data: schemas.RegistroAdminMicroempresa, db: Session = Depends(get_db)):
    return service.crear_admin_microempresa(db, data)

# ---------- ASIGNAR MICROEMPRESA A ADMIN ----------
@router.put("/admin/{id_usuario}/asignar-microempresa")
def asignar_microempresa(id_usuario: int, id_microempresa: int, db: Session = Depends(get_db)):
    return service.asignar_microempresa_a_admin(db, id_usuario, id_microempresa)


@router.post("/register/superadmin", response_model=UsuarioResponse)
def registrar_superadmin(data: schemas.RegistroSuperAdmin, db: Session = Depends(get_db)):
    nuevo_usuario = service.crear_superadmin(db, data)
    return {
        "id_usuario": nuevo_usuario.id_usuario,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email,
        "estado": nuevo_usuario.estado,
        "rol": "superadmin"
    }





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