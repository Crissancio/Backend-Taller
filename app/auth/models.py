# app/auth/models.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class SuperAdmin(Base):
    __tablename__ = "super_admin"
    id_superadmin = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    usuario = relationship("Usuario", backref="superadmin")  # SOLO relación, no import directo
