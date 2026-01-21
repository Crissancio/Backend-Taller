from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

# --- IMPORTS NUEVOS PARA LAS NOTIFICACIONES ---
from app.core.dependencies import get_current_user
from app.notificaciones import service as notif_service
from app.notificaciones.schemas import NotificacionCreate
from app.productos.models import Producto 

router = APIRouter(prefix="/inventario", tags=["Inventario"])

@router.post("/", response_model=schemas.StockResponse)
def crear_stock(
    stock: schemas.StockCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Agregamos el usuario para saber quién dispara la alerta
):
    # 1. Ejecutar la creación normal
    nuevo_stock = service.crear_stock(db, stock)
    
    # 2. VALIDACIÓN: Si la cantidad es 0, creamos la alerta
    if stock.cantidad <= 0:
        try:
            # Buscamos el nombre del producto para que la alerta sea clara
            producto = db.query(Producto).filter(Producto.id_producto == stock.id_producto).first()
            
            if producto:
                notif_data = NotificacionCreate(
                    id_microempresa=producto.id_microempresa,
                    id_usuario=current_user.id_usuario,
                    tipo="STOCK_BAJO",
                    mensaje=f"Alerta de Inventario: El producto '{producto.nombre}' se ha registrado sin stock (0 unidades)."
                )
                notif_service.crear_notificacion(db, notif_data)
        except Exception as e:
            print(f"Error creando notificación en inventario: {e}")

    return nuevo_stock

@router.put("/{id_stock}", response_model=schemas.StockResponse)
def actualizar_stock(
    id_stock: int, 
    stock: schemas.StockUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1. Actualización normal
    result = service.actualizar_stock(db, id_stock, stock)
    if not result:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    
    # 2. VALIDACIÓN: Si al editar ponen 0
    if stock.cantidad is not None and stock.cantidad <= 0:
        try:
            # result contiene el objeto Stock actualizado, usamos su id_producto
            producto = db.query(Producto).filter(Producto.id_producto == result.id_producto).first()
            
            if producto:
                notif_data = NotificacionCreate(
                    id_microempresa=producto.id_microempresa,
                    id_usuario=current_user.id_usuario,
                    tipo="STOCK_BAJO",
                    mensaje=f"Alerta: El producto '{producto.nombre}' se ha quedado sin stock."
                )
                notif_service.crear_notificacion(db, notif_data)
        except Exception as e:
            print(f"Error creando notificación en inventario: {e}")

    return result

@router.delete("/{id_stock}", response_model=schemas.StockResponse)
def baja_logica_stock(id_stock: int, db: Session = Depends(get_db)):
    result = service.baja_logica_stock(db, id_stock)
    if not result:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return result

@router.get("/", response_model=list[schemas.StockResponse])
def listar_stock(db: Session = Depends(get_db)):
    return service.listar_stock(db)

@router.get("/microempresa/{id_microempresa}", response_model=list[schemas.StockResponse])
def listar_stock_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_stock_por_microempresa(db, id_microempresa)

@router.get("/{id_stock}", response_model=schemas.StockResponse)
def obtener_stock(id_stock: int, db: Session = Depends(get_db)):
    stock = db.query(service.models.Stock).filter(service.models.Stock.id_stock == id_stock).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return stock

@router.get("/producto/{id_producto}", response_model=schemas.StockResponse)
def obtener_stock_por_producto(id_producto: int, db: Session = Depends(get_db)):
    stock = db.query(service.models.Stock).filter(service.models.Stock.id_producto == id_producto).order_by(service.models.Stock.ultima_actualizacion.desc()).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock no encontrado para el producto")
    return stock