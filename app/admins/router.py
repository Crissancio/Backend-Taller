from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.users.models import AdminMicroempresa
from app.auth.base_user import Usuario
from app.users.schemas import UsuarioResponse
from app.core.dependencies import get_current_user, get_user_role
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/admins",
    tags=["AdminsMicroempresa"]
)

class AdminUpdate(BaseModel):
    nombre: str
    email: EmailStr


# Listar admins SOLO aquí
@router.get("/", response_model=list[UsuarioResponse])
def listar_admins(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    def build_response(adm):
        usuario = adm.usuario
        return {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "estado": usuario.estado,
            "rol": "adminmicroempresa",
            "id_microempresa": adm.id_microempresa
        }
    if rol == 'superadmin':
        return [build_response(adm) for adm in db.query(AdminMicroempresa).all()]
    elif rol == 'adminmicroempresa':
        id_micro = user.admin_microempresa.id_microempresa
        return [build_response(adm) for adm in db.query(AdminMicroempresa).filter_by(id_microempresa=id_micro).all()]
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener_admin(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    admin = db.query(AdminMicroempresa).filter_by(id_usuario=id_usuario).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    usuario = admin.usuario
    response = {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "estado": usuario.estado,
        "rol": "adminmicroempresa",
        "id_microempresa": admin.id_microempresa
    }
    if rol == 'superadmin':
        return response
    elif rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == admin.id_microempresa:
        return response
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.delete("/{id_usuario}")
def eliminar_admin(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    admin = db.query(AdminMicroempresa).filter_by(id_usuario=id_usuario).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and user.id_usuario == id_usuario):
        db.delete(admin)
        db.commit()
        return {"detail": "Admin eliminado"}
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.put("/{id_usuario}", response_model=UsuarioResponse)
def actualizar_admin(id_usuario: int, data: AdminUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    admin = db.query(AdminMicroempresa).filter_by(id_usuario=id_usuario).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    # Validar email único
    existe = db.query(Usuario).filter(Usuario.email == data.email, Usuario.id_usuario != id_usuario).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and user.id_usuario == id_usuario):
        usuario = admin.usuario
        usuario.nombre = data.nombre
        usuario.email = data.email
        db.commit()
        db.refresh(usuario)
        return usuario
    else:
        raise HTTPException(status_code=403, detail="No autorizado")
