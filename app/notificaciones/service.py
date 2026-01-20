# service.py para notificaciones

from sqlalchemy.orm import Session
from . import models, schemas
from .websocket import notificar_usuario
import asyncio

def crear_notificacion(db: Session, notificacion: schemas.NotificacionCreate):
    db_notificacion = models.Notificacion(**notificacion.dict())
    db.add(db_notificacion)
    db.commit()
    db.refresh(db_notificacion)
    # Enviar notificación por WebSocket si el usuario está conectado
    mensaje = f"Nueva notificación: {db_notificacion.mensaje}"
    try:
        asyncio.create_task(notificar_usuario(db_notificacion.id_usuario, mensaje))
    except Exception:
        pass
    return db_notificacion

def actualizar_notificacion(db: Session, id_notificacion: int, notificacion: schemas.NotificacionUpdate):
    db_notificacion = db.query(models.Notificacion).filter(models.Notificacion.id_notificacion == id_notificacion).first()
    if not db_notificacion:
        return None
    for key, value in notificacion.dict(exclude_unset=True).items():
        setattr(db_notificacion, key, value)
    db.commit()
    db.refresh(db_notificacion)
    return db_notificacion

def marcar_leida(db: Session, id_notificacion: int):
    db_notificacion = db.query(models.Notificacion).filter(models.Notificacion.id_notificacion == id_notificacion).first()
    if db_notificacion:
        db_notificacion.leido = True
        db.commit()
    return db_notificacion

def listar_notificaciones(db: Session):
    return db.query(models.Notificacion).all()

def listar_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Notificacion).filter(models.Notificacion.id_microempresa == id_microempresa).all()

def listar_por_usuario(db: Session, id_usuario: int):
    return db.query(models.Notificacion).filter(models.Notificacion.id_usuario == id_usuario).all()

def listar_no_leidas_por_usuario(db: Session, id_usuario: int):
    return db.query(models.Notificacion).filter(models.Notificacion.id_usuario == id_usuario, models.Notificacion.leido == False).all()
