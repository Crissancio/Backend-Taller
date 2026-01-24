from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.compras import models, schemas
from app.proveedores.models import Proveedor, ProveedorProducto, ProveedorMetodoPago
from app.productos.models import Producto
# Importamos el servicio de inventario (asegúrate de que la ruta sea correcta)
from app.inventario import service as inventario_service

# 1️⃣ Crear compra (Con actualización automática de Stock)
def crear_compra(db: Session, data: schemas.CompraCreate, id_microempresa: int = None):
    # 1. Validar Proveedor
    proveedor = db.query(Proveedor).filter_by(id_proveedor=data.id_proveedor, estado=True).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")

    # 2. Validar Microempresa
    micro_id = id_microempresa if id_microempresa is not None else data.id_microempresa
    if not micro_id:
        raise HTTPException(status_code=400, detail="No se pudo determinar la microempresa")
    
    if proveedor.id_microempresa != micro_id:
        raise HTTPException(status_code=403, detail="El proveedor no pertenece a la microempresa")

    # 3. Crear Cabecera de Compra
    # Creamos la compra directamente como CONFIRMADA para afectar stock inmediatamente
    compra = models.Compra(
        id_microempresa=micro_id,
        id_proveedor=data.id_proveedor,
        total=0, 
        estado="CONFIRMADA", 
        observacion=data.observacion
    )
    db.add(compra)
    db.flush() # Obtenemos el ID de la compra

    # 4. Procesar Detalles y ACTUALIZAR STOCK
    total_acumulado = 0
    
    if data.detalles:
        for item in data.detalles:
            # Validar producto
            producto = db.query(Producto).filter_by(id_producto=item.id_producto).first()
            if not producto:
                continue 

            # Validar pertenencia del producto
            if producto.id_microempresa != micro_id:
                continue

            subtotal = item.cantidad * item.precio_unitario
            
            detalle = models.DetalleCompra(
                id_compra=compra.id_compra,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                subtotal=subtotal
            )
            db.add(detalle)
            total_acumulado += subtotal
            
            # --- 🟢 ACTUALIZACIÓN DE STOCK (Lógica Robusta) ---
            try:
                # Opción A: Usar servicio de inventario si existe
                if hasattr(inventario_service, 'aumentar_stock'):
                    inventario_service.aumentar_stock(db, item.id_producto, item.cantidad)
                elif hasattr(inventario_service, 'ajuste_stock'):
                    inventario_service.ajuste_stock(db, item.id_producto, item.cantidad)
                
                # Opción B (Fallback): Actualizar modelo directamente
                else:
                    if producto.stock is None:
                        producto.stock = 0
                    producto.stock += item.cantidad
                    db.add(producto) # Marcamos para guardar
                    
            except Exception as e:
                print(f"Advertencia: Error al actualizar stock para producto {item.id_producto}: {str(e)}")
            # ----------------------------------------------------

    # 5. Guardar Cambios Finales
    compra.total = total_acumulado
    db.commit()
    db.refresh(compra)
    return compra

# 2️⃣ Agregar detalle a compra (También actualiza stock)
def agregar_detalle_compra(db: Session, id_compra: int, data: schemas.DetalleCompraCreate, id_microempresa: int = None):
    compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    if id_microempresa and compra.id_microempresa != id_microempresa:
        raise HTTPException(status_code=403, detail="La compra no pertenece a la microempresa")
    
    subtotal = data.cantidad * data.precio_unitario
    detalle = models.DetalleCompra(
        id_compra=id_compra,
        id_producto=data.id_producto,
        cantidad=data.cantidad,
        precio_unitario=data.precio_unitario,
        subtotal=subtotal
    )
    db.add(detalle)
    
    # 🟢 Actualizar Stock (Manual directo para asegurar)
    producto = db.query(Producto).filter_by(id_producto=data.id_producto).first()
    if producto:
        producto.stock = (producto.stock or 0) + data.cantidad
        db.add(producto)

    db.commit()
    
    # Recalcular total de la compra
    total = db.query(func.sum(models.DetalleCompra.subtotal)).filter_by(id_compra=id_compra).scalar() or 0
    compra.total = total
    db.commit()
    db.refresh(detalle)
    return detalle

# 3️⃣ Obtener compra completa
def obtener_compra_completa(db: Session, id_compra: int):
    compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    detalles = db.query(models.DetalleCompra).filter_by(id_compra=id_compra).all()
    pagos = db.query(models.PagoCompra).filter_by(id_compra=id_compra).all()
    return compra, detalles, pagos

# 4️⃣ Confirmar compra
def confirmar_compra(db: Session, id_compra: int, id_microempresa: int = None):
    compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    if id_microempresa and compra.id_microempresa != id_microempresa:
        raise HTTPException(status_code=403, detail="La compra no pertenece a la microempresa")
    
    # Si la compra estaba en borrador y pasa a confirmada, aquí se debería sumar stock si no se hizo antes.
    # Como en este flujo sumamos al crear, solo cambiamos estado si fuese necesario.
    compra.estado = "CONFIRMADA"
    db.commit()
    db.refresh(compra)
    return compra

# 5️⃣ Registrar pago
def registrar_pago(db: Session, id_compra: int, data: schemas.PagoCompraCreate, id_microempresa: int = None):
    compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
        
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

# 6️⃣ Listar pagos
def listar_pagos(db: Session, id_compra: int):
    return db.query(models.PagoCompra).filter_by(id_compra=id_compra).all()

# 7️⃣ Listar compras
def listar_compras(db: Session, id_microempresa: int):
    # Retorna las compras de la microempresa ordenadas por fecha (más reciente primero)
    return db.query(models.Compra)\
             .filter_by(id_microempresa=id_microempresa)\
             .order_by(models.Compra.fecha.desc())\
             .all()

# 8️⃣ Finalizar compra (Opcional, si usas flujo de 2 pasos)
def finalizar_compra(db: Session, id_compra: int, id_microempresa: int = None):
    compra = db.query(models.Compra).filter_by(id_compra=id_compra).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
        
    # Lógica adicional si se requiere marcar como "PAGADA" u otro estado final
    compra.estado = "FINALIZADA"
    db.commit()
    db.refresh(compra)
    return compra