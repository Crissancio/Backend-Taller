# service.py para inventario (stock)

from sqlalchemy.orm import Session
from . import models, schemas
from app.productos.models import Producto

def crear_stock(db: Session, stock: schemas.StockCreate):
    from datetime import datetime
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
    for key, value in stock.dict(exclude_unset=True).items():
        setattr(db_stock, key, value)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def baja_logica_stock(db: Session, id_stock: int):
    db_stock = db.query(models.Stock).filter(models.Stock.id_stock == id_stock).first()
    if db_stock:
        db_stock.cantidad = 0
        db.commit()
    return db_stock

def listar_stock(db: Session):
    return db.query(models.Stock).all()

def listar_stock_por_microempresa(db: Session, id_microempresa: int):
    productos_ids = db.query(Producto.id_producto).filter(Producto.id_microempresa == id_microempresa).all()
    productos_ids = [pid[0] for pid in productos_ids]
    return db.query(models.Stock).filter(models.Stock.id_producto.in_(productos_ids)).all()
