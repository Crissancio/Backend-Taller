from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def crear_cliente(db: Session, data: schemas.ClienteCreate):
    cliente = models.Cliente(
        id_microempresa=data.id_microempresa,
        nombre=data.nombre,
        documento=data.documento,
        telefono=data.telefono,
        email=data.email,
        fecha_creacion=datetime.now(),
        estado=True
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente

def obtener_cliente(db: Session, id_cliente: int):
    return db.query(models.Cliente).filter_by(id_cliente=id_cliente).first()


# Listar todos los clientes (sin filtrar por estado)
def listar_clientes(db: Session):
    return db.query(models.Cliente).all()

# Listar clientes activos (sin filtrar por microempresa)
def listar_clientes_activos(db: Session):
    return db.query(models.Cliente).filter_by(estado=True).all()

# Listar clientes inactivos (sin filtrar por microempresa)
def listar_clientes_inactivos(db: Session):
    return db.query(models.Cliente).filter_by(estado=False).all()

def listar_clientes_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Cliente).filter_by(id_microempresa=id_microempresa).all()

def listar_clientes_activos_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Cliente).filter_by(id_microempresa=id_microempresa, estado=True).all()

def listar_clientes_inactivos_por_microempresa(db: Session, id_microempresa: int):
    return db.query(models.Cliente).filter_by(id_microempresa=id_microempresa, estado=False).all()

def actualizar_cliente(db: Session, id_cliente: int, data: schemas.ClienteUpdate):
    cliente = db.query(models.Cliente).filter_by(id_cliente=id_cliente).first()
    if not cliente:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return cliente

def baja_logica_cliente(db: Session, id_cliente: int):
    cliente = db.query(models.Cliente).filter_by(id_cliente=id_cliente).first()
    if not cliente:
        return None
    cliente.estado = False
    db.commit()
    return cliente

def eliminar_cliente(db: Session, id_cliente: int):
    cliente = db.query(models.Cliente).filter_by(id_cliente=id_cliente).first()
    if not cliente:
        return False
    db.delete(cliente)
    db.commit()
    return True
