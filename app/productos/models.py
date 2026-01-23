# models.py para productos y categorías

from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base

class Categoria(Base):
    __tablename__ = "categoria"
    __table_args__ = (
        UniqueConstraint('id_microempresa', 'nombre', name='uq_categoria_microempresa_nombre'),
    )
    id_categoria = Column(Integer, primary_key=True, index=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(TIMESTAMP, nullable=False)
    productos = relationship("Producto", back_populates="categoria")
    microempresa = relationship("Microempresa")

class Producto(Base):
    __tablename__ = "producto"
    id_producto = Column(Integer, primary_key=True, index=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa", ondelete="CASCADE"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    precio_venta = Column(Numeric(10,2), nullable=False)
    costo_compra = Column(Numeric(10,2))
    codigo = Column(String(50))
    imagen = Column(Text)
    estado = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(TIMESTAMP, nullable=False)
    categoria = relationship("Categoria", back_populates="productos")
