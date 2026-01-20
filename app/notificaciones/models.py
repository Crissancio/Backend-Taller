# models.py para notificaciones

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.base import Base

class Notificacion(Base):
    __tablename__ = "notificacion"
    id_notificacion = Column(Integer, primary_key=True, index=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    tipo = Column(String(50))
    mensaje = Column(Text, nullable=False)
    leido = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(TIMESTAMP, nullable=False)
