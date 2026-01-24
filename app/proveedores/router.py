
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db
from app.proveedores import service, schemas

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

# 1️⃣ Crear proveedor
@router.post("", response_model=schemas.ProveedorResponse)
def crear_proveedor(data: schemas.ProveedorCreate, db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.crear_proveedor(db, data)

# 2️⃣ Listar proveedores por microempresa
@router.get("", response_model=List[schemas.ProveedorResponse])
def listar_proveedores(id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	if id_microempresa is None:
		raise HTTPException(status_code=400, detail="Debe especificar la microempresa")
	return service.listar_proveedores(db, id_microempresa)

# 3️⃣ Obtener proveedor por ID (con métodos de pago y productos)
@router.get("/{id_proveedor}")
def obtener_proveedor(id_proveedor: int = Path(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	proveedor, metodos_pago, productos = service.obtener_proveedor(db, id_proveedor, id_microempresa)
	return {
		"proveedor": schemas.ProveedorResponse.model_validate(proveedor),
		"metodos_pago": [schemas.ProveedorMetodoPagoResponse.model_validate(m) for m in metodos_pago],
		"productos": [schemas.ProveedorProductoResponse.model_validate(p) for p in productos]
	}

# 4️⃣ Actualizar proveedor
@router.put("/{id_proveedor}", response_model=schemas.ProveedorResponse)
def actualizar_proveedor(id_proveedor: int = Path(...), data: schemas.ProveedorUpdate = Body(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.actualizar_proveedor(db, id_proveedor, data, id_microempresa)

# 5️⃣ Activar/desactivar proveedor
@router.patch("/{id_proveedor}/estado", response_model=schemas.ProveedorResponse)
def cambiar_estado_proveedor(id_proveedor: int = Path(...), estado: bool = Body(..., embed=True), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.cambiar_estado_proveedor(db, id_proveedor, estado, id_microempresa)

# 6️⃣ Crear método de pago
@router.post("/{id_proveedor}/metodos-pago", response_model=schemas.ProveedorMetodoPagoResponse)
def crear_metodo_pago(id_proveedor: int = Path(...), data: schemas.ProveedorMetodoPagoCreate = Body(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.crear_metodo_pago(db, id_proveedor, data, id_microempresa)


# 7️⃣ Listar métodos de pago activos
@router.get("/{id_proveedor}/metodos-pago", response_model=List[schemas.ProveedorMetodoPagoResponse])
def listar_metodos_pago(id_proveedor: int = Path(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.listar_metodos_pago(db, id_proveedor, id_microempresa)

# Listar métodos de pago NO activos
@router.get("/{id_proveedor}/metodos-pago/no-activos", response_model=List[schemas.ProveedorMetodoPagoResponse])
def listar_metodos_pago_no_activos(id_proveedor: int = Path(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.listar_metodos_pago(db, id_proveedor, id_microempresa, solo_activos=False)

# 8️⃣ Activar/desactivar método de pago
@router.patch("/metodos-pago/{id_metodo_pago}/estado", response_model=schemas.ProveedorMetodoPagoResponse)
def cambiar_estado_metodo_pago(id_metodo_pago: int = Path(...), activo: bool = Body(..., embed=True), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.cambiar_estado_metodo_pago(db, id_metodo_pago, activo, id_microempresa)

# 9️⃣ Asociar producto a proveedor
@router.post("/{id_proveedor}/productos", response_model=schemas.ProveedorProductoResponse)
def asociar_producto_proveedor(id_proveedor: int = Path(...), data: schemas.ProveedorProductoCreate = Body(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.asociar_producto_proveedor(db, id_proveedor, data, id_microempresa)


# 🔟 Listar productos de proveedor (activos)
@router.get("/{id_proveedor}/productos", response_model=List[schemas.ProveedorProductoResponse])
def listar_productos_proveedor(id_proveedor: int = Path(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.listar_productos_proveedor(db, id_proveedor, id_microempresa)

# Listar productos NO activos de proveedor
@router.get("/{id_proveedor}/productos/no-activos", response_model=List[schemas.ProveedorProductoResponse])
def listar_productos_no_activos_proveedor(id_proveedor: int = Path(...), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.listar_productos_proveedor(db, id_proveedor, id_microempresa, solo_activos=False)

# 1️⃣1️⃣ Activar/desactivar producto del proveedor
@router.patch("/{id_proveedor}/productos/{id_producto}/estado", response_model=schemas.ProveedorProductoResponse)
def cambiar_estado_producto_proveedor(id_proveedor: int = Path(...), id_producto: int = Path(...), activo: bool = Body(..., embed=True), id_microempresa: int = Query(None), db: Session = Depends(get_db)):
	# TODO: Reemplazar None por user.id_microempresa cuando haya autenticación
	return service.cambiar_estado_producto_proveedor(db, id_proveedor, id_producto, activo, id_microempresa)
