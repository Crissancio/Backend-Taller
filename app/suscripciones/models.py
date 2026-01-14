from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class Suscripcion(Base):
    __tablename__ = "suscripciones"
    id_suscripcion = Column(Integer, primary_key=True, index=True)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_fin = Column(DateTime(timezone=True))
    estado = Column(Boolean, default=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=False)
    id_plan = Column(Integer, ForeignKey("planes.id_plan"), nullable=False)
