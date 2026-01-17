from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, index=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(150), nullable=False)
    documento = Column(String(50))
    telefono = Column(String(30))
    email = Column(String(150))
    fecha_creacion = Column(TIMESTAMP, nullable=False)
    estado = Column(Boolean, default=True)

    microempresa = relationship("Microempresa", back_populates="clientes")
