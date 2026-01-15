def eliminar_usuario(db: Session, id_usuario: int):
    from app.auth.base_user import Usuario
    usuario = db.query(Usuario).filter_by(id_usuario=id_usuario).first()
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True
def obtener_usuario(db: Session, id_usuario: int):
    from app.auth.base_user import Usuario
    return db.query(Usuario).filter_by(id_usuario=id_usuario).first()
def actualizar_usuario(db: Session, id_usuario: int, usuario_data):
    from app.auth.base_user import Usuario
    usuario = db.query(Usuario).filter_by(id_usuario=id_usuario).first()
    if not usuario:
        return None
    if hasattr(usuario_data, 'nombre') and usuario_data.nombre is not None:
        usuario.nombre = usuario_data.nombre
    if hasattr(usuario_data, 'email') and usuario_data.email is not None:
        usuario.email = usuario_data.email
    if hasattr(usuario_data, 'estado') and usuario_data.estado is not None:
        usuario.estado = usuario_data.estado
    db.commit()
    db.refresh(usuario)
    return usuario
from app.core.security import hash_password
def crear_usuario(db: Session, usuario_data):
    from app.auth.base_user import Usuario
    # Verificar que el email no exista
    if db.query(Usuario).filter_by(email=usuario_data.email).first():
        raise ValueError("El email ya está registrado")
    nuevo_usuario = Usuario(
        nombre=usuario_data.nombre,
        email=usuario_data.email,
        password_hash=hash_password(usuario_data.password),
        estado=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
def listar_usuarios(db: Session):
    return db.query(Usuario).all()
from sqlalchemy.orm import Session
from app.users.models import Usuario

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()
