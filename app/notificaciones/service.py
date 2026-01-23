from sqlalchemy.orm import Session
from . import models, schemas
from .websocket import notificar_usuario
import asyncio
from datetime import datetime

def crear_notificacion(db: Session, notificacion: schemas.NotificacionCreate):
    import sys
    print(f"[Notificaciones] Creando notificación para usuario {notificacion.id_usuario} (microempresa {notificacion.id_microempresa}) tipo: {notificacion.tipo} mensaje: {notificacion.mensaje}")
    # Convertimos el esquema a diccionario
    notificacion_data = notificacion.dict()
    # Creamos la instancia del modelo
    db_notificacion = models.Notificacion(**notificacion_data)
    # 2. ASIGNAR LA FECHA DE CREACIÓN MANUALMENTE
    db_notificacion.fecha_creacion = datetime.now() 
    db.add(db_notificacion)
    db.commit()
    db.refresh(db_notificacion)
    print(f"[Notificaciones] Notificación creada con id {db_notificacion.id_notificacion}")
    # Enviar notificación por WebSocket si el usuario está conectado
    try:
        mensaje = f"Nueva notificación: {db_notificacion.mensaje}"
        print(f"[Notificaciones] Intentando enviar mensaje por WebSocket a usuario {db_notificacion.id_usuario}")
        try:
            import asyncio
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No hay loop corriendo
                pass
            if loop and loop.is_running():
                loop.create_task(notificar_usuario(db_notificacion.id_usuario, mensaje))
            else:
                asyncio.run(notificar_usuario(db_notificacion.id_usuario, mensaje))
        except Exception as e:
            print(f"[Notificaciones] Error al intentar enviar notificación por WebSocket: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[Notificaciones] Error general en notificación: {e}", file=sys.stderr)
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

def listar_notificaciones_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Notificacion).filter(
        models.Notificacion.id_microempresa == id_microempresa
    ).order_by(models.Notificacion.fecha_creacion.desc()).all()

def marcar_notificacion_leida(db: Session, id_notificacion: int):
    notificacion = db.query(models.Notificacion).filter(models.Notificacion.id_notificacion == id_notificacion).first()
    if not notificacion:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notificacion.leido = True
    db.commit()
    db.refresh(notificacion)
    return notificacion