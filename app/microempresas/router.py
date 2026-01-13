from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.microempresas import schemas, service

router = APIRouter(
    prefix="/microempresas",
    tags=["Microempresas"]
)

# CREAR
@router.post("/", response_model=schemas.MicroempresaResponse)
def crear_empresa(empresa: schemas.MicroempresaCreate, db: Session = Depends(get_db)):
    try:
        return service.crear_microempresa(db, empresa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# LISTAR
@router.get("/", response_model=list[schemas.MicroempresaResponse])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(service.models.Microempresa).all()

# SUSCRIPCIÓN
@router.post("/{id_microempresa}/suscripcion", response_model=schemas.SuscripcionResponse)
def suscribir(id_microempresa: int, suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db)):
    try:
        return service.suscribir_empresa(db, id_microempresa, suscripcion.id_plan)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
