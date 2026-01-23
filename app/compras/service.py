
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException
from app.compras import models, schemas
from app.proveedores.models import Proveedor, ProveedorProducto, ProveedorMetodoPago
from app.productos.models import Producto
from app.inventario import service as inventario_service
from app.microempresas.models import Microempresa

# 1️⃣2️⃣ Crear compra
def crear_compra(db: Session, data: schemas.CompraCreate, id_microempresa: int = None):
	proveedor = db.query(Proveedor).filter_by(id_proveedor=data.id_proveedor, estado=True).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")
	# Determinar microempresa
	micro_id = id_microempresa if id_microempresa is not None else data.id_microempresa
	if not micro_id:
		raise HTTPException(status_code=400, detail="No se pudo determinar la microempresa")
	if proveedor.id_microempresa != micro_id:
		raise HTTPException(status_code=403, detail="El proveedor no pertenece a la microempresa")
	compra = models.Compra(
		id_microempresa=micro_id,
		id_proveedor=data.id_proveedor,
		total=0,
		estado="REGISTRADA",
		observacion=data.observacion
	)
	db.add(compra)
	db.commit()
	db.refresh(compra)
	return compra

# 1️⃣3️⃣ Agregar detalle a compra
def agregar_detalle_compra(db: Session, id_compra: int, data: schemas.DetalleCompraCreate, id_microempresa: int = None):
	compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
	if not compra or compra.estado != "REGISTRADA":
		raise HTTPException(status_code=400, detail="Compra no encontrada o no está en estado REGISTRADA")
	# Validar microempresa
	if id_microempresa and compra.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="La compra no pertenece a la microempresa")
	rel = db.query(ProveedorProducto).filter_by(id_proveedor=compra.id_proveedor, id_producto=data.id_producto, activo=True).first()
	if not rel:
		raise HTTPException(status_code=400, detail="El producto no es provisto por el proveedor")
	producto = db.query(Producto).filter_by(id_producto=data.id_producto).first()
	if not producto:
		raise HTTPException(status_code=404, detail="Producto no encontrado")
	if id_microempresa and producto.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="El producto no pertenece a la microempresa")
	subtotal = data.cantidad * data.precio_unitario
	detalle = models.DetalleCompra(
		id_compra=id_compra,
		id_producto=data.id_producto,
		cantidad=data.cantidad,
		precio_unitario=data.precio_unitario,
		subtotal=subtotal
	)
	db.add(detalle)
	db.commit()
	# Recalcular total
	total = db.query(func.sum(models.DetalleCompra.subtotal)).filter_by(id_compra=id_compra).scalar() or 0
	compra.total = total
	db.commit()
	db.refresh(detalle)
	return detalle

# 1️⃣4️⃣ Obtener compra completa
def obtener_compra_completa(db: Session, id_compra: int):
	compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
	if not compra:
		raise HTTPException(status_code=404, detail="Compra no encontrada")
	detalles = db.query(models.DetalleCompra).filter_by(id_compra=id_compra).all()
	pagos = db.query(models.PagoCompra).filter_by(id_compra=id_compra).all()
	return compra, detalles, pagos

# 1️⃣5️⃣ Confirmar compra
def confirmar_compra(db: Session, id_compra: int, id_microempresa: int = None):
	compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
	if not compra:
		raise HTTPException(status_code=404, detail="Compra no encontrada")
	if id_microempresa and compra.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="La compra no pertenece a la microempresa")
	detalles = db.query(models.DetalleCompra).filter_by(id_compra=id_compra).all()
	if not detalles:
		raise HTTPException(status_code=400, detail="La compra no tiene detalles")
	compra.estado = "CONFIRMADA"
	db.commit()
	db.refresh(compra)
	return compra

# 1️⃣6️⃣ Registrar pago
def registrar_pago(db: Session, id_compra: int, data: schemas.PagoCompraCreate, id_microempresa: int = None):
	compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
	if not compra:
		raise HTTPException(status_code=404, detail="Compra no encontrada")
	if compra.estado != "CONFIRMADA":
		raise HTTPException(status_code=400, detail="Solo se pueden registrar pagos para compras CONFIRMADAS")
	if id_microempresa and compra.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="La compra no pertenece a la microempresa")
	if data.id_metodo_pago:
		metodo = db.query(ProveedorMetodoPago).filter_by(id_metodo_pago=data.id_metodo_pago).first()
		if not metodo:
			raise HTTPException(status_code=404, detail="Método de pago no encontrado")
		proveedor = db.query(Proveedor).filter_by(id_proveedor=compra.id_proveedor).first()
		if not proveedor or metodo.id_proveedor != proveedor.id_proveedor:
			raise HTTPException(status_code=400, detail="El método de pago no pertenece al proveedor de la compra")
	pago = models.PagoCompra(
		id_compra=id_compra,
		id_metodo_pago=data.id_metodo_pago,
		monto=data.monto,
		comprobante_url=data.comprobante_url
	)
	db.add(pago)
	db.commit()
	db.refresh(pago)
	return pago

# 1️⃣7️⃣ Listar pagos
def listar_pagos(db: Session, id_compra: int):
	return db.query(models.PagoCompra).filter_by(id_compra=id_compra).all()

# 1️⃣8️⃣ Finalizar compra (actualiza stock)
def finalizar_compra(db: Session, id_compra: int, id_microempresa: int = None):
	from sqlalchemy.exc import SQLAlchemyError
	compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
	if not compra or compra.estado != "CONFIRMADA":
		raise HTTPException(status_code=400, detail="Compra no encontrada o no está CONFIRMADA")
	if id_microempresa and compra.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="La compra no pertenece a la microempresa")
	detalles = db.query(models.DetalleCompra).filter_by(id_compra=id_compra).all()
	if not detalles:
		raise HTTPException(status_code=400, detail="La compra no tiene detalles")
	try:
		compra.estado = "PAGADA"
		for detalle in detalles:
			inventario_service.ajuste_stock(db, detalle.id_producto, detalle.cantidad)
		db.commit()
		db.refresh(compra)
		return compra
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=500, detail="Error al finalizar la compra: " + str(e))
