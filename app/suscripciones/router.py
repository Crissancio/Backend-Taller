from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter(
    prefix="/suscripciones",
    tags=["Suscripciones"]
)

@router.post("/", response_model=schemas.SuscripcionResponse)
def crear_suscripcion(suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db)):
    return service.crear_suscripcion(db, suscripcion)

@router.get("/", response_model=list[schemas.SuscripcionResponse])
def listar_suscripciones(db: Session = Depends(get_db)):
    return service.listar_suscripciones(db)

@router.get("/{id_suscripcion}", response_model=schemas.SuscripcionResponse)
def obtener_suscripcion(id_suscripcion: int, db: Session = Depends(get_db)):
    suscripcion = service.obtener_suscripcion(db, id_suscripcion)
    if not suscripcion:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return suscripcion

@router.put("/{id_suscripcion}", response_model=schemas.SuscripcionResponse)
def actualizar_suscripcion(id_suscripcion: int, suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db)):
    actualizado = service.actualizar_suscripcion(db, id_suscripcion, suscripcion)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return actualizado

@router.delete("/{id_suscripcion}")
def eliminar_suscripcion(id_suscripcion: int, db: Session = Depends(get_db)):
    if not service.eliminar_suscripcion(db, id_suscripcion):
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {"detail": "Suscripción eliminada"}
