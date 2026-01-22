from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas

def crear_categoria(db: Session, id_microempresa: int, categoria: schemas.CategoriaCreate):
    existe = db.query(models.Categoria).filter(
        models.Categoria.id_microempresa == id_microempresa,
        models.Categoria.nombre == categoria.nombre
    ).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre en la microempresa.")
    db_categoria = models.Categoria(
        id_microempresa=id_microempresa,
        nombre=categoria.nombre,
        descripcion=categoria.descripcion
    )
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def listar_categorias_activas(db: Session, id_microempresa: int):
    return db.query(models.Categoria).filter(
        models.Categoria.id_microempresa == id_microempresa,
        models.Categoria.activo == True
    ).all()

def editar_categoria(db: Session, id_categoria: int, id_microempresa: int, categoria: schemas.CategoriaUpdate):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id_categoria == id_categoria).first()
    if not db_categoria or db_categoria.id_microempresa != id_microempresa:
        raise HTTPException(status_code=404, detail="Categoría no encontrada en la microempresa.")
    db_categoria.nombre = categoria.nombre
    db_categoria.descripcion = categoria.descripcion
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def cambiar_estado_categoria(db: Session, id_categoria: int, estado: bool, id_microempresa: int):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id_categoria == id_categoria).first()
    if not db_categoria or db_categoria.id_microempresa != id_microempresa:
        raise HTTPException(status_code=404, detail="Categoría no encontrada en la microempresa.")
    db_categoria.activo = estado
    db.commit()
    db.refresh(db_categoria)
    return db_categoria
