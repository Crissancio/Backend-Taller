from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.post("/", response_model=schemas.NotificacionResponse)
def crear_notificacion(notificacion: schemas.NotificacionCreate, db: Session = Depends(get_db)):
    return service.crear_notificacion(db, notificacion)

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
