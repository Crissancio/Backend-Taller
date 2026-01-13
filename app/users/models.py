from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.auth.base_user import Usuario  # IMPORTAR desde auth
from app.microempresas.models import Microempresa

class AdminMicroempresa(Base):
    __tablename__ = "admin_microempresa"

    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=True)  # Cambiado a nullable=True

    usuario = relationship("Usuario", back_populates="admin_microempresa")
    microempresa = relationship("Microempresa", back_populates="admins")

# =============================
# Vendedor
# =============================
class Vendedor(Base):
    __tablename__ = "vendedor"

    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=True)  # Ahora puede ser null

    # Relaciones
    usuario = relationship("Usuario", back_populates="vendedor")           # Debe existir en Usuario
    microempresa = relationship("Microempresa", back_populates="vendedores")  # Debe existir en Microempresa
