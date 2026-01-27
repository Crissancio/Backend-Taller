from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


# --- RUBRO ---
class Rubro(Base):
    __tablename__ = "rubro"

    id_rubro = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True, index=True)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)

    # Relación uno a muchos con Microempresa
    microempresas = relationship("Microempresa", back_populates="rubro", cascade="all, delete-orphan")


# --- MICROEMPRESA ---
class Microempresa(Base):
    __tablename__ = "microempresas"

    id_microempresa = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    nit = Column(String(30), nullable=False, unique=True)
    correo_contacto = Column(String(150))
    direccion = Column(String(255))
    telefono = Column(String(30))
    tipo_atencion = Column(String(20), nullable=False)
    latitud = Column(Float(precision=7))
    longitud = Column(Float(precision=7))
    dias_atencion = Column(String(100))
    horario_atencion = Column(String(150))
    moneda = Column(String(10), nullable=False, default="BOB")
    logo = Column(String)
    id_rubro = Column(Integer, ForeignKey("rubro.id_rubro"), nullable=False)
    activo = Column(Boolean, nullable=False, default=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    rubro = relationship("Rubro", back_populates="microempresas")
    admins = relationship("AdminMicroempresa", back_populates="microempresa")
    vendedores = relationship("Vendedor", back_populates="microempresa")
    clientes = relationship("Cliente", back_populates="microempresa")
