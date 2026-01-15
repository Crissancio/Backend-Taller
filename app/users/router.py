from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.dependencies import get_current_user, get_user_role
from . import schemas, service

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)



# Ruta /usuarios/me para obtener el usuario actual con rol
from app.core.dependencies import get_user_role

@router.get("/me", response_model=schemas.UsuarioResponse)
def get_me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rol = get_user_role(user, db)
    # Construir la respuesta incluyendo el rol
    return {
        "id_usuario": user.id_usuario,
        "nombre": user.nombre,
        "email": user.email,
        "estado": user.estado,
        "rol": rol or "usuario"
    }

# CRUD BÁSICO DE USUARIOS

# Registro de usuario base SOLO aquí

@router.post("/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    try:
        nuevo_usuario = service.crear_usuario(db, usuario)
        # Construir la respuesta agregando el rol por defecto
        return {
            "id_usuario": nuevo_usuario.id_usuario,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "estado": nuevo_usuario.estado,
            "rol": "usuario"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = service.listar_usuarios(db)
    usuarios_con_rol = []
    for user in usuarios:
        rol = get_user_role(user, db)
        usuarios_con_rol.append({
            "id_usuario": user.id_usuario,
            "nombre": user.nombre,
            "email": user.email,
            "estado": user.estado,
            "rol": rol or "usuario"
        })
    return usuarios_con_rol


@router.get("/{id_usuario}", response_model=schemas.UsuarioResponse)
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = service.obtener_usuario(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    rol = get_user_role(usuario, db)
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "estado": usuario.estado,
        "rol": rol or "usuario"
    }


@router.put("/{id_usuario}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(id_usuario: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    actualizado = service.actualizar_usuario(db, id_usuario, usuario)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    rol = get_user_role(actualizado, db)
    return {
        "id_usuario": actualizado.id_usuario,
        "nombre": actualizado.nombre,
        "email": actualizado.email,
        "estado": actualizado.estado,
        "rol": rol or "usuario"
    }

@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    if not service.eliminar_usuario(db, id_usuario):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"detail": "Usuario eliminado"}
