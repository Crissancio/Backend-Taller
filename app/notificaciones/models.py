# models.py para notificaciones

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.base import Base



# --- MODELO EXTENDIDO DE NOTIFICACION ---
class Notificacion(Base):
    __tablename__ = "notificacion"
    id_notificacion = Column(Integer, primary_key=True, index=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    tipo_evento = Column("tipo", String(50), nullable=False)  # Mapea a columna 'tipo'
    canal = Column(String(20), nullable=False)        # IN_APP, EMAIL, WHATSAPP
    mensaje = Column(Text, nullable=False)
    leido = Column(Boolean, default=False, nullable=False)
    enviado = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(TIMESTAMP, nullable=False)


# --- NUEVO: PreferenciaNotificacion ---
class PreferenciaNotificacion(Base):
    __tablename__ = "preferencia_notificacion"
    id_preferencia = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    canal = Column(String(20), nullable=False)  # IN_APP, EMAIL, WHATSAPP
    activo = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        # No duplicar preferencias por usuario + tipo_evento + canal
        {'sqlite_autoincrement': True},
    )


# --- NUEVO: EventoSistema ---
class EventoSistema(Base):
    __tablename__ = "evento_sistema"
    id_evento = Column(Integer, primary_key=True, index=True)
    id_microempresa = Column(Integer, ForeignKey("microempresas.id_microempresa"), nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    referencia_id = Column(Integer, nullable=True)  # id_venta, id_compra, id_producto, etc
    descripcion = Column(Text, nullable=False)
    fecha_evento = Column(TIMESTAMP, nullable=False)


# --- NUEVO: Modelo para notificacion_preferencia ---
class NotificacionPreferencia(Base):
    __tablename__ = "notificacion_preferencia"
    id_preferencia = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    tipo_evento = Column(String(50), nullable=False)
    recibir_app = Column(Boolean, default=True)
    recibir_email = Column(Boolean, default=False)
    recibir_whatsapp = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)

    # Relaciones (opcional)
    usuario = relationship("Usuario", backref="preferencias_notificacion")


# --- NUEVO: Modelo para notificacion_email_log ---
class NotificacionEmailLog(Base):
    __tablename__ = "notificacion_email_log"
    id_log = Column(Integer, primary_key=True, index=True)
    id_notificacion = Column(Integer, ForeignKey("notificacion.id_notificacion"), nullable=False)
    email_destino = Column(String(150))
    estado = Column(String(20))
    fecha_envio = Column(TIMESTAMP)

    notificacion = relationship("Notificacion", backref="email_logs")
