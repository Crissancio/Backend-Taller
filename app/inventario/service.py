from sqlalchemy.orm import Session
from . import models, schemas
from app.productos.models import Producto
from datetime import datetime
from fastapi import HTTPException

# --- FUNCIÓN CORREGIDA ---
def crear_stock(db: Session, stock: schemas.StockCreate):
    # Validar que el producto exista y obtener su microempresa
    producto = db.query(Producto).filter(Producto.id_producto == stock.id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    existente = db.query(models.Stock).filter(models.Stock.id_producto == stock.id_producto).first()
    if existente:
        for key, value in stock.dict(exclude_unset=True).items():
            setattr(existente, key, value)
        existente.ultima_actualizacion = datetime.now()
        db.commit()
        db.refresh(existente)
        return existente
    data = stock.dict()
    data["ultima_actualizacion"] = datetime.now()
    db_stock = models.Stock(**data)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def actualizar_stock(db: Session, id_stock: int, stock: schemas.StockUpdate):
    db_stock = db.query(models.Stock).filter(models.Stock.id_stock == id_stock).first()
    if not db_stock:
        return None
    # Validar que el producto existe y obtener microempresa
    producto = db.query(Producto).filter(Producto.id_producto == db_stock.id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado para el stock")
    for key, value in stock.dict(exclude_unset=True).items():
        setattr(db_stock, key, value)
    if db_stock.cantidad is not None and db_stock.cantidad < 0:
        db_stock.cantidad = 0
    db.commit()
    db.refresh(db_stock)
    # Notificación si el stock está igual o por debajo del mínimo
    if db_stock.cantidad <= db_stock.stock_minimo:
        from app.notificaciones.service import crear_notificacion
        admins = db.execute("SELECT id_usuario FROM admin_microempresa WHERE id_microempresa = :idm", {"idm": producto.id_microempresa}).fetchall()
        for admin in admins:
            crear_notificacion(db, schemas.NotificacionCreate(
                id_microempresa=producto.id_microempresa,
                id_usuario=admin[0],
                tipo="stock_minimo",
                mensaje=f"El producto '{producto.nombre}' tiene stock igual o menor al mínimo definido ({db_stock.cantidad}/{db_stock.stock_minimo})"
            ))
    return db_stock

def baja_logica_stock(db: Session, id_stock: int):
    db_stock = db.query(models.Stock).filter(models.Stock.id_stock == id_stock).first()
    if not db_stock:
        return None
    # Validar que el producto existe y obtener microempresa
    producto = db.query(Producto).filter(Producto.id_producto == db_stock.id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado para el stock")
    db_stock.cantidad = 0
    db.commit()
    return db_stock

def listar_stock(db: Session):
    # No exponer todos los stocks sin filtro de microempresa
    raise HTTPException(status_code=403, detail="No permitido listar todo el stock globalmente")

def listar_stock_por_microempresa(db: Session, id_microempresa: int):
    productos_ids = db.query(Producto.id_producto).filter(Producto.id_microempresa == id_microempresa).all()
    productos_ids = [pid[0] for pid in productos_ids]
    return db.query(models.Stock).filter(models.Stock.id_producto.in_(productos_ids)).all()

def crear_stock_inicial(db: Session, id_producto: int):
    # Solo crear si no existe stock para ese producto
    producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    existe = db.query(models.Stock).filter(models.Stock.id_producto == id_producto).first()
    if existe:
        return existe
    db_stock = models.Stock(
        id_producto=id_producto,
        cantidad=0,
        stock_minimo=0,
        ultima_actualizacion=datetime.now()
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def registrar_stock_inicial(db: Session, id_producto: int, cantidad: int, stock_minimo: int = 0):
    producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    stock = db.query(models.Stock).filter(models.Stock.id_producto == id_producto).first()
    if stock and stock.cantidad > 0:
        raise HTTPException(status_code=400, detail="El stock ya tiene existencias. Use la función de ajuste o edición.")
    if not stock:
        stock = models.Stock(
            id_producto=id_producto,
            cantidad=cantidad,
            stock_minimo=stock_minimo,
            ultima_actualizacion=datetime.now()
        )
        db.add(stock)
    else:
        stock.cantidad = cantidad
        stock.stock_minimo = stock_minimo
        stock.ultima_actualizacion = datetime.now()
    db.commit()
    db.refresh(stock)
    return stock

def ajuste_stock(db: Session, id_producto: int, ajuste: int):
    stock = db.query(models.Stock).filter(models.Stock.id_producto == id_producto).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock no encontrado para el producto.")
    producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado para el stock")
    stock.cantidad += ajuste
    if stock.cantidad < 0:
        stock.cantidad = 0
    stock.ultima_actualizacion = datetime.now()
    db.commit()
    db.refresh(stock)
    if stock.cantidad <= stock.stock_minimo:
        from app.notificaciones.service import crear_notificacion
        admins = db.execute("SELECT id_usuario FROM admin_microempresa WHERE id_microempresa = :idm", {"idm": producto.id_microempresa}).fetchall()
        for admin in admins:
            crear_notificacion(db, schemas.NotificacionCreate(
                id_microempresa=producto.id_microempresa,
                id_usuario=admin[0],
                tipo="stock_minimo",
                mensaje=f"El producto '{producto.nombre}' tiene stock igual o menor al mínimo definido ({stock.cantidad}/{stock.stock_minimo})"
            ))
    return stock

def listar_stock_por_microempresa_con_alerta(db: Session, id_microempresa: int):
    productos_ids = db.query(Producto.id_producto).filter(Producto.id_microempresa == id_microempresa).all()
    productos_ids = [pid[0] for pid in productos_ids]
    stocks = db.query(models.Stock).filter(models.Stock.id_producto.in_(productos_ids)).all()
    resultado = []
    for s in stocks:
        bajo_minimo = s.cantidad <= s.stock_minimo
        resultado.append({
            **schemas.StockResponse.from_orm(s).dict(),
            "bajo_minimo": bajo_minimo
        })
    return resultado