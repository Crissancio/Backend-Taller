from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


# ------------------- NOTIFICACIONES -------------------
@router.post("/", response_model=schemas.NotificacionResponse)
def crear_notificacion(notificacion: schemas.NotificacionCreate, db: Session = Depends(get_db)):
    return service.crear_notificacion(db, notificacion)

@router.get("/", response_model=list[schemas.NotificacionResponse])
def listar_notificaciones(id_usuario: int = None, db: Session = Depends(get_db)):
    if id_usuario:
        return service.listar_por_usuario(db, id_usuario)
    return service.listar_notificaciones(db)

@router.patch("/{id}/leer", response_model=schemas.NotificacionResponse)
def marcar_leida(id: int, db: Session = Depends(get_db)):
    notif = service.marcar_leida(db, id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notif

@router.delete("/{id}")
def eliminar_notificacion(id: int, db: Session = Depends(get_db)):
    notif = db.query(service.models.Notificacion).filter_by(id_notificacion=id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.delete(notif)
    db.commit()
    return {"ok": True}

# ------------------- PREFERENCIAS -------------------
@router.post("/preferencias", response_model=schemas.PreferenciaNotificacionResponse)
def crear_o_actualizar_preferencia(preferencia: schemas.PreferenciaNotificacionCreate, db: Session = Depends(get_db)):
    return service.crear_o_actualizar_preferencia(db, preferencia)

@router.get("/preferencias/{id_usuario}", response_model=list[schemas.PreferenciaNotificacionResponse])
def listar_preferencias_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return service.listar_preferencias_usuario(db, id_usuario)

@router.patch("/preferencias/{id}/estado", response_model=schemas.PreferenciaNotificacionResponse)
def cambiar_estado_preferencia(id: int, estado: bool, db: Session = Depends(get_db)):
    pref = service.cambiar_estado_preferencia(db, id, estado)
    if not pref:
        raise HTTPException(status_code=404, detail="Preferencia no encontrada")
    return pref

# ------------------- EVENTOS -------------------
@router.get("/eventos", response_model=list[schemas.EventoSistemaResponse])
def listar_eventos(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_eventos_microempresa(db, id_microempresa)

@router.put("/{id_notificacion}", response_model=schemas.NotificacionResponse)
def actualizar_notificacion(id_notificacion: int, notificacion: schemas.NotificacionUpdate, db: Session = Depends(get_db)):
    result = service.actualizar_notificacion(db, id_notificacion, notificacion)
    if not result:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return result

@router.post("/{id_notificacion}/leida", response_model=schemas.NotificacionResponse)
def marcar_leida(id_notificacion: int, db: Session = Depends(get_db)):
    result = service.marcar_leida(db, id_notificacion)
    if not result:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return result

@router.get("/", response_model=list[schemas.NotificacionResponse])
def listar_notificaciones(db: Session = Depends(get_db)):
    return service.listar_notificaciones(db)

@router.get("/microempresa/{id_microempresa}", response_model=list[schemas.NotificacionResponse])
def listar_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_por_microempresa(db, id_microempresa)

@router.get("/usuario/{id_usuario}", response_model=list[schemas.NotificacionResponse])
def listar_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return service.listar_por_usuario(db, id_usuario)

@router.get("/usuario/{id_usuario}/no-leidas", response_model=list[schemas.NotificacionResponse])
def listar_no_leidas_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return service.listar_no_leidas_por_usuario(db, id_usuario)

@router.get("/{id_notificacion}", response_model=schemas.NotificacionResponse)
def obtener_notificacion(id_notificacion: int, db: Session = Depends(get_db)):
    notificacion = db.query(service.models.Notificacion).filter(service.models.Notificacion.id_notificacion == id_notificacion).first()
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notificacion

@router.get("/microempresas/{id_microempresa}/notificaciones", response_model=list[schemas.NotificacionResponse])
def listar_notificaciones_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_notificaciones_microempresa(db, id_microempresa)

@router.patch("/notificaciones/{id_notificacion}/leida", response_model=schemas.NotificacionResponse)
def marcar_notificacion_leida(id_notificacion: int, db: Session = Depends(get_db)):
    return service.marcar_notificacion_leida(db, id_notificacion)
