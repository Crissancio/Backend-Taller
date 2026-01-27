from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

# --- FUNCIONES DE ESCRITURA (Crear/Editar/Eliminar) ---

def crear_categoria(db: Session, id_microempresa: int, categoria: schemas.CategoriaCreate):
    existe = db.query(models.Categoria).filter(
        models.Categoria.id_microempresa == id_microempresa,
        models.Categoria.nombre == categoria.nombre
    ).first()
    if existe:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre en la microempresa.")
    db_categoria = models.Categoria(
        id_microempresa=id_microempresa,
        nombre=categoria.nombre,
        descripcion=categoria.descripcion,
        activo=True,
        fecha_creacion=datetime.now()
    )
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

def eliminar_categoria(db: Session, id_categoria: int):
    from app.notificaciones import service as notif_service
    from app.notificaciones.schemas import NotificacionCreate
    from app.users.models import AdminMicroempresa
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id_categoria == id_categoria).first()
    if db_categoria:
        id_microempresa = db_categoria.id_microempresa
        nombre_categoria = db_categoria.nombre
        db.delete(db_categoria)
        db.commit()
        # Notificar al admin de la microempresa
        admin = db.query(AdminMicroempresa).filter(AdminMicroempresa.id_microempresa == id_microempresa).first()
        if admin:
            notificacion = NotificacionCreate(
                id_microempresa=id_microempresa,
                id_usuario=admin.id_usuario,
                tipo_evento="categoria",
                canal="IN_APP",
                mensaje=f"La categoría '{nombre_categoria}' ha sido eliminada (baja física)."
            )
            notif_service.crear_notificacion(db, notificacion)
    return db_categoria

def crear_producto(db: Session, id_microempresa: int, producto: schemas.ProductoCreate):
    # Validar que la categoría pertenezca a la microempresa
    categoria = db.query(models.Categoria).filter(
        models.Categoria.id_categoria == producto.id_categoria,
        models.Categoria.id_microempresa == id_microempresa
    ).first()
    if not categoria:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="La categoría no pertenece a la microempresa.")
    
    # Crear producto
    data = producto.dict()
    data["id_microempresa"] = id_microempresa
    data["fecha_creacion"] = datetime.now()
    db_producto = models.Producto(**data)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    
    # Crear registro en stock con cantidad = 0
    from app.inventario.models import Stock
    from app.inventario.service import crear_stock_inicial
    crear_stock_inicial(db, db_producto.id_producto)
    # Evento: Producto creado
    from app.notificaciones import service as notif_service
    notif_service.generar_evento(
        tipo_evento="NUEVO_PRODUCTO",
        mensaje=f"Se ha creado el producto '{db_producto.nombre}' en la microempresa.",
        id_microempresa=id_microempresa,
        referencia_id=db_producto.id_producto,
        db=db
    )
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
        # Evento: Producto desactivado
        from app.notificaciones import service as notif_service
        notif_service.generar_evento(
            tipo_evento="PRODUCTO_DESACTIVADO",
            mensaje=f"El producto '{db_producto.nombre}' ha sido desactivado.",
            id_microempresa=db_producto.id_microempresa,
            referencia_id=db_producto.id_producto,
            db=db
        )
    return db_producto

def eliminar_producto_fisico(db: Session, id_producto: int):
    from app.notificaciones import service as notif_service
    from app.notificaciones.schemas import NotificacionCreate
    from app.users.models import AdminMicroempresa
    db_producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if db_producto:
        id_microempresa = db_producto.id_microempresa
        nombre_producto = db_producto.nombre
        db.delete(db_producto)
        db.commit()
        # Notificar al admin de la microempresa
        admin = db.query(AdminMicroempresa).filter(AdminMicroempresa.id_microempresa == id_microempresa).first()
        if admin:
            notificacion = NotificacionCreate(
                id_microempresa=id_microempresa,
                id_usuario=admin.id_usuario,
                tipo="producto",
                mensaje=f"El producto '{nombre_producto}' ha sido eliminado permanentemente."
            )
            notif_service.crear_notificacion(db, notificacion)
    return db_producto

def baja_logica_producto(db: Session, id_producto: int):
    db_producto = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if db_producto:
        db_producto.estado = False
        db.commit()
    return db_producto

# --- FUNCIONES DE LECTURA (CATEGORÍAS) ---

def listar_categorias(db: Session):
    return db.query(models.Categoria).all()

def listar_categorias_activas(db: Session, id_microempresa: int):
    return db.query(models.Categoria).filter(
        models.Categoria.id_microempresa == id_microempresa,
        models.Categoria.activo == True
    ).all()

def listar_todas_categorias_activas(db: Session):
    """(NUEVO) Devuelve todas las categorías activas sin filtrar por empresa (Global)"""
    return db.query(models.Categoria).filter(models.Categoria.activo == True).all()

def listar_categorias_inactivas(db: Session):
    return db.query(models.Categoria).filter(models.Categoria.activo == False).all()

# --- FUNCIONES DE LECTURA (PRODUCTOS) ---

def listar_productos(db: Session, id_microempresa: int, id_categoria: int = None, estado: bool = None):
    query = db.query(models.Producto).filter(models.Producto.id_microempresa == id_microempresa)
    if id_categoria is not None:
        query = query.filter(models.Producto.id_categoria == id_categoria)
    if estado is not None:
        query = query.filter(models.Producto.estado == estado)
    return query.all()

def listar_productos_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Producto).filter(models.Producto.id_microempresa == id_microempresa).all()

def filtrar_productos_por_microempresa_y_nombre(db: Session, id_microempresa: int, nombre: str):
    return db.query(models.Producto).filter(
        models.Producto.id_microempresa == id_microempresa,
        models.Producto.nombre.ilike(f"%{nombre}%")
    ).all()

# --- FUNCIONES DE PRODUCTOS CON STOCK (NUEVAS Y NECESARIAS PARA EVITAR ERRORES) ---

def listar_productos_con_stock_global(db: Session):
    """Devuelve productos de todo el sistema que tienen stock > 0"""
    from app.inventario.models import Stock
    return db.query(models.Producto).join(Stock, models.Producto.id_producto == Stock.id_producto).filter(Stock.cantidad > 0).all()

def listar_productos_sin_stock_global(db: Session):
    """Devuelve productos de todo el sistema que tienen stock = 0"""
    from app.inventario.models import Stock
    return db.query(models.Producto).join(Stock, models.Producto.id_producto == Stock.id_producto).filter(Stock.cantidad == 0).all()

def listar_productos_portal_publico(db: Session, id_microempresa: int):
    """Lógica del portal"""
    from app.inventario.models import Stock
    return (
        db.query(models.Producto)
        .join(Stock, models.Producto.id_producto == Stock.id_producto)
        .filter(
            models.Producto.id_microempresa == id_microempresa,
            models.Producto.estado == True,
            Stock.cantidad > 0 
        )
        .all()
    )

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


def listar_productos_activos_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Producto).filter(
        models.Producto.id_microempresa == id_microempresa,
        models.Producto.estado == True
    ).all()

# NUEVA FUNCIÓN: Listar productos inactivos por microempresa
def listar_productos_inactivos_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Producto).filter(
        models.Producto.id_microempresa == id_microempresa,
        models.Producto.estado == False
    ).all()


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