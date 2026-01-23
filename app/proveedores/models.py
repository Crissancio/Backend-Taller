# models.py para el módulo de proveedores
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Proveedor(Base):
	__tablename__ = "proveedor"

	id_proveedor = Column(Integer, primary_key=True, index=True)
	id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa", ondelete="CASCADE"), nullable=False)
	nombre = Column(String(150), nullable=False)
	contacto = Column(String(150))
	email = Column(String(150))
	estado = Column(Boolean, default=True, nullable=False)
	fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	microempresa = relationship("Microempresa")
	metodos_pago = relationship("ProveedorMetodoPago", back_populates="proveedor", cascade="all, delete-orphan")
	productos = relationship("ProveedorProducto", back_populates="proveedor", cascade="all, delete-orphan")


class ProveedorMetodoPago(Base):
	__tablename__ = "proveedor_metodo_pago"

	id_metodo_pago = Column(Integer, primary_key=True, index=True)
	id_proveedor = Column(Integer, ForeignKey("proveedor.id_proveedor", ondelete="CASCADE"), nullable=False)
	tipo = Column(String(50), nullable=False)  # EJ: CUENTA_BANCARIA, QR, EFECTIVO, PASARELA
	descripcion = Column(Text)
	datos_pago = Column(Text)
	qr_imagen = Column(Text)
	activo = Column(Boolean, default=True, nullable=False)

	proveedor = relationship("Proveedor", back_populates="metodos_pago")


class ProveedorProducto(Base):
	__tablename__ = "proveedor_producto"

	id_proveedor = Column(Integer, ForeignKey("proveedor.id_proveedor", ondelete="CASCADE"), primary_key=True)
	id_producto = Column(Integer, ForeignKey("producto.id_producto", ondelete="CASCADE"), primary_key=True)
	precio_referencia = Column(Numeric(10,2))
	activo = Column(Boolean, default=True, nullable=False)

	proveedor = relationship("Proveedor", back_populates="productos")
	producto = relationship("Producto")
