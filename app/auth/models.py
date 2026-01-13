# app/auth/models.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class SuperAdmin(Base):
    __tablename__ = "super_admin"
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    usuario = relationship("Usuario", back_populates="super_admin")
