from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from app.database.base import Base

class Plan(Base):
    __tablename__ = "planes"
    id_plan = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    precio = Column(Float, nullable=False)
    limite_productos = Column(Integer, nullable=False)
    limite_admins = Column(Integer, nullable=False)
    limite_vendedores = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    descripcion = Column(Text, nullable=True)
