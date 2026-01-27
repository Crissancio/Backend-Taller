
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, UploadFile
from typing import Optional
from app.microempresas import models, schemas

# --- RUBRO SERVICES ---
def crear_rubro(db: Session, data: schemas.RubroCreate):
    if db.query(models.Rubro).filter(models.Rubro.nombre == data.nombre.strip()).first():
        raise HTTPException(status_code=400, detail="Ya existe un rubro con ese nombre")
    rubro = models.Rubro(
        nombre=data.nombre.strip(),
        descripcion=data.descripcion,
        activo=data.activo if data.activo is not None else True
    )
    db.add(rubro)
    db.commit()
    db.refresh(rubro)
    return rubro

def actualizar_rubro(db: Session, id_rubro: int, data: schemas.RubroUpdate):
    rubro = db.query(models.Rubro).filter_by(id_rubro=id_rubro).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    if data.nombre:
        nombre = data.nombre.strip()
        if nombre != rubro.nombre and db.query(models.Rubro).filter(models.Rubro.nombre == nombre).first():
            raise HTTPException(status_code=400, detail="Ya existe un rubro con ese nombre")
        rubro.nombre = nombre
    if data.descripcion is not None:
        rubro.descripcion = data.descripcion
    if data.activo is not None:
        rubro.activo = data.activo
    db.commit()
    db.refresh(rubro)
    return rubro

def cambiar_estado_rubro(db: Session, id_rubro: int, activo: bool):
    rubro = db.query(models.Rubro).filter_by(id_rubro=id_rubro).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    rubro.activo = activo
    db.commit()
    db.refresh(rubro)
    return rubro

def listar_rubros(db: Session, solo_activos: bool = False):
    query = db.query(models.Rubro)
    if solo_activos:
        query = query.filter_by(activo=True)
    return query.order_by(models.Rubro.nombre).all()

def obtener_rubro(db: Session, id_rubro: int):
    rubro = db.query(models.Rubro).filter_by(id_rubro=id_rubro).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    return rubro

def eliminar_rubro(db: Session, id_rubro: int):
    rubro = db.query(models.Rubro).filter_by(id_rubro=id_rubro).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    if db.query(models.Microempresa).filter_by(id_rubro=id_rubro).first():
        raise HTTPException(status_code=400, detail="No se puede eliminar un rubro en uso por microempresas")
    db.delete(rubro)
    db.commit()
    return True

# --- MICROEMPRESA SERVICES ---
def crear_microempresa(db: Session, data: schemas.MicroempresaCreate):
    if db.query(models.Microempresa).filter(models.Microempresa.nit == data.nit.strip()).first():
        raise HTTPException(status_code=400, detail="Ya existe una microempresa con ese NIT")
    rubro = db.query(models.Rubro).filter_by(id_rubro=data.id_rubro, activo=True).first()
    if not rubro:
        raise HTTPException(status_code=400, detail="El rubro especificado no existe o está inactivo")
    micro = models.Microempresa(
        nombre=data.nombre.strip(),
        nit=data.nit.strip(),
        correo_contacto=data.correo_contacto,
        direccion=data.direccion,
        telefono=data.telefono,
        tipo_atencion=data.tipo_atencion.strip() if data.tipo_atencion else None,
        latitud=data.latitud,
        longitud=data.longitud,
        dias_atencion=data.dias_atencion,
        horario_atencion=data.horario_atencion,
        moneda=data.moneda.strip() if data.moneda else None,
        logo=data.logo,
        id_rubro=data.id_rubro
    )
    db.add(micro)
    db.commit()
    db.refresh(micro)
    return micro

def actualizar_microempresa(db: Session, id_microempresa: int, data: schemas.MicroempresaUpdate):
    micro = db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    if data.nit:
        nit = data.nit.strip()
        if nit != micro.nit and db.query(models.Microempresa).filter(models.Microempresa.nit == nit).first():
            raise HTTPException(status_code=400, detail="Ya existe una microempresa con ese NIT")
        micro.nit = nit
    if data.nombre:
        micro.nombre = data.nombre.strip()
    if data.correo_contacto is not None:
        micro.correo_contacto = data.correo_contacto
    if data.direccion is not None:
        micro.direccion = data.direccion
    if data.telefono is not None:
        micro.telefono = data.telefono
    if data.tipo_atencion is not None:
        micro.tipo_atencion = data.tipo_atencion.strip() if data.tipo_atencion else None
    if data.latitud is not None:
        micro.latitud = data.latitud
    if data.longitud is not None:
        micro.longitud = data.longitud
    if data.dias_atencion is not None:
        micro.dias_atencion = data.dias_atencion
    if data.horario_atencion is not None:
        micro.horario_atencion = data.horario_atencion
    if data.moneda is not None:
        micro.moneda = data.moneda.strip() if data.moneda else None
    if data.logo is not None:
        micro.logo = data.logo
    if data.id_rubro is not None:
        rubro = db.query(models.Rubro).filter_by(id_rubro=data.id_rubro, activo=True).first()
        if not rubro:
            raise HTTPException(status_code=400, detail="El rubro especificado no existe o está inactivo")
        micro.id_rubro = data.id_rubro
    db.commit()
    db.refresh(micro)
    return micro

def listar_microempresas(db: Session, solo_activas: bool = False, id_rubro: Optional[int] = None):
    query = db.query(models.Microempresa)
    if solo_activas:
        query = query.filter_by(activo=True)
    if id_rubro is not None:
        query = query.filter_by(id_rubro=id_rubro)
    return query.order_by(models.Microempresa.nombre).all()

def obtener_microempresa(db: Session, id_microempresa: int):
    micro = db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    return micro

def activar_microempresa(db: Session, id_microempresa: int):
    micro = db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    if micro.activo:
        raise HTTPException(status_code=400, detail="La microempresa ya está activa")
    micro.activo = True
    db.commit()
    db.refresh(micro)
    return micro

def desactivar_microempresa(db: Session, id_microempresa: int):
    micro = db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    if not micro.activo:
        raise HTTPException(status_code=400, detail="La microempresa ya está inactiva")
    micro.activo = False
    db.commit()
    db.refresh(micro)
    return micro

def listar_microempresas_por_rubro(db: Session, id_rubro: int, solo_activas: bool = False):
    query = db.query(models.Microempresa).filter_by(id_rubro=id_rubro)
    if solo_activas:
        query = query.filter_by(activo=True)
    return query.order_by(models.Microempresa.nombre).all()

def subir_logo_microempresa(db: Session, id_microempresa: int, file: UploadFile):
    micro = db.query(models.Microempresa).filter_by(id_microempresa=id_microempresa).first()
    if not micro:
        raise HTTPException(status_code=404, detail="Microempresa no encontrada")
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos de imagen")
    # Validar tamaño (ejemplo: 2MB máximo)
    contents = file.file.read()
    max_size = 2 * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máx 2MB)")
    # Guardar archivo
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"]:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado")
    dir_path = os.path.join("public", str(micro.id_microempresa))
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"logo{ext}")
    with open(file_path, "wb") as f:
        f.write(contents)
    # Guardar ruta en DB (relativa)
    micro.logo = file_path.replace("\\", "/")
    db.commit()
    db.refresh(micro)
    return micro