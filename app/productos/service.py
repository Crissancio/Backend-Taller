
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def crear_categoria(db: Session, categoria: schemas.CategoriaCreate):
    # Validar unicidad antes de crear
    existe = db.query(models.Categoria).filter(
        models.Categoria.id_microempresa == categoria.id_microempresa,
        models.Categoria.nombre == categoria.nombre
    ).first()
    if existe:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre para esta microempresa.")
    db_categoria = models.Categoria(**categoria.dict(), fecha_creacion=datetime.now())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def actualizar_categoria(db: Session, id_categoria: int, categoria: schemas.CategoriaUpdate):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id_categoria == id_categoria).first()
    if not db_categoria:
        return None
    for key, value in categoria.dict(exclude_unset=True).items():
        setattr(db_categoria, key, value)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def baja_logica_categoria(db: Session, id_categoria: int):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id_categoria == id_categoria).first()
    if db_categoria:
        db_categoria.activo = False
        db.commit()
    return db_categoria

def listar_categorias(db: Session):
    return db.query(models.Categoria).all()

def crear_producto(db: Session, producto: schemas.ProductoCreate):
    from datetime import datetime
    data = producto.dict()
    data["fecha_creacion"] = datetime.now()
    db_producto = models.Producto(**data)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def actualizar_producto(db: Session, id_producto: int, producto: schemas.ProductoUpdate):
    db_producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not db_producto:
        return None
    for key, value in producto.dict(exclude_unset=True).items():
        setattr(db_producto, key, value)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def baja_logica_producto(db: Session, id_producto: int):
    db_producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if db_producto:
        db_producto.estado = False
        db.commit()
    return db_producto

def listar_productos(db: Session):
    return db.query(models.Producto).all()

def listar_productos_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Producto).filter(models.Producto.id_microempresa == id_microempresa).all()

def listar_productos_activos_con_stock_por_microempresa(db: Session, id_microempresa: int):
    from app.inventario.models import Stock
    return (
        db.query(models.Producto)
        .join(Stock, models.Producto.id_producto == Stock.id_producto)
        .filter(models.Producto.id_microempresa == id_microempresa)
        .filter(models.Producto.estado == True)
        .filter(Stock.cantidad > 0)
        .all()
    )
# service.py para productos y categorías
def listar_productos_activos_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Producto).filter(
        models.Producto.id_microempresa == id_microempresa,
        models.Producto.estado == True
    ).all()

def listar_productos_inactivos_sin_stock_por_microempresa(db: Session, id_microempresa: int):
    from app.inventario.models import Stock
    return (
        db.query(models.Producto)
        .join(Stock, models.Producto.id_producto == Stock.id_producto)
        .filter(models.Producto.id_microempresa == id_microempresa)
        .filter(models.Producto.estado == False)
        .filter(Stock.cantidad == 0)
        .all()
    )
def filtrar_productos_por_microempresa_y_nombre(db: Session, id_microempresa: int, nombre: str):
    return db.query(models.Producto).filter(
        models.Producto.id_microempresa == id_microempresa,
        models.Producto.nombre.ilike(f"%{nombre}%")
    ).all()

def activar_producto(db: Session, id_producto: int):
    db_producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if db_producto:
        db_producto.estado = True
        db.commit()
        db.refresh(db_producto)
    return db_producto

def desactivar_producto(db: Session, id_producto: int):
    db_producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if db_producto:
        db_producto.estado = False
        db.commit()
        db.refresh(db_producto)
    return db_producto

def eliminar_producto_fisico(db: Session, id_producto: int):
    db_producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if db_producto:
        db.delete(db_producto)
        db.commit()
    return db_producto


def listar_categorias_activas(db: Session):
    return db.query(models.Categoria).filter(models.Categoria.activo == True).all()

def listar_categorias_inactivas(db: Session):
    return db.query(models.Categoria).filter(models.Categoria.activo == False).all()
def listar_productos_con_stock_por_microempresa(db: Session, id_microempresa: int):
    from app.inventario.models import Stock
    return (
        db.query(models.Producto)
        .join(Stock, models.Producto.id_producto == Stock.id_producto)
        .filter(models.Producto.id_microempresa == id_microempresa)
        .filter(Stock.cantidad > 0)
        .all()
    )
def buscar_productos_por_nombre_microempresa(db: Session, id_microempresa: int, nombre: str):
    return db.query(models.Producto).filter(
        models.Producto.id_microempresa == id_microempresa,
        models.Producto.nombre.ilike(f"%{nombre}%")
    ).all()

