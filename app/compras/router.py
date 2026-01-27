from fastapi.responses import StreamingResponse
import io

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db
from app.compras import service, schemas
from app.core.dependencies import get_current_user

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
def crear_compra(data: schemas.CompraCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.crear_compra(db, data, id_microempresa=None, usuario_actual=user)

# 1️⃣3️⃣ Agregar detalle a compra
@router.post("/{id_compra}/detalles", response_model=schemas.DetalleCompraResponse)
def agregar_detalle_compra(id_compra: int = Path(...), data: schemas.DetalleCompraCreate = Body(...), db: Session = Depends(get_db)):
	return service.agregar_detalle_compra(db, id_compra, data, id_microempresa=None)

# 1️⃣4️⃣ Obtener compra completa
# 1️⃣4️⃣ Obtener compra completa
@router.get("/{id_compra}")
def obtener_compra_completa(id_compra: int, db: Session = Depends(get_db)):
	compra, detalles, pagos = service.obtener_compra_completa(db, id_compra)
	return {
		"compra": schemas.CompraResponse.model_validate(compra),
		"detalles": [schemas.DetalleCompraResponse.model_validate(d) for d in detalles],
		"pagos": [schemas.PagoCompraResponse.model_validate(p) for p in pagos]
	}

# PDF de factura de compra
@router.get("/{id_compra}/pdf")
def generar_pdf_compra(id_compra: int, db: Session = Depends(get_db)):

	from reportlab.lib.pagesizes import letter
	from reportlab.pdfgen import canvas
	from reportlab.lib.units import mm
	from reportlab.lib import colors
	import datetime

	compra, detalles, _ = service.obtener_compra_completa(db, id_compra)
	proveedor = compra.proveedor
	microempresa = compra.microempresa
	buffer = io.BytesIO()
	c = canvas.Canvas(buffer, pagesize=letter)
	width, height = letter

	# Encabezado profesional
	c.setFillColor(colors.HexColor('#003366'))
	c.rect(0, height-70, width, 70, fill=1, stroke=0)
	c.setFillColor(colors.white)
	c.setFont("Helvetica-Bold", 20)
	c.drawString(30, height - 40, f"{microempresa.nombre if microempresa else 'Microempresa'}")
	c.setFont("Helvetica-Bold", 14)
	c.drawString(30, height - 65, "Factura de Compra")
	c.setFont("Helvetica", 10)
	c.setFillColor(colors.white)
	c.drawString(400, height - 40, f"Fecha: {compra.fecha.strftime('%d/%m/%Y %H:%M')}")
	c.drawString(400, height - 55, f"N° Compra: {compra.id_compra}")
	c.setFillColor(colors.black)

	# Datos proveedor
	y = height - 90
	c.setFont("Helvetica-Bold", 11)
	c.drawString(30, y, "Proveedor:")
	c.setFont("Helvetica", 10)
	c.drawString(110, y, proveedor.nombre if proveedor else '-')
	y -= 15
	c.setFont("Helvetica-Bold", 11)
	c.drawString(30, y, "Contacto:")
	c.setFont("Helvetica", 10)
	c.drawString(110, y, proveedor.contacto if proveedor else '-')
	y -= 15
	c.setFont("Helvetica-Bold", 11)
	c.drawString(30, y, "Email:")
	c.setFont("Helvetica", 10)
	c.drawString(110, y, proveedor.email if proveedor else '-')

	# Tabla de productos con bordes
	y -= 30
	c.setFont("Helvetica-Bold", 11)
	c.setFillColor(colors.HexColor('#003366'))
	c.rect(30, y-5, width-60, 20, fill=1, stroke=0)
	c.setFillColor(colors.white)
	c.drawString(35, y, "Producto")
	c.drawString(220, y, "Cantidad")
	c.drawString(300, y, "Precio Unitario")
	c.drawString(420, y, "Subtotal")
	c.setFillColor(colors.black)
	c.setFont("Helvetica", 10)
	y -= 20
	for d in detalles:
		nombre = d.producto.nombre if hasattr(d.producto, 'nombre') else str(d.id_producto)
		c.rect(30, y-2, width-60, 18, fill=0, stroke=1)
		c.drawString(35, y, nombre)
		c.drawRightString(260, y, str(d.cantidad))
		c.drawRightString(370, y, f"{float(d.precio_unitario):.2f}")
		c.drawRightString(500, y, f"{float(d.subtotal):.2f}")
		y -= 18
		if y < 100:
			c.showPage()
			y = height - 100

	# Línea total
	c.setFont("Helvetica-Bold", 12)
	c.setFillColor(colors.HexColor('#003366'))
	c.line(300, y-5, 550, y-5)
	c.drawString(300, y-20, "TOTAL:")
	c.drawRightString(500, y-20, f"{float(compra.total):.2f}")
	c.setFillColor(colors.black)

	# Observaciones
	if compra.observacion:
		y -= 40
		c.setFont("Helvetica-Bold", 11)
		c.drawString(30, y, "Observaciones:")
		c.setFont("Helvetica", 10)
		c.drawString(130, y, compra.observacion)

	c.save()
	buffer.seek(0)
	return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=compra_{id_compra}.pdf"})

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

# Obtener solo los detalles de una compra por su id
@router.get("/{id_compra}/detalles", response_model=List[schemas.DetalleCompraResponse])
def obtener_detalles_compra(id_compra: int, db: Session = Depends(get_db)):
	detalles = db.query(service.models.DetalleCompra).filter_by(id_compra=id_compra).all()
	return detalles
