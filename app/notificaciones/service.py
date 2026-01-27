from app.core.email_utils import enviar_email
from app.users.models import Usuario
from app.microempresas.models import Microempresa
from sqlalchemy.exc import SQLAlchemyError
# ===================== SISTEMA CENTRAL DE EVENTOS Y NOTIFICACIONES =====================
def generar_evento(tipo_evento: str, mensaje: str, id_microempresa: int, referencia_id: int = None, db: Session = None):
    """
    Registra un evento, genera notificaciones y envía correos según preferencias de usuarios de la microempresa.
    - Valida existencia de microempresa
    - Valida no duplicar evento (por tipo, referencia y fecha reciente)
    - Crea notificaciones internas y por email según preferencias
    - Envía email usando Gmail SMTP si corresponde
    - Usa transacción DB
    """
    if db is None:
        raise Exception("Se requiere una sesión de base de datos (db)")
    # Validar microempresa
    micro = db.query(Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise Exception("Microempresa no encontrada")
    # Validar duplicidad de evento (ejemplo: no registrar dos veces el mismo evento para la misma referencia en 1 minuto)
    from datetime import datetime, timedelta
    hace_un_minuto = datetime.now() - timedelta(minutes=1)
    evento_existente = db.query(models.EventoSistema).filter_by(
        id_microempresa=id_microempresa,
        tipo_evento=tipo_evento,
        referencia_id=referencia_id
    ).filter(models.EventoSistema.fecha_evento > hace_un_minuto).first()
    if evento_existente:
        return None  # No duplicar evento reciente
    # Registrar evento
    evento = models.EventoSistema(
        id_microempresa=id_microempresa,
        tipo_evento=tipo_evento,
        referencia_id=referencia_id,
        descripcion=mensaje,
        fecha_evento=datetime.now()
    )
    try:
        db.add(evento)
        db.flush()  # Obtener id_evento
        # Buscar usuarios de la microempresa (admins y vendedores)
        from app.users.models import AdminMicroempresa, Vendedor
        admin_ids = db.query(AdminMicroempresa.id_usuario).filter_by(id_microempresa=id_microempresa).all()
        vendedor_ids = db.query(Vendedor.id_usuario).filter_by(id_microempresa=id_microempresa).all()
        ids = [id for (id,) in admin_ids + vendedor_ids]
        usuarios = db.query(Usuario).filter(Usuario.id_usuario.in_(ids)).all()
        for usuario in usuarios:
            if not usuario:
                continue
            # ARREGLO PARCIAL: Siempre crear notificación IN_APP para todos los usuarios
            crear_notificacion_usuario(
                db=db,
                id_microempresa=id_microempresa,
                id_usuario=usuario.id_usuario,
                tipo_evento=tipo_evento,
                canal="IN_APP",
                mensaje=mensaje
            )
        db.commit()
        return evento
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error al generar evento y notificaciones: {e}")


def crear_notificacion_usuario(db: Session, id_microempresa: int, id_usuario: int, tipo_evento: str, canal: str, mensaje: str):
    """
    Crea una notificación para un usuario si no existe una igual reciente.
    """
    from datetime import datetime, timedelta
    hace_un_minuto = datetime.now() - timedelta(minutes=1)
    existe = db.query(models.Notificacion).filter_by(
        id_microempresa=id_microempresa,
        id_usuario=id_usuario,
        tipo_evento=tipo_evento,
        canal=canal
    ).filter(models.Notificacion.fecha_creacion > hace_un_minuto).first()
    if existe:
        return None
    notif = models.Notificacion(
        id_microempresa=id_microempresa,
        id_usuario=id_usuario,
        tipo_evento=tipo_evento,
        canal=canal,
        mensaje=mensaje,
        leido=False,
        enviado=(canal == "EMAIL"),
        fecha_creacion=datetime.now()
    )
    db.add(notif)
    db.flush()
    # WebSocket: notificar en tiempo real si es IN_APP
    if canal == "IN_APP":
        try:
            from .websocket import notificar_usuario
            import asyncio
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
            if loop and loop.is_running():
                loop.create_task(notificar_usuario(id_usuario, mensaje))
            else:
                asyncio.run(notificar_usuario(id_usuario, mensaje))
        except Exception as e:
            print(f"[WebSocket] Error al notificar usuario {id_usuario}: {e}")
    return notif


def enviar_email_notificacion(db: Session, usuario, asunto: str, mensaje: str, id_evento: int):
    """
    Envía un correo de notificación y registra el log.
    """
    if not usuario.email:
        return False
    exito = enviar_email(usuario.email, asunto, mensaje)
    # Registrar log
    from .models import NotificacionEmailLog
    from datetime import datetime
    log = NotificacionEmailLog(
        id_notificacion=None,  # Puede asociarse si se requiere
        email_destino=usuario.email,
        estado="ENVIADO" if exito else "FALLIDO",
        fecha_envio=datetime.now()
    )
    db.add(log)
    db.flush()
    return exito
from sqlalchemy.orm import Session
from . import models, schemas
from .websocket import notificar_usuario
import asyncio
from datetime import datetime

def crear_notificacion(db: Session, notificacion: schemas.NotificacionCreate):
    import sys
    print(f"[Notificaciones] Creando notificación para usuario {notificacion.id_usuario} (microempresa {notificacion.id_microempresa}) tipo: {notificacion.tipo_evento} mensaje: {notificacion.mensaje}")
    # Convertimos el esquema a diccionario
    notificacion_data = notificacion.dict()
    # Creamos la instancia del modelo
    db_notificacion = models.Notificacion(**notificacion_data)
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


# ------------------- PREFERENCIAS DE NOTIFICACION -------------------
def crear_o_actualizar_preferencia(db: Session, pref: schemas.PreferenciaNotificacionCreate):
    # No duplicar preferencias por usuario + tipo_evento + canal
    existente = db.query(models.PreferenciaNotificacion).filter_by(
        id_usuario=pref.id_usuario,
        tipo_evento=pref.tipo_evento,
        canal=pref.canal
    ).first()
    if existente:
        existente.activo = pref.activo if pref.activo is not None else True
        db.commit()
        db.refresh(existente)
        return existente
    nueva = models.PreferenciaNotificacion(
        id_usuario=pref.id_usuario,
        tipo_evento=pref.tipo_evento,
        canal=pref.canal,
        activo=pref.activo if pref.activo is not None else True
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def listar_preferencias_usuario(db: Session, id_usuario: int):
    return db.query(models.PreferenciaNotificacion).filter_by(id_usuario=id_usuario).all()

def cambiar_estado_preferencia(db: Session, id_preferencia: int, estado: bool):
    pref = db.query(models.PreferenciaNotificacion).filter_by(id_preferencia=id_preferencia).first()
    if not pref:
        return None
    pref.activo = estado
    db.commit()
    db.refresh(pref)
    return pref

# ------------------- EVENTOS DEL SISTEMA -------------------
def registrar_evento(db: Session, evento: schemas.EventoSistemaCreate):
    db_evento = models.EventoSistema(
        id_microempresa=evento.id_microempresa,
        tipo_evento=evento.tipo_evento,
        referencia_id=evento.referencia_id,
        descripcion=evento.descripcion,
        fecha_evento=datetime.now()
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

def listar_eventos_microempresa(db: Session, id_microempresa: int):
    return db.query(models.EventoSistema).filter_by(id_microempresa=id_microempresa).order_by(models.EventoSistema.fecha_evento.desc()).all()

# ------------------- LOGICA DE NOTIFICACION AUTOMATICA -------------------
def generar_notificaciones_por_evento(db: Session, id_microempresa: int, tipo_evento: str, referencia_id: int, descripcion: str):
    # Registrar evento
    evento = registrar_evento(db, schemas.EventoSistemaCreate(
        id_microempresa=id_microempresa,
        tipo_evento=tipo_evento,
        referencia_id=referencia_id,
        descripcion=descripcion
    ))
    # Buscar preferencias activas de usuarios de la microempresa
    from app.users.models import Usuario
    usuarios = db.query(Usuario).filter_by(id_microempresa=id_microempresa).all()
    notificaciones_creadas = []
    for usuario in usuarios:
        prefs = db.query(models.PreferenciaNotificacion).filter_by(
            id_usuario=usuario.id_usuario,
            tipo_evento=tipo_evento,
            activo=True
        ).all()
        for pref in prefs:
            notif = models.Notificacion(
                id_microempresa=id_microempresa,
                id_usuario=usuario.id_usuario,
                tipo_evento=tipo_evento,
                canal=pref.canal,
                mensaje=descripcion,
                leido=False,
                enviado=False,
                fecha_creacion=datetime.now()
            )
            db.add(notif)
            notificaciones_creadas.append(notif)
    db.commit()
    return notificaciones_creadas

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