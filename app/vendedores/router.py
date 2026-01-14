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

@router.get("/", response_model=list[UsuarioResponse])
def listar_vendedores(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    if rol == 'superadmin':
        return [v.usuario for v in db.query(Vendedor).all()]
    elif rol == 'adminmicroempresa':
        id_micro = user.admin_microempresa.id_microempresa
        return [v.usuario for v in db.query(Vendedor).filter_by(id_microempresa=id_micro).all()]
    elif rol == 'vendedor':
        return [user]
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener_vendedor(id_usuario: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    vendedor = db.query(Vendedor).filter_by(id_usuario=id_usuario).first()
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
