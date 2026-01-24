
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db
from app.compras import service, schemas

router = APIRouter(prefix="/compras", tags=["Compras"])

from fastapi import Query # Asegúrate de importar Query

# 1️⃣9️⃣ Listar compras de una microempresa (ESTE FALTABA)
@router.get("", response_model=List[schemas.CompraResponse])
def listar_compras(id_microempresa: int = Query(None), db: Session = Depends(get_db)):
    if id_microempresa is None:
        raise HTTPException(status_code=400, detail="Debe especificar la microempresa")
    return service.listar_compras(db, id_microempresa)

# 1️⃣2️⃣ Crear compra
@router.post("", response_model=schemas.CompraResponse)
def crear_compra(data: schemas.CompraCreate, db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.crear_compra(db, data, id_microempresa=None)

# 1️⃣3️⃣ Agregar detalle a compra
@router.post("/{id_compra}/detalles", response_model=schemas.DetalleCompraResponse)
def agregar_detalle_compra(id_compra: int = Path(...), data: schemas.DetalleCompraCreate = Body(...), db: Session = Depends(get_db)):
	return service.agregar_detalle_compra(db, id_compra, data, id_microempresa=None)

# 1️⃣4️⃣ Obtener compra completa
@router.get("/{id_compra}")
def obtener_compra_completa(id_compra: int, db: Session = Depends(get_db)):
	compra, detalles, pagos = service.obtener_compra_completa(db, id_compra)
	return {
		"compra": schemas.CompraResponse.model_validate(compra),
		"detalles": [schemas.DetalleCompraResponse.model_validate(d) for d in detalles],
		"pagos": [schemas.PagoCompraResponse.model_validate(p) for p in pagos]
	}

# 1️⃣5️⃣ Confirmar compra
@router.post("/{id_compra}/confirmar", response_model=schemas.CompraResponse)
def confirmar_compra(id_compra: int = Path(...), db: Session = Depends(get_db)):
	return service.confirmar_compra(db, id_compra, id_microempresa=None)

# 1️⃣6️⃣ Registrar pago
@router.post("/{id_compra}/pagos", response_model=schemas.PagoCompraResponse)
def registrar_pago(id_compra: int = Path(...), data: schemas.PagoCompraCreate = Body(...), db: Session = Depends(get_db)):
	return service.registrar_pago(db, id_compra, data, id_microempresa=None)

# 1️⃣7️⃣ Listar pagos
@router.get("/{id_compra}/pagos", response_model=List[schemas.PagoCompraResponse])
def listar_pagos(id_compra: int, db: Session = Depends(get_db)):
	return service.listar_pagos(db, id_compra)

# 1️⃣8️⃣ Finalizar compra (actualiza stock)
@router.post("/{id_compra}/finalizar", response_model=schemas.CompraResponse)
def finalizar_compra(id_compra: int = Path(...), db: Session = Depends(get_db)):
	return service.finalizar_compra(db, id_compra, id_microempresa=None)
