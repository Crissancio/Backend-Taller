


from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service
from pydantic import ValidationError

router = APIRouter(
    prefix="/planes",
    tags=["Planes"]
)


# Ruta para crear un nuevo plan
@router.post("/", response_model=schemas.PlanResponse)
def crear_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    try:
        return service.crear_plan(db, plan)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/total/activos", response_model=dict)
def total_planes_activos(db: Session = Depends(get_db)):
    cantidad = db.query(service.models.Plan).filter_by(activo=True).count()
    return {"cantidad": cantidad}

@router.get("/activos", response_model=list[schemas.PlanResponse])
def listar_planes_activos(db: Session = Depends(get_db)):
    return db.query(service.models.Plan).filter_by(activo=True).all()

@router.get("/no-activos", response_model=list[schemas.PlanResponse])
def listar_planes_no_activos(db: Session = Depends(get_db)):
    return db.query(service.models.Plan).filter_by(activo=False).all()

@router.get("/{id_plan}", response_model=schemas.PlanResponse)
def obtener_plan(id_plan: int, db: Session = Depends(get_db)):
    plan = service.obtener_plan(db, id_plan)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan

@router.put("/{id_plan}", response_model=schemas.PlanResponse)
def actualizar_plan(id_plan: int, plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    try:
        actualizado = service.actualizar_plan(db, id_plan, plan)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        return actualizado
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id_plan}")
def eliminar_plan(id_plan: int, db: Session = Depends(get_db)):
    if not service.eliminar_plan(db, id_plan):
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return {"detail": "Plan eliminado"}


@router.get("/total/activos", response_model=dict)
def total_planes_activos(db: Session = Depends(get_db)):
    cantidad = db.query(service.models.Plan).filter_by(activo=True).count()
    return {"cantidad": cantidad}

@router.get("/activos", response_model=list[schemas.PlanResponse])
def listar_planes_activos(db: Session = Depends(get_db)):
    return db.query(service.models.Plan).filter_by(activo=True).all()

@router.get("/no-activos", response_model=list[schemas.PlanResponse])
def listar_planes_no_activos(db: Session = Depends(get_db)):
    return db.query(service.models.Plan).filter_by(activo=False).all()

# Activar un plan
@router.put("/{id_plan}/activar", response_model=schemas.PlanResponse)
def activar_plan(id_plan: int, db: Session = Depends(get_db)):
    plan = db.query(service.models.Plan).filter_by(id_plan=id_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    if plan.activo:
        raise HTTPException(status_code=400, detail="El plan ya está activo")
    plan.activo = True
    db.commit()
    db.refresh(plan)
    return plan

# Desactivar un plan
@router.put("/{id_plan}/desactivar", response_model=schemas.PlanResponse)
def desactivar_plan(id_plan: int, db: Session = Depends(get_db)):
    plan = db.query(service.models.Plan).filter_by(id_plan=id_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    if not plan.activo:
        raise HTTPException(status_code=400, detail="El plan ya está inactivo")
    plan.activo = False
    db.commit()
    db.refresh(plan)
    return plan

# Listar todos los planes (activos e inactivos)
@router.get("/", response_model=list[schemas.PlanResponse])
def listar_planes(db: Session = Depends(get_db)):
    return db.query(service.models.Plan).all()

