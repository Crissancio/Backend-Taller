from sqlalchemy import Column, Integer, String, Float, Text
from app.database.base import Base

class Plan(Base):
    __tablename__ = "planes"
    id_plan = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    precio = Column(Float, nullable=False)
    limite_usuarios = Column(Integer, nullable=False)
    descripcion = Column(Text, nullable=True)
