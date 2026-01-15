from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.microempresas import models
from app.planes.models import Plan

def crear_microempresa(db: Session, data: models.MicroempresaCreate):
    existe = db.query(models.Microempresa).filter(models.Microempresa.nit == data.nit).first()
    if existe:
        raise ValueError("Ya existe una empresa con ese NIT")
    
    nueva_empresa = models.Microempresa(
        nombre=data.nombre,
        nit=data.nit,
        direccion=data.direccion,
        telefono=data.telefono,
        moneda=data.moneda
    )
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa

def suscribir_empresa(db: Session, id_microempresa: int, id_plan: int):
    empresa = db.query(models.Microempresa).filter(models.Microempresa.id_microempresa == id_microempresa).first()
    if not empresa:
        raise ValueError("Microempresa no encontrada")

        plan = db.query(Plan).filter(Plan.id_plan == id_plan).first()
    if not plan:
        raise ValueError("Plan no encontrado")

    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=30)

    suscripcion = models.Suscripcion(
        id_microempresa=id_microempresa,
        id_plan=id_plan,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado=True
    )
    db.add(suscripcion)
    db.commit()
    db.refresh(suscripcion)

    return {
        "id_suscripcion": suscripcion.id_suscripcion,
        "id_microempresa": suscripcion.id_microempresa,
        "plan": plan.nombre,
        "fecha_inicio": suscripcion.fecha_inicio,
        "fecha_fin": suscripcion.fecha_fin,
        "estado": suscripcion.estado
    }


def obtener_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa).first()

def actualizar_microempresa(db: Session, id_microempresa: int, data):
    micro = db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(micro, field, value)
    db.commit()
    db.refresh(micro)
    return micro

def eliminar_microempresa(db: Session, id_microempresa: int):
    micro = db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa, estado=True).first()
    if not micro:
        return False
    micro.estado = False
    db.commit()
    return True