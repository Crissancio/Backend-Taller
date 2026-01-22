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

def crear_venta(db: Session, venta: schemas.VentaCreate):
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

def crear_pago_venta(db: Session, pago: schemas.PagoVentaCreate, id_venta: int):
    from datetime import datetime
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

def listar_ventas_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Venta).filter(models.Venta.id_microempresa == id_microempresa).all()

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

def crear_venta_presencial(db: Session, id_microempresa: int, venta: schemas.VentaCreate):
    from datetime import datetime
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
            notif = NotificacionCreate(
                id_microempresa=id_microempresa,
                id_usuario=1,  # Ajustar según lógica de usuario
                tipo="STOCK_BAJO",
                mensaje=f"El producto '{producto.nombre}' está bajo el stock mínimo."
            )
            crear_notificacion(db, notif)
    db.commit()
    db.refresh(db_venta)
    return db_venta

def crear_venta_online(db: Session, venta: schemas.VentaCreate, cliente_data: dict):
    from app.clientes.models import Cliente  # Importación local para evitar ciclos
    
    # 1. Extraer datos del diccionario de forma segura
    id_empresa = cliente_data.get("id_microempresa")
    doc_cliente = cliente_data.get("documento")
    
    # 2. BUSCAR SI EL CLIENTE YA EXISTE (Lógica inteligente)
    cliente_existente = db.query(Cliente).filter(
        Cliente.id_microempresa == id_empresa,
        Cliente.documento == doc_cliente
    ).first()

    if cliente_existente:
        # Si existe, actualizamos sus datos de contacto
        cliente_existente.telefono = cliente_data.get("telefono")
        cliente_existente.email = cliente_data.get("email")
        cliente_existente.nombre = cliente_data.get("nombre") # Actualizar nombre también por si acaso
        
        id_cliente_final = cliente_existente.id_cliente
    else:
        # Si no existe, lo creamos manualmente mapeando los campos
        nuevo_cliente = Cliente(
            id_microempresa=id_empresa,
            nombre=cliente_data.get("nombre"),
            documento=doc_cliente,
            telefono=cliente_data.get("telefono"),
            email=cliente_data.get("email"),
            fecha_creacion=cliente_data.get("fecha_creacion"),
            estado=True
        )
        db.add(nuevo_cliente)
        db.flush() # Para obtener el ID
        id_cliente_final = nuevo_cliente.id_cliente

    # 3. CREAR LA VENTA
    # Calcular total desde el backend para seguridad (opcional, pero recomendado)
    total_calculado = 0
    # Usamos venta.detalles porque 'venta' SÍ es un objeto Schema (no un dict)
    for d in venta.detalles:
        total_calculado += (d.cantidad * d.precio_unitario)

    db_venta = models.Venta(
        id_microempresa=id_empresa,
        id_cliente=id_cliente_final,
        total=total_calculado, # Usamos el calculado o venta.total
        estado="PENDIENTE_PAGO",
        tipo="ONLINE",
        fecha=datetime.now()
    )
    db.add(db_venta)
    db.flush()

    # 4. CREAR DETALLES
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
    from datetime import datetime
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    # Cambiar estado de venta y pago
    venta.estado = "PAGADA"
    db.commit()
    # Validar pago
    pago = db.query(models.PagoVenta).filter(models.PagoVenta.id_venta == id_venta).order_by(models.PagoVenta.fecha.desc()).first()
    if pago:
        pago.estado = "VALIDADO"
        db.commit()
    # Descontar stock y notificar si es necesario
    detalles = db.query(models.DetalleVenta).filter(models.DetalleVenta.id_venta == id_venta).all()
    for det in detalles:
        stock = db.query(Stock).filter(Stock.id_producto == det.id_producto).first()
        if not stock:
            raise HTTPException(status_code=400, detail=f"No existe stock para el producto {det.id_producto}")
        stock.cantidad -= det.cantidad
        stock.ultima_actualizacion = datetime.now()
        db.commit()
        if stock.cantidad <= stock.stock_minimo:
            producto = db.query(Producto).filter(Producto.id_producto == det.id_producto).first()
            notif = NotificacionCreate(
                id_microempresa=venta.id_microempresa,
                id_usuario=1,  # Ajustar según lógica de usuario
                tipo="STOCK_BAJO",
                mensaje=f"El producto '{producto.nombre}' está bajo el stock mínimo."
            )
            crear_notificacion(db, notif)
    db.commit()
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
