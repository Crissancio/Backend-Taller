# models.py para el módulo de compras
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Compra(Base):
	__tablename__ = "compra"

	id_compra = Column(Integer, primary_key=True, index=True)
	id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=False)
	id_proveedor = Column(Integer, ForeignKey("proveedor.id_proveedor"), nullable=False)
	fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	total = Column(Numeric(10,2), nullable=False)
	estado = Column(String(20), nullable=False, default="REGISTRADA")
	observacion = Column(Text)

	microempresa = relationship("Microempresa")
	proveedor = relationship("Proveedor")
	detalles = relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")
	pagos = relationship("PagoCompra", back_populates="compra", cascade="all, delete-orphan")


class DetalleCompra(Base):
	__tablename__ = "detalle_compra"

	id_detalle_compra = Column(Integer, primary_key=True, index=True)
	id_compra = Column(Integer, ForeignKey("compra.id_compra", ondelete="CASCADE"), nullable=False)
	id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
	cantidad = Column(Integer, nullable=False)
	precio_unitario = Column(Numeric(10,2), nullable=False)
	subtotal = Column(Numeric(10,2), nullable=False)

	compra = relationship("Compra", back_populates="detalles")
	producto = relationship("Producto")


class PagoCompra(Base):
	__tablename__ = "pago_compra"

	id_pago = Column(Integer, primary_key=True, index=True)
	id_compra = Column(Integer, ForeignKey("compra.id_compra", ondelete="CASCADE"), nullable=False)
	id_metodo_pago = Column(Integer, ForeignKey("proveedor_metodo_pago.id_metodo_pago"))
	monto = Column(Numeric(10,2), nullable=False)
	comprobante_url = Column(Text)
	fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	compra = relationship("Compra", back_populates="pagos")
	metodo_pago = relationship("ProveedorMetodoPago")
