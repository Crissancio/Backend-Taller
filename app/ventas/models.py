from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, TIMESTAMP, DECIMAL
from sqlalchemy.orm import relationship
from app.database.base import Base

class Venta(Base):
    __tablename__ = "venta"
    id_venta = Column(Integer, primary_key=True, index=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=True)
    fecha = Column(TIMESTAMP)
    total = Column(Numeric(10,2), nullable=False)
    estado = Column(String(20), nullable=False)
    tipo = Column(String(20), nullable=False)

    detalles = relationship("DetalleVenta", back_populates="venta")
    pagos = relationship("PagoVenta", back_populates="venta")

class DetalleVenta(Base):
    __tablename__ = "detalle_venta"
    id_detalle = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10,2), nullable=False)
    subtotal = Column(Numeric(10,2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    # producto = relationship("Producto")  # Si necesitas relación directa

class PagoVenta(Base):
    __tablename__ = "pago_venta"
    id_pago = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    metodo = Column(String(30), nullable=False)
    comprobante_url = Column(Text)
    estado = Column(String(20), nullable=False)
    fecha = Column(TIMESTAMP)

    venta = relationship("Venta", back_populates="pagos")
