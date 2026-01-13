from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from app.database.base import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    estado = Column(Boolean, default=True)

    # Relaciones
    admin_microempresa = relationship("AdminMicroempresa", back_populates="usuario", uselist=False)
    super_admin = relationship("SuperAdmin", back_populates="usuario", uselist=False)
    vendedor = relationship("Vendedor", back_populates="usuario", uselist=False)
