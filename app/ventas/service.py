from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import and_
from app.inventario.models import Stock
from app.inventario.service import ajuste_stock
from app.notificaciones.service import crear_notificacion
from app.notificaciones.schemas import NotificacionCreate
from app.productos.models import Producto
from app.clientes.models import Cliente

# --- CRUD BÁSICO ---

def crear_venta(db: Session, venta: schemas.VentaCreate):
    """Crea una venta genérica (sin lógica de stock automática)"""
    db_venta = models.Venta(
        id_microempresa=venta.id_microempresa,
        id_cliente=venta.id_cliente,
        total=venta.total,
        estado=venta.estado,
        tipo=venta.tipo,
        fecha=venta.fecha or datetime.now()
    )
    db.add(db_venta)
    db.commit()
    db.refresh(db_venta)
    # Crear detalles
    for det in venta.detalles:
        db_det = models.DetalleVenta(
            id_venta=db_venta.id_venta,
            id_producto=det.id_producto,
            cantidad=det.cantidad,
            precio_unitario=det.precio_unitario,
            subtotal=det.subtotal
        )
        db.add(db_det)
    # Crear pagos si existen
    if venta.pagos:
        for pag in venta.pagos:
            db_pag = models.PagoVenta(
                id_venta=db_venta.id_venta,
                metodo=pag.metodo,
                comprobante_url=pag.comprobante_url,
                estado=pag.estado,
                fecha=pag.fecha or datetime.now()
            )
            db.add(db_pag)
    db.commit()
    db.refresh(db_venta)
    return db_venta

def listar_ventas(db: Session):
    return db.query(models.Venta).all()

def obtener_venta(db: Session, id_venta: int):
    return db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()

def listar_ventas_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Venta).filter(models.Venta.id_microempresa == id_microempresa).all()

# --- PAGOS Y DETALLES ---

def crear_pago_venta(db: Session, pago: schemas.PagoVentaCreate, id_venta: int):
    db_pago = models.PagoVenta(
        id_venta=id_venta,
        metodo=pago.metodo,
        comprobante_url=pago.comprobante_url,
        estado=pago.estado,
        fecha=pago.fecha or datetime.now()
    )
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago

def listar_pagos_venta(db: Session, id_venta: int):
    return db.query(models.PagoVenta).filter(models.PagoVenta.id_venta == id_venta).all()

def listar_detalles_venta(db: Session, id_venta: int):
    return db.query(models.DetalleVenta).filter(models.DetalleVenta.id_venta == id_venta).all()

def listar_pagos_por_microempresa(db: Session, id_microempresa: int):
    return (
        db.query(models.PagoVenta)
        .join(models.Venta, models.PagoVenta.id_venta == models.Venta.id_venta)
        .filter(models.Venta.id_microempresa == id_microempresa)
        .all()
    )

def listar_detalles_por_microempresa(db: Session, id_microempresa: int):
    return (
        db.query(models.DetalleVenta)
        .join(models.Venta, models.DetalleVenta.id_venta == models.Venta.id_venta)
        .filter(models.Venta.id_microempresa == id_microempresa)
        .all()
    )

# --- LÓGICA DE NEGOCIO AVANZADA (Presencial vs Online) ---

def crear_venta_presencial(db: Session, id_microempresa: int, venta: schemas.VentaCreate):
    """Crea venta presencial, marca como PAGADA y descuenta stock inmediatamente"""
    # Calcular total automáticamente
    total = sum([d.cantidad * d.precio_unitario for d in venta.detalles])
    
    db_venta = models.Venta(
        id_microempresa=id_microempresa,
        id_cliente=venta.id_cliente,
        total=total,
        estado="PAGADA",
        tipo="PRESENCIAL",
        fecha=datetime.now()
    )
    db.add(db_venta)
    db.commit()
    db.refresh(db_venta)
    
    # Crear detalles y descontar stock
    for det in venta.detalles:
        db_det = models.DetalleVenta(
            id_venta=db_venta.id_venta,
            id_producto=det.id_producto,
            cantidad=det.cantidad,
            precio_unitario=det.precio_unitario,
            subtotal=det.cantidad * det.precio_unitario
        )
        db.add(db_det)
        
        # Descontar stock
        stock = db.query(Stock).filter(Stock.id_producto == det.id_producto).first()
        if not stock:
            raise HTTPException(status_code=400, detail=f"No existe stock para el producto {det.id_producto}")
        
        stock.cantidad -= det.cantidad
        stock.ultima_actualizacion = datetime.now()
        db.commit()
        
        # Notificación si stock bajo
        if stock.cantidad <= stock.stock_minimo:
            producto = db.query(Producto).filter(Producto.id_producto == det.id_producto).first()
            if producto:
                admins = db.execute("SELECT id_usuario FROM admin_microempresa WHERE id_microempresa = :idm", {"idm": id_microempresa}).fetchall()
                for admin in admins:
                    notif = NotificacionCreate(
                        id_microempresa=id_microempresa,
                        id_usuario=admin[0],
                        tipo="STOCK_BAJO",
                        mensaje=f"El producto '{producto.nombre}' está bajo el stock mínimo."
                    )
                    crear_notificacion(db, notif)
                
    db.commit()
    db.refresh(db_venta)
    return db_venta

