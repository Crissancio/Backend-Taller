from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/", response_model=schemas.VentaResponse)
def crear_venta(venta: schemas.VentaCreate, db: Session = Depends(get_db)):
    return service.crear_venta(db, venta)

@router.get("/", response_model=list[schemas.VentaResponse])
def listar_ventas(db: Session = Depends(get_db)):
    return service.listar_ventas(db)

@router.get("/{id_venta}", response_model=schemas.VentaResponse)
def obtener_venta(id_venta: int, db: Session = Depends(get_db)):
    venta = service.obtener_venta(db, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@router.post("/{id_venta}/pagos", response_model=schemas.PagoVentaResponse)
def crear_pago_venta(id_venta: int, pago: schemas.PagoVentaCreate, db: Session = Depends(get_db)):
    return service.crear_pago_venta(db, pago, id_venta)

@router.get("/{id_venta}/pagos", response_model=list[schemas.PagoVentaResponse])
def listar_pagos_venta(id_venta: int, db: Session = Depends(get_db)):
    return service.listar_pagos_venta(db, id_venta)

@router.get("/{id_venta}/detalles", response_model=list[schemas.DetalleVentaResponse])
def listar_detalles_venta(id_venta: int, db: Session = Depends(get_db)):
    return service.listar_detalles_venta(db, id_venta)

@router.get("/microempresa/{id_microempresa}", response_model=list[schemas.VentaResponse])
def listar_ventas_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_ventas_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/pagos", response_model=list[schemas.PagoVentaResponse])
def listar_pagos_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_pagos_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/detalles", response_model=list[schemas.DetalleVentaResponse])
def listar_detalles_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_detalles_por_microempresa(db, id_microempresa)

@router.post("/microempresas/{id_microempresa}/ventas", response_model=schemas.VentaResponse)
def crear_venta_presencial(id_microempresa: int, venta: schemas.VentaCreate, db: Session = Depends(get_db)):
    return service.crear_venta_presencial(db, id_microempresa, venta)

@router.post("/ventas/checkout", response_model=schemas.VentaResponse)
def crear_venta_online(venta: schemas.VentaCreate = Body(...), cliente: dict = Body(...), db: Session = Depends(get_db)):
    return service.crear_venta_online(db, venta, cliente)

@router.post("/ventas/{id_venta}/pago", response_model=schemas.PagoVentaResponse)
def crear_pago_venta_pendiente(id_venta: int, pago: schemas.PagoVentaCreate = Body(...), db: Session = Depends(get_db)):
    return service.crear_pago_venta_pendiente(db, id_venta, pago)

@router.put("/ventas/{id_venta}/pago/validar", response_model=schemas.VentaResponse)
def validar_pago_venta(id_venta: int, db: Session = Depends(get_db)):
    return service.validar_pago_venta(db, id_venta)

@router.put("/ventas/{id_venta}/pago/rechazar", response_model=schemas.VentaResponse)
def rechazar_pago_venta(id_venta: int, db: Session = Depends(get_db)):
    return service.rechazar_pago_venta(db, id_venta)

@router.get("/microempresas/{id_microempresa}/ventas", response_model=list[schemas.VentaResponse])
def listar_ventas_filtrado(
    id_microempresa: int,
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    estado: str = Query(None),
    tipo: str = Query(None),
    db: Session = Depends(get_db)
):
    return service.listar_ventas_filtrado(db, id_microempresa, fecha_inicio, fecha_fin, estado, tipo)
