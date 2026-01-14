from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class Microempresa(Base):
    __tablename__ = "microempresas"

    id_microempresa = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    nit = Column(String, nullable=False, unique=True)
    direccion = Column(String)
    telefono = Column(String)
    moneda = Column(String, default="BOB")
    impuestos = Column(Float, default=0.0)
    logo = Column(String)
    horario_atencion = Column(String)
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    admins = relationship("AdminMicroempresa", back_populates="microempresa")
    vendedores = relationship("Vendedor", back_populates="microempresa")
