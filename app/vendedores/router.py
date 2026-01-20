
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.users.models import Vendedor
from app.auth.base_user import Usuario
from app.users.schemas import UsuarioResponse
from app.core.dependencies import get_current_user, get_user_role
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/vendedores",
    tags=["Vendedores"]
)

class VendedorUpdate(BaseModel):
    nombre: str
    email: EmailStr


# Listar vendedores SOLO aquí
@router.get("/", response_model=list[UsuarioResponse])
def listar_vendedores(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    def build_response(v):
        usuario = v.usuario
        return {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "estado": usuario.estado,
            "rol": "vendedor",
            "id_microempresa": v.id_microempresa
        }
    if rol == 'superadmin':
        return [build_response(v) for v in db.query(Vendedor).all()]
    elif rol == 'adminmicroempresa':
        id_micro = user.admin_microempresa.id_microempresa
        return [build_response(v) for v in db.query(Vendedor).filter_by(id_microempresa=id_micro).all()]
    elif rol == 'vendedor':
        return [{
            "id_usuario": user.id_usuario,
            "nombre": user.nombre,
            "email": user.email,
            "estado": user.estado,
            "rol": "vendedor",
            "id_microempresa": user.vendedor.id_microempresa if hasattr(user, 'vendedor') and user.vendedor else None
        }]
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener_vendedor(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    vendedor = db.query(Vendedor).filter_by(id_usuario=id_usuario).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    usuario = vendedor.usuario
    response = {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "estado": usuario.estado,
        "rol": "vendedor",
        "id_microempresa": vendedor.id_microempresa
    }
    if rol == 'superadmin':
        return response
    elif rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == vendedor.id_microempresa:
        return response
    elif rol == 'vendedor' and user.id_usuario == id_usuario:
        return response
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.delete("/{id_usuario}")
def eliminar_vendedor(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    vendedor = db.query(Vendedor).filter_by(id_usuario=id_usuario).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    if rol == 'superadmin' or (rol == 'vendedor' and user.id_usuario == id_usuario):
        db.delete(vendedor)
        db.commit()
        return {"detail": "Vendedor eliminado"}
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.put("/{id_usuario}", response_model=UsuarioResponse)
def actualizar_vendedor(id_usuario: int, data: VendedorUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    vendedor = db.query(Vendedor).filter_by(id_usuario=id_usuario).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    # Validar email único
    existe = db.query(Usuario).filter(Usuario.email == data.email, Usuario.id_usuario != id_usuario).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    if rol == 'superadmin' or (rol == 'vendedor' and user.id_usuario == id_usuario):
        usuario = vendedor.usuario
        usuario.nombre = data.nombre
        usuario.email = data.email
        db.commit()
        db.refresh(usuario)
        return usuario
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.put("/{id_usuario}/baja-logica", response_model=dict)
def baja_logica_vendedor(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    vendedor = db.query(Vendedor).filter_by(id_usuario=id_usuario).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    usuario = vendedor.usuario
    # Permitir solo a superadmin, admin de la microempresa o el propio vendedor
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == vendedor.id_microempresa) or (rol == 'vendedor' and user.id_usuario == id_usuario):
        usuario.estado = False
        db.commit()
        return {"detail": "Vendedor dado de baja lógicamente"}
    else:
        raise HTTPException(status_code=403, detail="No autorizado")