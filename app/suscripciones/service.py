from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta

def crear_suscripcion(db: Session, data: schemas.SuscripcionCreate):
    suscripcion = models.Suscripcion(
        id_microempresa=data.id_microempresa,
        id_plan=data.id_plan,
        fecha_fin=data.fecha_fin or (datetime.now() + timedelta(days=30)),
        estado=True
    )
    db.add(suscripcion)
    db.commit()
    db.refresh(suscripcion)
    return suscripcion

def listar_suscripciones(db: Session):
    return db.query(models.Suscripcion).all()

def obtener_suscripcion(db: Session, id_suscripcion: int):
    return db.query(models.Suscripcion).filter_by(id_suscripcion=id_suscripcion).first()

def actualizar_suscripcion(db: Session, id_suscripcion: int, data: schemas.SuscripcionCreate):
    suscripcion = db.query(models.Suscripcion).filter_by(id_suscripcion=id_suscripcion).first()
    if not suscripcion:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(suscripcion, field, value)
    db.commit()
    db.refresh(suscripcion)
    return suscripcion

def eliminar_suscripcion(db: Session, id_suscripcion: int):
    suscripcion = db.query(models.Suscripcion).filter_by(id_suscripcion=id_suscripcion).first()
    if not suscripcion:
        return False
    db.delete(suscripcion)
    db.commit()
    return True
