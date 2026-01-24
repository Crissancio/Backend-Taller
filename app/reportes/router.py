from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.reportes import service

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/dashboard")
def obtener_dashboard(periodo: str = "mes", id_microempresa: int = None, db: Session = Depends(get_db)):
    # periodo puede ser: 'mes', 'trimestre', 'anio'
    return service.obtener_datos_dashboard(db, id_microempresa, periodo)