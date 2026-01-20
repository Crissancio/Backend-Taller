# models.py para inventario (stock)

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.base import Base

class Stock(Base):
    __tablename__ = "stock"
    id_stock = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto", ondelete="CASCADE"), nullable=False, unique=True)
    cantidad = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=0, nullable=False)
    ultima_actualizacion = Column(TIMESTAMP, nullable=False)
    producto = relationship("Producto")
