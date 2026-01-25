from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta

def crear_suscripcion(db: Session, data: schemas.SuscripcionCreate):
    # Validar datos no nulos
    if not data.id_microempresa or not data.id_plan:
        raise ValueError("id_microempresa y id_plan son obligatorios")

    # Validar existencia de microempresa y plan
    from app.microempresas.models import Microempresa
    from app.planes.models import Plan
    micro = db.query(Microempresa).filter_by(id_microempresa=data.id_microempresa).first()
    if not micro:
        raise LookupError("Microempresa no encontrada")
    plan = db.query(Plan).filter_by(id_plan=data.id_plan).first()
    if not plan:
        raise LookupError("Plan no encontrado")

    suscripcion = models.Suscripcion(
        id_microempresa=data.id_microempresa,
        id_plan=data.id_plan,
        fecha_fin=data.fecha_fin or (datetime.now() + timedelta(days=30)),
        estado=True
    )
    db.add(suscripcion)
    db.commit()
    db.refresh(suscripcion)
    # Evento: Nueva suscripción creada
    from app.notificaciones import service as notif_service
    notif_service.generar_evento(
        tipo_evento="PAGO_APROBADO",
        mensaje=f"Nueva suscripción creada para la microempresa {data.id_microempresa} (plan {data.id_plan}).",
        id_microempresa=data.id_microempresa,
        referencia_id=suscripcion.id_suscripcion,
        db=db
    )
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

def baja_logica_suscripcion(db: Session, id_suscripcion: int):
    suscripcion = db.query(models.Suscripcion).filter_by(id_suscripcion=id_suscripcion).first()
    if not suscripcion:
        return None
    suscripcion.estado = False
    db.commit()
    db.refresh(suscripcion)
    return suscripcion
