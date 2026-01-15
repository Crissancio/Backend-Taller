from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.models import SuperAdmin
from app.auth.base_user import Usuario
from app.users.schemas import UsuarioResponse
from app.core.dependencies import get_current_user, get_user_role
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/superadmins",
    tags=["SuperAdmins"]
)

class SuperAdminUpdate(BaseModel):
    nombre: str
    email: EmailStr


# Listar superadmins SOLO aquí
@router.get("/", response_model=list[UsuarioResponse])
def listar_superadmins(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if get_user_role(user, db) != 'superadmin':
        raise HTTPException(status_code=403, detail="Solo superadmins pueden ver esta información")
    return [sa.usuario for sa in db.query(SuperAdmin).all()]

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener_superadmin(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if get_user_role(user, db) != 'superadmin':
        raise HTTPException(status_code=403, detail="Solo superadmins pueden ver esta información")
    superadmin = db.query(SuperAdmin).filter_by(id_usuario=id_usuario).first()
    if not superadmin:
        raise HTTPException(status_code=404, detail="SuperAdmin no encontrado")
    return superadmin.usuario

@router.delete("/{id_usuario}")
def eliminar_superadmin(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if get_user_role(user, db) != 'superadmin':
        raise HTTPException(status_code=403, detail="Solo superadmins pueden eliminar superadmins")
    superadmin = db.query(SuperAdmin).filter_by(id_usuario=id_usuario).first()
    if not superadmin:
        raise HTTPException(status_code=404, detail="SuperAdmin no encontrado")
    db.delete(superadmin)
    db.commit()
    return {"detail": "SuperAdmin eliminado"}

@router.put("/{id_usuario}", response_model=UsuarioResponse)
def actualizar_superadmin(id_usuario: int, data: SuperAdminUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if get_user_role(user, db) != 'superadmin':
        raise HTTPException(status_code=403, detail="Solo superadmins pueden actualizar superadmins")
    superadmin = db.query(SuperAdmin).filter_by(id_usuario=id_usuario).first()
    if not superadmin:
        raise HTTPException(status_code=404, detail="SuperAdmin no encontrado")
    # Validar email único
    existe = db.query(Usuario).filter(Usuario.email == data.email, Usuario.id_usuario != id_usuario).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    usuario = superadmin.usuario
    usuario.nombre = data.nombre
    usuario.email = data.email
    db.commit()
    db.refresh(usuario)
    return usuario