def crear_venta_online(db: Session, venta: schemas.VentaCreate, cliente_data: dict):
    """
    Crea venta online:
    1. Busca o crea cliente (CORREGIDO: ASIGNA ID_MICROEMPRESA)
    2. Crea venta en estado PENDIENTE_PAGO.
    3. NO descuenta stock (se hace al validar el pago).
    """
    from datetime import datetime
    from app.clientes.models import Cliente
    
    # 1. Buscar o crear cliente
    telefono = cliente_data.get("telefono")
    
    # Intentamos buscar al cliente por teléfono
    db_cliente = db.query(Cliente).filter(Cliente.telefono == telefono).first()
    
    if not db_cliente:
        # CORRECCIÓN: Inyectamos el id_microempresa de la venta al cliente nuevo
        cliente_data["id_microempresa"] = venta.id_microempresa
        cliente_data["fecha_creacion"] = datetime.now()
        cliente_data["estado"] = True # Activo por defecto
        
        db_cliente = Cliente(**cliente_data)
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
    
    # 2. Calcular total automáticamente
    total_calculado = sum([d.cantidad * d.precio_unitario for d in venta.detalles])

    # 3. Crear Venta
    db_venta = models.Venta(
        id_microempresa=venta.id_microempresa,
        id_cliente=db_cliente.id_cliente,
        total=total_calculado, 
        estado="PENDIENTE_PAGO",
        tipo="ONLINE",
        fecha=datetime.now()
    )
    db.add(db_venta)
    db.commit()
    db.refresh(db_venta)

    # 4. Crear detalles
    for det in venta.detalles:
        db_det = models.DetalleVenta(
            id_venta=db_venta.id_venta,
            id_producto=det.id_producto,
            cantidad=det.cantidad,
            precio_unitario=det.precio_unitario,
            subtotal=det.cantidad * det.precio_unitario
        )
        db.add(db_det)
    
    db.commit()
    db.refresh(db_venta)
    return db_venta

def crear_pago_venta_pendiente(db: Session, id_venta: int, pago: schemas.PagoVentaCreate):
    from datetime import datetime
    db_pago = models.PagoVenta(
        id_venta=id_venta,
        metodo=pago.metodo,
        comprobante_url=pago.comprobante_url,
        estado="PENDIENTE",
        fecha=datetime.now()
    )
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago

def validar_pago_venta(db: Session, id_venta: int):
    """Valida el pago y DESCUENTA EL STOCK"""
    from datetime import datetime
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Cambiar estado de venta
    venta.estado = "PAGADA"

    # Validar pago asociado si existe
    pago = db.query(models.PagoVenta).filter(models.PagoVenta.id_venta == id_venta).order_by(models.PagoVenta.fecha.desc()).first()
    if pago:
        pago.estado = "VALIDADO"

    # Notificar a todos los admins de la microempresa sobre la validación del pago
    from sqlalchemy import text
    admins = db.execute(text("SELECT id_usuario FROM admin_microempresa WHERE id_microempresa = :idm"), {"idm": venta.id_microempresa}).fetchall()
    for admin in admins:
        notif = NotificacionCreate(
            id_microempresa=venta.id_microempresa,
            id_usuario=admin[0],
            tipo="PAGO_VALIDADO",
            mensaje=f"Se ha validado un pago para la venta #{venta.id_venta}."
        )
        crear_notificacion(db, notif)
    
    # Descontar stock
    detalles = db.query(models.DetalleVenta).filter(models.DetalleVenta.id_venta == id_venta).all()
    
    for det in detalles:
        stock = db.query(Stock).filter(Stock.id_producto == det.id_producto).first()
        if stock:
            stock.cantidad -= det.cantidad
            stock.ultima_actualizacion = datetime.now()
            
            # Alerta stock bajo
            if stock.cantidad <= stock.stock_minimo:
                producto = db.query(Producto).filter(Producto.id_producto == det.id_producto).first()
                if producto:
                    admins = db.execute("SELECT id_usuario FROM admin_microempresa WHERE id_microempresa = :idm", {"idm": venta.id_microempresa}).fetchall()
                    for admin in admins:
                        notif = NotificacionCreate(
                            id_microempresa=venta.id_microempresa,
                            id_usuario=admin[0],
                            tipo="STOCK_BAJO",
                            mensaje=f"El producto '{producto.nombre}' está bajo el stock mínimo."
                        )
                        crear_notificacion(db, notif)
        else:
             pass

    db.commit()
    db.refresh(venta)
    return venta

def rechazar_pago_venta(db: Session, id_venta: int):
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    venta.estado = "CANCELADA"
    db.commit()
    pago = db.query(models.PagoVenta).filter(models.PagoVenta.id_venta == id_venta).order_by(models.PagoVenta.fecha.desc()).first()
    if pago:
        pago.estado = "RECHAZADO"
        db.commit()
    return venta

def listar_ventas_filtrado(db: Session, id_microempresa: int, fecha_inicio=None, fecha_fin=None, estado=None, tipo=None):
    query = db.query(models.Venta).filter(models.Venta.id_microempresa == id_microempresa)
    if fecha_inicio:
        query = query.filter(models.Venta.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(models.Venta.fecha <= fecha_fin)
    if estado:
        query = query.filter(models.Venta.estado == estado)
    if tipo:
        query = query.filter(models.Venta.tipo == tipo)
    return query.all()