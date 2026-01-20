from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.auth.base_user import Usuario
from app.auth.models import SuperAdmin
from app.users.models import Vendedor, AdminMicroempresa
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


def get_user_by_email(db: Session, email: str):
    """Busca un usuario por email en la tabla base de usuarios"""
    return db.query(Usuario).filter(Usuario.email == email).first()


def crear_vendedor(db: Session, data):
    """
    Crea un usuario base y un registro de Vendedor asociado a una microempresa
    """
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Crear usuario base
    usuario = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(usuario)
    db.flush()  # Necesario para obtener id_usuario sin hacer commit

    # Crear registro de vendedor
    vendedor = Vendedor(
        id_usuario=usuario.id_usuario,
        id_microempresa=data.id_microempresa
    )
    db.add(vendedor)
    db.commit()
    db.refresh(usuario)
    return usuario


def crear_admin_microempresa(db: Session, data):
    """
    Crea un usuario base y un registro de AdminMicroempresa asociado a una microempresa
    """
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    usuario = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(usuario)
    db.flush()

    admin = AdminMicroempresa(
        id_usuario=usuario.id_usuario,
        id_microempresa=data.id_microempresa if data.id_microempresa is not None else None
    )
    db.add(admin)
    db.commit()
    db.refresh(usuario)
    return usuario


# ---------- ASIGNAR MICROEMPRESA A ADMIN ----------
def asignar_microempresa_a_admin(db: Session, id_usuario: int, id_microempresa: int):
    """Asigna una microempresa a un admin existente"""
    # Validar que el usuario exista
    usuario = db.query(Usuario).filter_by(id_usuario=id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si ya es admin, actualiza la microempresa
    admin = db.query(AdminMicroempresa).filter_by(id_usuario=id_usuario).first()
    if admin:
        admin.id_microempresa = id_microempresa
        db.commit()
        db.refresh(admin)
        return admin
    # Si no es admin, lo crea
    nuevo_admin = AdminMicroempresa(
        id_usuario=id_usuario,
        id_microempresa=id_microempresa
    )
    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)
    return nuevo_admin


def crear_superadmin(db: Session, data):
    """
    Crea un usuario base y un registro de SuperAdmin (global)
    """
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    usuario = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    super_admin_obj = SuperAdmin(id_usuario=usuario.id_usuario)
    db.add(super_admin_obj)
    db.commit()
    db.refresh(super_admin_obj)

    return usuario


# ---------- LOGIN ----------
def login(db: Session, email: str, password: str):
    """Autentica al usuario y devuelve un token JWT"""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token(
        data={"sub": str(user.id_usuario)},
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return token



# ---------- RECUPERACIÓN DE CONTRASEÑA ----------
def generar_token_recuperacion(email: str):
    """Genera un token temporal para recuperación de contraseña (15 min)"""
    return create_access_token(data={"email": email}, expires_minutes=15)


# ---------- CREAR USUARIO BASE (sin rol) ----------
def crear_usuario_base(db: Session, data):
    """Crea solo un usuario base, sin rol asociado"""
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    usuario = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario