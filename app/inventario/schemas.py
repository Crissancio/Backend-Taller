# schemas.py para inventario (stock)

from pydantic import BaseModel, Field
from typing import Optional

class StockBase(BaseModel):
    id_producto: int
    cantidad: int = Field(0, ge=0)
    stock_minimo: int = Field(0, ge=0)

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    cantidad: Optional[int] = None
    stock_minimo: Optional[int] = None

from datetime import datetime

class StockResponse(StockBase):
    id_stock: int
    ultima_actualizacion: datetime
    class Config:
        from_attributes = True
