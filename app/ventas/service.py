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
from sqlalchemy import text

# --- CRUD BÁSICO ---

def crear_venta(db: Session, venta: schemas.VentaCreate):
    # Validar stock antes de registrar la venta
    from app.inventario.models import Stock
    errores_stock = []
    for det in venta.detalles:
        stock = db.query(Stock).filter(Stock.id_producto == det.id_producto).first()
        if not stock:
            errores_stock.append({
                "id_producto": det.id_producto,
                "error": "Producto no encontrado en inventario",
                "cantidad_solicitada": det.cantidad,
                "stock_disponible": 0
            })
        elif stock.cantidad < det.cantidad:
            errores_stock.append({
                "id_producto": det.id_producto,
                "error": "Stock insuficiente",
                "cantidad_solicitada": det.cantidad,
                "stock_disponible": stock.cantidad
            })
    if errores_stock:
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": "No se puede registrar la venta por problemas de stock.",
                "errores": errores_stock
            }
        )

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
    # Crear detalles (NO descontar stock aquí)
    for det in venta.detalles:
        db_det = models.DetalleVenta(
            id_venta=db_venta.id_venta,
            id_producto=det.id_producto,
            cantidad=det.cantidad,
            precio_unitario=det.precio_unitario,
            subtotal=det.subtotal
        )
        db.add(db_det)
    # Crear pagos 
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
    # Notificación y evento: Venta registrada
    from app.notificaciones import service as notif_service
    notif_service.generar_evento(
        tipo_evento="VENTA_REGISTRADA",
        mensaje=f"Se ha registrado una nueva venta (ID: {db_venta.id_venta}) por un total de {db_venta.total}.",
        id_microempresa=db_venta.id_microempresa,
        referencia_id=db_venta.id_venta,
        db=db
    )
    return db_venta

def listar_ventas(db: Session):
    return db.query(models.Venta).all()

def obtener_venta(db: Session, id_venta: int):
    return db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()

def listar_ventas_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Venta).filter(models.Venta.id_microempresa == id_microempresa).order_by(models.Venta.fecha.desc()).all()

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
    from app.notificaciones import service as notif_service
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
    # Evento de venta pagada
    notif_service.generar_evento(
        tipo_evento="VENTA_REALIZADA",
        mensaje=f"Venta presencial pagada (ID: {db_venta.id_venta}) por un total de {db_venta.total}.",
        id_microempresa=id_microempresa,
        referencia_id=db_venta.id_venta,
        db=db
    )
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

    # Validar stock antes de registrar la venta online
    from app.inventario.models import Stock
    errores_stock = []
    for det in venta.detalles:
        stock = db.query(Stock).filter(Stock.id_producto == det.id_producto).first()
        if not stock:
            errores_stock.append({
                "id_producto": det.id_producto,
                "error": "Producto no encontrado en inventario",
                "cantidad_solicitada": det.cantidad,
                "stock_disponible": 0
            })
        elif stock.cantidad < det.cantidad:
            errores_stock.append({
                "id_producto": det.id_producto,
                "error": "Stock insuficiente",
                "cantidad_solicitada": det.cantidad,
                "stock_disponible": stock.cantidad
            })
    if errores_stock:
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": "No se puede registrar la venta por problemas de stock.",
                "errores": errores_stock
            }
        )

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

    # 4. Crear detalles (NO descontar stock aquí)
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

    # Validar pago asociado 
    pago = db.query(models.PagoVenta).filter(models.PagoVenta.id_venta == id_venta).order_by(models.PagoVenta.fecha.desc()).first()
    if pago:
        pago.estado = "VALIDADO"

    # Evento de venta pagada
    from app.notificaciones import service as notif_service
    notif_service.generar_evento(
        tipo_evento="PAGO_VENTA_CONFIRMADO",
        mensaje=f"Se ha validado un pago para la venta #{venta.id_venta}.",
        id_microempresa=venta.id_microempresa,
        referencia_id=venta.id_venta,
        db=db
    )
    # Descontar stock
    detalles = db.query(models.DetalleVenta).filter(models.DetalleVenta.id_venta == id_venta).all()
    for det in detalles:
        stock = db.query(Stock).filter(Stock.id_producto == det.id_producto).first()
        if stock:
            stock.cantidad -= det.cantidad
            stock.ultima_actualizacion = datetime.now()
            producto = db.query(Producto).filter(Producto.id_producto == det.id_producto).first()
            if stock.cantidad == 0:
                notif_service.generar_evento(
                    tipo_evento="STOCK_AGOTADO",
                    mensaje=f"El producto '{producto.nombre}' se ha agotado (stock=0)",
                    id_microempresa=venta.id_microempresa,
                    referencia_id=producto.id_producto,
                    db=db
                )
            elif stock.cantidad <= stock.stock_minimo:
                notif_service.generar_evento(
                    tipo_evento="STOCK_BAJO",
                    mensaje=f"El producto '{producto.nombre}' está bajo el stock mínimo.",
                    id_microempresa=venta.id_microempresa,
                    referencia_id=producto.id_producto,
                    db=db
                )
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
    # Evento de venta cancelada
    from app.notificaciones import service as notif_service
    notif_service.generar_evento(
        tipo_evento="VENTA_CANCELADA",
        mensaje=f"La venta #{venta.id_venta} ha sido cancelada.",
        id_microempresa=venta.id_microempresa,
        referencia_id=venta.id_venta,
        db=db
    )
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