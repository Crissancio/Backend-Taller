from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.dependencies import get_current_user
from . import schemas, service

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.get("/me", response_model=schemas.UsuarioResponse)
def get_me(user=Depends(get_current_user)):
    return user

# CRUD BÁSICO DE USUARIOS
@router.post("/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioBase, db: Session = Depends(get_db)):
    return service.crear_usuario(db, usuario)

@router.get("/", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return service.listar_usuarios(db)

@router.get("/{id_usuario}", response_model=schemas.UsuarioResponse)
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = service.obtener_usuario(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/{id_usuario}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(id_usuario: int, usuario: schemas.UsuarioBase, db: Session = Depends(get_db)):
    actualizado = service.actualizar_usuario(db, id_usuario, usuario)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return actualizado

@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    if not service.eliminar_usuario(db, id_usuario):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"detail": "Usuario eliminado"}
