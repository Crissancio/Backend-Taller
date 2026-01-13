from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.microempresas import schemas, service
from app.core.dependencies import get_current_user, get_user_role

router = APIRouter(
    prefix="/microempresas",
    tags=["Microempresas"]
)

# CREAR
@router.post("/", response_model=schemas.MicroempresaResponse)
def crear_empresa(empresa: schemas.MicroempresaCreate, db: Session = Depends(get_db)):
    try:
        return service.crear_microempresa(db, empresa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# LISTAR
@router.get("/", response_model=list[schemas.MicroempresaResponse])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(service.models.Microempresa).all()

# SUSCRIPCIÓN
@router.post("/{id_microempresa}/suscripcion", response_model=schemas.SuscripcionResponse)
def suscribir(id_microempresa: int, suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db)):
    try:
        return service.suscribir_empresa(db, id_microempresa, suscripcion.id_plan)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
# --- CRUD MICROEMPRESA (restricciones) ---
@router.get("/{id_microempresa}", response_model=schemas.MicroempresaResponse)
def obtener_microempresa(id_microempresa: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rol = get_user_role(user, db)
    micro = db.query(service.models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
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