
from app.users.models import AdminMicroempresa, Vendedor
from app.users.schemas import UsuarioResponse
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.microempresas import schemas, service
from app.core.dependencies import get_current_user, get_user_role


router = APIRouter(
    prefix="/microempresas",
    tags=["Microempresas"]
)

# Importar después de definir router para evitar NameError
from app.users.models import AdminMicroempresa
from app.users.schemas import UsuarioResponse

# ==================== RUBROS ====================
@router.post("/rubros", response_model=schemas.RubroResponse)
def crear_rubro(rubro: schemas.RubroCreate, db: Session = Depends(get_db)):
    return service.crear_rubro(db, rubro)

@router.put("/rubros/{id_rubro}", response_model=schemas.RubroResponse)
def editar_rubro(id_rubro: int, rubro: schemas.RubroUpdate, db: Session = Depends(get_db)):
    return service.actualizar_rubro(db, id_rubro, rubro)

@router.get("/rubros", response_model=list[schemas.RubroResponse])
def listar_rubros(db: Session = Depends(get_db)):
    return service.listar_rubros(db)

@router.get("/rubros/activos", response_model=list[schemas.RubroResponse])
def listar_rubros_activos(db: Session = Depends(get_db)):
    return service.listar_rubros(db, solo_activos=True)

@router.patch("/rubros/{id_rubro}/estado", response_model=schemas.RubroResponse)
def cambiar_estado_rubro(id_rubro: int, activo: bool = Body(...), db: Session = Depends(get_db)):
    return service.cambiar_estado_rubro(db, id_rubro, activo)

# ==================== MICROEMPRESAS ====================
@router.post("/", response_model=schemas.MicroempresaResponse)
def crear_microempresa(empresa: schemas.MicroempresaCreate, db: Session = Depends(get_db)):
    return service.crear_microempresa(db, empresa)

@router.put("/{id_microempresa}", response_model=schemas.MicroempresaResponse)
def actualizar_microempresa(id_microempresa: int, empresa: schemas.MicroempresaUpdate, db: Session = Depends(get_db)):
    return service.actualizar_microempresa(db, id_microempresa, empresa)

@router.get("/", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas(db: Session = Depends(get_db)):
    return service.listar_microempresas(db)

@router.get("/{id_microempresa}", response_model=schemas.MicroempresaResponse)
def obtener_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.obtener_microempresa(db, id_microempresa)

@router.get("/rubro/{id_rubro}", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas_por_rubro(id_rubro: int, db: Session = Depends(get_db)):
    return service.listar_microempresas_por_rubro(db, id_rubro)

@router.get("/activas", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas_activas(db: Session = Depends(get_db)):
    return service.listar_microempresas(db, solo_activas=True)

@router.patch("/{id_microempresa}/activar", response_model=schemas.MicroempresaResponse)
def activar_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.activar_microempresa(db, id_microempresa)

@router.patch("/{id_microempresa}/desactivar", response_model=schemas.MicroempresaResponse)
def desactivar_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.desactivar_microempresa(db, id_microempresa)

@router.patch("/{id_microempresa}/logo", response_model=schemas.MicroempresaResponse)
def subir_logo_microempresa(id_microempresa: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return service.subir_logo_microempresa(db, id_microempresa, file)

@router.get("/total/activas", response_model=dict)
def total_microempresas_activas(db: Session = Depends(get_db)):
    cantidad = db.query(service.models.Microempresa).filter_by(estado=True).count()
    return {"cantidad": cantidad}

@router.get("/total/inactivas", response_model=dict)
def total_microempresas_inactivas(db: Session = Depends(get_db)):
    cantidad = db.query(service.models.Microempresa).filter_by(estado=False).count()
    return {"cantidad": cantidad}

# LISTAR (superadmin ve todas, admin y vendedor solo la suya)

# Obtener todas las microempresas (activas e inactivas)
@router.get("/", response_model=list[schemas.MicroempresaResponse])
def listar_empresas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    query = db.query(service.models.Microempresa)
    if rol == 'superadmin':
        return query.all()
    elif rol == 'adminmicroempresa' and hasattr(user, 'admin_microempresa') and user.admin_microempresa:
        micro = query.filter_by(id_microempresa=user.admin_microempresa.id_microempresa).first()
        return [micro] if micro else []
    elif rol == 'vendedor' and hasattr(user, 'vendedor') and user.vendedor:
        micro = query.filter_by(id_microempresa=user.vendedor.id_microempresa).first()
        return [micro] if micro else []
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# Obtener todas las microempresas ordenadas por nombre
@router.get("/orden/nombre", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas_por_nombre(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    query = db.query(service.models.Microempresa).order_by(service.models.Microempresa.nombre)
    if rol == 'superadmin':
        return query.all()
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# Obtener todas las microempresas ordenadas por NIT
@router.get("/orden/nit", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas_por_nit(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    query = db.query(service.models.Microempresa).order_by(service.models.Microempresa.nit)
    if rol == 'superadmin':
        return query.all()
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# Obtener todas las microempresas por plan (id_plan como parámetro de ruta)
@router.get("/por-plan/{id_plan}", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas_por_plan(id_plan: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.suscripciones.models import Suscripcion
    rol = get_user_role(user, db)
    # Buscar microempresas con suscripción activa al plan dado
    subquery = db.query(Suscripcion.id_microempresa).filter(Suscripcion.id_plan == id_plan, Suscripcion.estado == True).subquery()
    query = db.query(service.models.Microempresa).filter(service.models.Microempresa.id_microempresa.in_(subquery))
    if rol == 'superadmin':
        return query.all()
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# Obtener todas las microempresas activas
@router.get("/activas", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas_activas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    query = db.query(service.models.Microempresa).filter_by(estado=True)
    if rol == 'superadmin':
        return query.all()
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# Obtener todas las microempresas inactivas
@router.get("/inactivas", response_model=list[schemas.MicroempresaResponse])
def listar_microempresas_inactivas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    query = db.query(service.models.Microempresa).filter_by(estado=False)
    if rol == 'superadmin':
        return query.all()
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# --- CRUD MICROEMPRESA (restricciones) ---
# OBTENER

# Ruta pública: Obtener microempresa por id (sin restricciones de autenticación ni autorización)
@router.get("/{id_microempresa}", response_model=schemas.MicroempresaResponse)
def obtener_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    micro = db.query(service.models.Microempresa).filter_by(id_microempresa=id_microempresa, estado=True).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    return micro

# ACTUALIZAR (solo superadmin o admin de esa microempresa)
@router.put("/{id_microempresa}", response_model=schemas.MicroempresaResponse)
def actualizar_microempresa(id_microempresa: int, data: schemas.MicroempresaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and hasattr(user, 'admin_microempresa') and user.admin_microempresa and user.admin_microempresa.id_microempresa == id_microempresa):
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
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and hasattr(user, 'admin_microempresa') and user.admin_microempresa and user.admin_microempresa.id_microempresa == id_microempresa):
        micro.estado = False
        db.commit()
        return {"detail": "Microempresa dada de baja lógicamente"}
    else:
        raise HTTPException(status_code=403, detail="No autorizado")
    


@router.get("/total", response_model=dict)
def total_microempresas(db: Session = Depends(get_db)):
    cantidad = db.query(service.models.Microempresa).count()
    return {"cantidad": cantidad}


@router.get("/total/activas", response_model=dict)
def total_microempresas_activas(db: Session = Depends(get_db)):
    cantidad = db.query(service.models.Microempresa).filter_by(estado=True).count()
    return {"cantidad": cantidad}


@router.get("/total/inactivas", response_model=dict)
def total_microempresas_inactivas(db: Session = Depends(get_db)):
    cantidad = db.query(service.models.Microempresa).filter_by(estado=False).count()
    return {"cantidad": cantidad}


# ACTIVAR microempresa (solo superadmin o admin de esa microempresa)
@router.put("/{id_microempresa}/activar", response_model=dict)
def activar_microempresa(id_microempresa: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    micro = db.query(service.models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and hasattr(user, 'admin_microempresa') and user.admin_microempresa and user.admin_microempresa.id_microempresa == id_microempresa):
        if micro.estado:
            return {"detail": "La microempresa ya está activa"}
        micro.estado = True
        db.commit()
        return {"detail": "Microempresa activada correctamente"}
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

# DESACTIVAR microempresa (solo superadmin o admin de esa microempresa)
@router.put("/{id_microempresa}/desactivar", response_model=dict)
def desactivar_microempresa(id_microempresa: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    micro = db.query(service.models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    if rol == 'superadmin' or (rol == 'adminmicroempresa' and hasattr(user, 'admin_microempresa') and user.admin_microempresa and user.admin_microempresa.id_microempresa == id_microempresa):
        if not micro.estado:
            return {"detail": "La microempresa ya está inactiva"}
        micro.estado = False
        db.commit()
        return {"detail": "Microempresa desactivada correctamente"}
    else:
        raise HTTPException(status_code=403, detail="No autorizado")


# ==================== ADMINISTRADORES DE MICROEMPRESA ====================
@router.get("/{id_microempresa}/admins", response_model=list[UsuarioResponse])
def obtener_admins_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    admins = db.query(AdminMicroempresa).filter_by(id_microempresa=id_microempresa).all()
    result = []
    for a in admins:
        usuario = a.usuario
        # Construir el dict con todos los campos requeridos por UsuarioResponse
        result.append({
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "estado": usuario.estado,
            "rol": "admin_microempresa",
            "id_microempresa": id_microempresa
        })
    return result


# ==================== VENDEDORES DE MICROEMPRESA ====================
@router.get("/{id_microempresa}/vendedores", response_model=list[UsuarioResponse])
def obtener_vendedores_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    from app.users.models import Vendedor
    vendedores = db.query(Vendedor).filter_by(id_microempresa=id_microempresa).all()
    result = []
    for v in vendedores:
        usuario = v.usuario
        result.append({
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "estado": usuario.estado,
            "rol": "vendedor",
            "id_microempresa": id_microempresa
        })
    return result
