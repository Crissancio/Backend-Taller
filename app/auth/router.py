from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth import schemas, service
from app.core.security import verify_password, hash_password
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, ALGORITHM

from app.users.schemas import UsuarioResponse
from app.auth.schemas import RegistroUsuario
from fastapi import Form
from pydantic import BaseModel


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
def login(
    username: str = Form(..., description="Correo electrónico"),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    token = service.login(db, username, password)  # username es el email
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

# --- OBTENER ADMIN POR ID (restricciones) ---
@router.get("/admins/{id_usuario}", response_model=UsuarioResponse)
def obtener_admin(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.core.dependencies import get_user_role
    rol = get_user_role(user, db)
    admin = db.query(service.AdminMicroempresa).filter_by(id_usuario=id_usuario).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    if rol == 'superadmin':
        return admin.usuario
    elif rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == admin.id_microempresa:
        return admin.usuario
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# --- OBTENER VENDEDOR POR ID (restricciones) ---
@router.get("/vendedores/{id_usuario}", response_model=UsuarioResponse)
def obtener_vendedor(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.core.dependencies import get_user_role
    rol = get_user_role(user, db)
    vendedor = db.query(service.Vendedor).filter_by(id_usuario=id_usuario).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    if rol == 'superadmin':
        return vendedor.usuario
    elif rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == vendedor.id_microempresa:
        return vendedor.usuario
    elif rol == 'vendedor' and user.id_usuario == id_usuario:
        return vendedor.usuario
    else:
        raise HTTPException(status_code=403, detail="No autorizado")
# --- CRUD SUPERADMIN ---
@router.get("/superadmins", response_model=list[UsuarioResponse])
def listar_superadmins(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.core.dependencies import get_user_role
    if get_user_role(user, db) != 'superadmin':
        raise HTTPException(status_code=403, detail="Solo superadmins pueden ver esta información")
    return [sa.usuario for sa in db.query(service.SuperAdmin).all()]

# --- CRUD ADMIN MICROEMPRESA ---
@router.get("/admins", response_model=list[UsuarioResponse])
def listar_admins(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.core.dependencies import get_user_role
    rol = get_user_role(user, db)
    if rol == 'superadmin':
        return [adm.usuario for adm in db.query(service.AdminMicroempresa).all()]
    elif rol == 'adminmicroempresa':
        id_micro = user.admin_microempresa.id_microempresa
        return [adm.usuario for adm in db.query(service.AdminMicroempresa).filter_by(id_microempresa=id_micro).all()]
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# --- CRUD VENDEDORES ---
@router.get("/vendedores", response_model=list[UsuarioResponse])
def listar_vendedores(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.core.dependencies import get_user_role
    rol = get_user_role(user, db)
    if rol == 'superadmin':
        return [v.usuario for v in db.query(service.Vendedor).all()]
    elif rol == 'adminmicroempresa':
        id_micro = user.admin_microempresa.id_microempresa
        return [v.usuario for v in db.query(service.Vendedor).filter_by(id_microempresa=id_micro).all()]
    elif rol == 'vendedor':
        return [user]
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

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