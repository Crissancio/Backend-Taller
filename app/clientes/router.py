

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
    # Asignar id_microempresa según el rol canónico
    if rol == "adminmicroempresa" and hasattr(user, "admin_microempresa") and user.admin_microempresa:
        id_microempresa = user.admin_microempresa.id_microempresa
    elif rol == "vendedor" and hasattr(user, "vendedor") and user.vendedor:
        id_microempresa = user.vendedor.id_microempresa
    elif rol == "superadmin":
        # superadmin puede crear clientes para cualquier microempresa
        pass
    elif rol == "usuario":
        raise HTTPException(status_code=403, detail="No autorizado para crear clientes")
    else:
        raise HTTPException(status_code=403, detail="Rol no autorizado para crear clientes")
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

# Endpoint SEGURO: Solo verifica si existe un cliente con ese documento
# NO expone datos sensibles (nombre, teléfono, email)
# Retorna: { existe: bool, id_cliente: int | null }
@router.get("/microempresa/{id_microempresa}/verificar-documento/{documento}")
def verificar_cliente_por_documento(id_microempresa: int, documento: str, db: Session = Depends(get_db)):
    cliente = service.buscar_cliente_por_documento(db, id_microempresa, documento)
    if cliente:
        return {"existe": True, "id_cliente": cliente.id_cliente}
    return {"existe": False, "id_cliente": None}

# Endpoint para obtener datos del cliente por ID (usado internamente después de verificar)
# Este endpoint requiere el ID específico, no expone búsqueda abierta
@router.get("/obtener/{id_cliente}", response_model=schemas.ClienteResponse)
def obtener_cliente_por_id(id_cliente: int, db: Session = Depends(get_db)):
    cliente = service.obtener_cliente(db, id_cliente)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente