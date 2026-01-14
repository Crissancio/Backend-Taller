from sqlalchemy.orm import Session
from . import models, schemas

def crear_plan(db: Session, data: schemas.PlanCreate):
    plan = models.Plan(**data.dict())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def listar_planes(db: Session):
    return db.query(models.Plan).all()

def obtener_plan(db: Session, id_plan: int):
    return db.query(models.Plan).filter_by(id_plan=id_plan).first()

def actualizar_plan(db: Session, id_plan: int, data: schemas.PlanCreate):
    plan = db.query(models.Plan).filter_by(id_plan=id_plan).first()
    if not plan:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan

def eliminar_plan(db: Session, id_plan: int):
    plan = db.query(models.Plan).filter_by(id_plan=id_plan).first()
    if not plan:
        return False
    db.delete(plan)
    db.commit()
    return True
