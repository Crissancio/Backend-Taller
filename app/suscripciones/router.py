from app.planes import schemas as plan_schemas
from app.planes.models import Plan
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter(
    prefix="/suscripciones",
    tags=["Suscripciones"]
)

# ENDPOINT: Obtener el plan al que está suscrita una microempresa (por id_microempresa)
@router.get("/microempresa/{id_microempresa}/plan", response_model=plan_schemas.PlanResponse)
def obtener_plan_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    """Devuelve el plan de la suscripción activa más reciente de la microempresa."""
    from .models import Suscripcion
    suscripcion = (
        db.query(Suscripcion)
        .filter_by(id_microempresa=id_microempresa, estado=True)
        .order_by(Suscripcion.fecha_inicio.desc())
        .first()
    )
    if not suscripcion:
        raise HTTPException(status_code=404, detail="No hay suscripción activa para esta microempresa")
    plan = db.query(Plan).filter_by(id_plan=suscripcion.id_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan

# ENDPOINT: Obtener la suscripción más reciente de una microempresa (por id_microempresa)
@router.get("/microempresa/{id_microempresa}/ultima", response_model=schemas.SuscripcionResponse)
def obtener_ultima_suscripcion_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    """Devuelve la suscripción más reciente (por fecha_inicio) de la microempresa."""
    from .models import Suscripcion
    suscripcion = (
        db.query(Suscripcion)
        .filter_by(id_microempresa=id_microempresa)
        .order_by(Suscripcion.fecha_inicio.desc())
        .first()
    )
    if not suscripcion:
        raise HTTPException(status_code=404, detail="No hay suscripciones para esta microempresa")
    return suscripcion



@router.post("/", response_model=schemas.SuscripcionResponse)
def crear_suscripcion(suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db)):
    try:
        return service.crear_suscripcion(db, suscripcion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[schemas.SuscripcionResponse])
def listar_suscripciones(db: Session = Depends(get_db)):
    return service.listar_suscripciones(db)

@router.get("/{id_suscripcion}", response_model=schemas.SuscripcionResponse)
def obtener_suscripcion(id_suscripcion: int, db: Session = Depends(get_db)):
    suscripcion = service.obtener_suscripcion(db, id_suscripcion)
    if not suscripcion:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return suscripcion

@router.put("/{id_suscripcion}", response_model=schemas.SuscripcionResponse)
def actualizar_suscripcion(id_suscripcion: int, suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db)):
    actualizado = service.actualizar_suscripcion(db, id_suscripcion, suscripcion)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return actualizado


# Baja física
@router.delete("/{id_suscripcion}")
def eliminar_suscripcion(id_suscripcion: int, db: Session = Depends(get_db)):
    if not service.eliminar_suscripcion(db, id_suscripcion):
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {"detail": "Suscripción eliminada físicamente"}

# Baja lógica
@router.put("/{id_suscripcion}/baja-logica", response_model=schemas.SuscripcionResponse)
def baja_logica_suscripcion(id_suscripcion: int, db: Session = Depends(get_db)):
    suscripcion = service.baja_logica_suscripcion(db, id_suscripcion)
    if not suscripcion:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return suscripcion
