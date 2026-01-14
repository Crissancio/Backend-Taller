from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter(
    prefix="/planes",
    tags=["Planes"]
)

@router.post("/", response_model=schemas.PlanResponse)
def crear_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    return service.crear_plan(db, plan)

@router.get("/", response_model=list[schemas.PlanResponse])
def listar_planes(db: Session = Depends(get_db)):
    return service.listar_planes(db)

@router.get("/{id_plan}", response_model=schemas.PlanResponse)
def obtener_plan(id_plan: int, db: Session = Depends(get_db)):
    plan = service.obtener_plan(db, id_plan)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan

@router.put("/{id_plan}", response_model=schemas.PlanResponse)
def actualizar_plan(id_plan: int, plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    actualizado = service.actualizar_plan(db, id_plan, plan)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return actualizado

@router.delete("/{id_plan}")
def eliminar_plan(id_plan: int, db: Session = Depends(get_db)):
    if not service.eliminar_plan(db, id_plan):
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return {"detail": "Plan eliminado"}
