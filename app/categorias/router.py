from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service

router = APIRouter()

@router.post("/microempresas/{id_microempresa}/categorias", response_model=schemas.CategoriaResponse)
def crear_categoria(id_microempresa: int = Path(...), categoria: schemas.CategoriaCreate = Body(...), db: Session = Depends(get_db)):
    return service.crear_categoria(db, id_microempresa, categoria)

@router.get("/microempresas/{id_microempresa}/categorias", response_model=list[schemas.CategoriaResponse])
def listar_categorias(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_categorias_activas(db, id_microempresa)

@router.put("/categorias/{id_categoria}", response_model=schemas.CategoriaResponse)
def editar_categoria(id_categoria: int, categoria: schemas.CategoriaUpdate = Body(...), id_microempresa: int = Body(...), db: Session = Depends(get_db)):
    return service.editar_categoria(db, id_categoria, id_microempresa, categoria)

@router.patch("/categorias/{id_categoria}/estado", response_model=schemas.CategoriaResponse)
def cambiar_estado_categoria(id_categoria: int, estado: bool = Body(...), id_microempresa: int = Body(...), db: Session = Depends(get_db)):
    return service.cambiar_estado_categoria(db, id_categoria, estado, id_microempresa)
