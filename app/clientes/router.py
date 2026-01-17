

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service
from app.core.dependencies import get_current_user, get_user_role

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.post("/", response_model=schemas.ClienteResponse)
def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    id_microempresa = cliente.id_microempresa
    
    if rol == "adminmicroempresa" and hasattr(user, "admin_microempresa") and user.admin_microempresa:
        id_microempresa = user.admin_microempresa.id_microempresa
    elif rol == "vendedor" and hasattr(user, "vendedor") and user.vendedor:
        id_microempresa = user.vendedor.id_microempresa
    cliente_data = schemas.ClienteCreate(
        nombre=cliente.nombre,
        documento=cliente.documento,
        telefono=cliente.telefono,
        email=cliente.email,
        id_microempresa=id_microempresa
    )
    return service.crear_cliente(db, cliente_data)

@router.get("/", response_model=list[schemas.ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return service.listar_clientes(db)

# Ruta para listar clientes activos (sin filtrar por microempresa)
@router.get("/activos", response_model=list[schemas.ClienteResponse])
def listar_clientes_activos(db: Session = Depends(get_db)):
    return service.listar_clientes_activos(db)

# Ruta para listar clientes inactivos (sin filtrar por microempresa)
@router.get("/inactivos", response_model=list[schemas.ClienteResponse])
def listar_clientes_inactivos(db: Session = Depends(get_db)):
    return service.listar_clientes_inactivos(db)

@router.get("/{id_cliente}", response_model=schemas.ClienteResponse)
def obtener_cliente(id_cliente: int, db: Session = Depends(get_db)):
    cliente = service.obtener_cliente(db, id_cliente)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.put("/{id_cliente}", response_model=schemas.ClienteResponse)
def actualizar_cliente(id_cliente: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    actualizado = service.actualizar_cliente(db, id_cliente, cliente)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return actualizado

@router.put("/{id_cliente}/baja-logica", response_model=schemas.ClienteResponse)
def baja_logica_cliente(id_cliente: int, db: Session = Depends(get_db)):
    cliente = service.baja_logica_cliente(db, id_cliente)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.delete("/{id_cliente}")
def eliminar_cliente(id_cliente: int, db: Session = Depends(get_db)):
    if not service.eliminar_cliente(db, id_cliente):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"detail": "Cliente eliminado"}


@router.get("/microempresa/{id_microempresa}", response_model=list[schemas.ClienteResponse])
def listar_clientes_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_clientes_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/activos", response_model=list[schemas.ClienteResponse])
def listar_clientes_activos_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_clientes_activos_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/inactivos", response_model=list[schemas.ClienteResponse])
def listar_clientes_inactivos_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_clientes_inactivos_por_microempresa(db, id_microempresa)

@router.put("/{id_cliente}/habilitar", response_model=schemas.ClienteResponse)
def habilitar_cliente(id_cliente: int, db: Session = Depends(get_db)):
    cliente = service.obtener_cliente(db, id_cliente)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.estado = True
    db.commit()
    db.refresh(cliente)
    return cliente