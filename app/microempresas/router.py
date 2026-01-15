from app.users.models import AdminMicroempresa, Vendedor
from app.users.schemas import UsuarioResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.microempresas import schemas, service
from app.core.dependencies import get_current_user, get_user_role

router = APIRouter(
    prefix="/microempresas",
    tags=["Microempresas"]
)


# ENDPOINT: Obtener administradores de una microempresa por id
@router.get("/{id_microempresa}/admins", response_model=list[UsuarioResponse])
def obtener_admins_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    admins = db.query(AdminMicroempresa).filter_by(id_microempresa=id_microempresa).all()
    return [
        {
            "id_usuario": adm.usuario.id_usuario,
            "nombre": adm.usuario.nombre,
            "email": adm.usuario.email,
            "estado": adm.usuario.estado,
            "rol": "adminmicroempresa",
            "id_microempresa": adm.id_microempresa
        }
        for adm in admins
    ]

# ENDPOINT: Obtener vendedores de una microempresa por id
@router.get("/{id_microempresa}/vendedores", response_model=list[UsuarioResponse])
def obtener_vendedores_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    vendedores = db.query(Vendedor).filter_by(id_microempresa=id_microempresa).all()
    return [
        {
            "id_usuario": v.usuario.id_usuario,
            "nombre": v.usuario.nombre,
            "email": v.usuario.email,
            "estado": v.usuario.estado,
            "rol": "vendedor",
            "id_microempresa": v.id_microempresa
        }
        for v in vendedores
    ]

# CREAR (acceso para todos los roles autenticados)
@router.post("/", response_model=schemas.MicroempresaResponse)
def crear_empresa(empresa: schemas.MicroempresaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return service.crear_microempresa(db, empresa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# LISTAR (superadmin ve todas, admin y vendedor solo la suya)
@router.get("/", response_model=list[schemas.MicroempresaResponse])
def listar_empresas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    query = db.query(service.models.Microempresa).filter_by(estado=True)
    if rol == 'superadmin':
        return query.all()
    elif rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa:
        micro = query.filter_by(id_microempresa=user.admin_microempresa.id_microempresa).first()
        return [micro] if micro else []
    elif rol == 'vendedor' and user.vendedor.id_microempresa:
        micro = query.filter_by(id_microempresa=user.vendedor.id_microempresa).first()
        return [micro] if micro else []
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# SUSCRIPCIÓN (solo superadmin o admin de esa microempresa)
@router.post("/{id_microempresa}/suscripcion", response_model=schemas.SuscripcionResponse)
    # This subscription route has been removed as there is a dedicated module for subscriptions.
# --- CRUD MICROEMPRESA (restricciones) ---
# OBTENER
@router.get("/{id_microempresa}", response_model=schemas.MicroempresaResponse)
def obtener_microempresa(id_microempresa: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    micro = db.query(service.models.Microempresa).filter_by(id_microempresa=id_microempresa, estado=True).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    if rol == 'superadmin':
        return micro
    elif rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == id_microempresa:
        return micro
    elif rol == 'vendedor' and user.vendedor.id_microempresa == id_microempresa:
        return micro
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# ACTUALIZAR (solo superadmin o admin de esa microempresa)
@router.put("/{id_microempresa}", response_model=schemas.MicroempresaResponse)
def actualizar_microempresa(id_microempresa: int, data: schemas.MicroempresaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == id_microempresa):
        micro = service.actualizar_microempresa(db, id_microempresa, data)
        if not micro:
            raise HTTPException(status_code=404, detail="Microempresa no encontrada")
        return micro
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# ELIMINAR (baja lógica, solo superadmin o admin de esa microempresa)
@router.delete("/{id_microempresa}")
def eliminar_microempresa(id_microempresa: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    micro = db.query(service.models.Microempresa).filter_by(id_microempresa=id_microempresa, estado=True).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and user.admin_microempresa.id_microempresa == id_microempresa):
        micro.estado = False
        db.commit()
        return {"detail": "Microempresa dada de baja lógicamente"}
    else:
        raise HTTPException(status_code=403, detail="No autorizado")