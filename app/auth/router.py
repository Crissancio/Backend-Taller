from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth import schemas, service
from app.users.schemas import UsuarioResponse
from app.core.dependencies import get_current_user

router = APIRouter()

# ---------- REGISTRO ----------
@router.post("/register/vendedor", response_model=UsuarioResponse)
def registrar_vendedor(data: schemas.RegistroVendedor, db: Session = Depends(get_db)):
    return service.crear_vendedor(db, data)

@router.post("/register/admin", response_model=UsuarioResponse)
def registrar_admin(data: schemas.RegistroAdminMicroempresa, db: Session = Depends(get_db)):
    return service.crear_admin_microempresa(db, data)

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
