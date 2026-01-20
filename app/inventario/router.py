from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter(prefix="/inventario", tags=["Inventario"])

@router.post("/", response_model=schemas.StockResponse)
def crear_stock(stock: schemas.StockCreate, db: Session = Depends(get_db)):
    return service.crear_stock(db, stock)

@router.put("/{id_stock}", response_model=schemas.StockResponse)
def actualizar_stock(id_stock: int, stock: schemas.StockUpdate, db: Session = Depends(get_db)):
    result = service.actualizar_stock(db, id_stock, stock)
    if not result:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
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
