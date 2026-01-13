from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth import schemas, service
from app.users.schemas import UsuarioResponse
from app.auth.schemas import RegistroUsuario


router = APIRouter()

# ---------- REGISTRO USUARIO BASE ----------
@router.post("/register/usuario", response_model=UsuarioResponse)
def registrar_usuario(data: RegistroUsuario, db: Session = Depends(get_db)):
    return service.crear_usuario_base(db, data)
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

# ---------- LOGIN ----------
@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    token = service.login(db, data.email, data.password)
    return {"access_token": token}

# ---------- USUARIO AUTENTICADO ----------
@router.get("/me", response_model=UsuarioResponse)
def me(user = Depends(get_current_user)):
    return user

# ---------- RECUPERACIÓN DE CONTRASEÑA ----------
@router.post("/recover")
def recover(data: schemas.RecuperacionRequest):
    token = service.generar_token_recuperacion(data.email)
    return {"reset_token": token}


@router.put("/admin/{id_usuario}/asignar-microempresa")
def asignar_microempresa(id_usuario: int, id_microempresa: int, db: Session = Depends(get_db)):
    return service.asignar_microempresa_a_admin(db, id_usuario, id_microempresa)