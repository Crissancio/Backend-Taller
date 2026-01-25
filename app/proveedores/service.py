
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.proveedores import models, schemas
from app.microempresas.models import Microempresa
from app.productos.models import Producto

# 1️⃣ Crear proveedor
def crear_proveedor(db: Session, data: schemas.ProveedorCreate):
	micro = db.query(Microempresa).filter_by(id_microempresa=data.id_microempresa).first()
	if not micro:
		raise HTTPException(status_code=404, detail="Microempresa no encontrada")
	proveedor = models.Proveedor(
		id_microempresa=data.id_microempresa,
		nombre=data.nombre,
		contacto=data.contacto,
		email=data.email,
		estado=True
	)
	db.add(proveedor)
	db.commit()
	db.refresh(proveedor)
	# Evento: Proveedor creado
	from app.notificaciones import service as notif_service
	notif_service.generar_evento(
		tipo_evento="PROVEEDOR_CREADO",
		mensaje=f"Se ha creado el proveedor '{proveedor.nombre}' en la microempresa.",
		id_microempresa=proveedor.id_microempresa,
		referencia_id=proveedor.id_proveedor,
		db=db
	)
	return proveedor

# 2️⃣ Listar proveedores por microempresa
def listar_proveedores(db: Session, id_microempresa: int):
	return db.query(models.Proveedor).filter_by(id_microempresa=id_microempresa, estado=True).all()

# 3️⃣ Obtener proveedor por ID (con métodos de pago y productos)
def obtener_proveedor(db: Session, id_proveedor: int, id_microempresa: int = None):
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="El proveedor no pertenece a la microempresa solicitada")
	metodos_pago = db.query(models.ProveedorMetodoPago).filter_by(id_proveedor=id_proveedor, activo=True).all()
	productos = db.query(models.ProveedorProducto).filter_by(id_proveedor=id_proveedor, activo=True).all()
	return proveedor, metodos_pago, productos

# 4️⃣ Actualizar proveedor
def actualizar_proveedor(db: Session, id_proveedor: int, data: schemas.ProveedorBase, id_microempresa: int = None):
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor, estado=True).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede modificar proveedores de otra microempresa")
	proveedor.nombre = data.nombre
	proveedor.contacto = data.contacto
	proveedor.email = data.email
	db.commit()
	db.refresh(proveedor)
	return proveedor

# 5️⃣ Activar/desactivar proveedor
def cambiar_estado_proveedor(db: Session, id_proveedor: int, estado: bool, id_microempresa: int = None):
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede modificar proveedores de otra microempresa")
	proveedor.estado = estado
	db.commit()
	db.refresh(proveedor)
	return proveedor

# 6️⃣ Crear método de pago
def crear_metodo_pago(db: Session, id_proveedor: int, data: schemas.ProveedorMetodoPagoCreate, id_microempresa: int = None):
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor, estado=True).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede crear métodos de pago para proveedores de otra microempresa")
	metodo = models.ProveedorMetodoPago(
		id_proveedor=id_proveedor,
		tipo=data.tipo,
		descripcion=data.descripcion,
		datos_pago=data.datos_pago,
		qr_imagen=data.qr_imagen,
		activo=True
	)
	db.add(metodo)
	db.commit()
	db.refresh(metodo)
	# Evento: Método de pago agregado
	from app.notificaciones import service as notif_service
	notif_service.generar_evento(
		tipo_evento="METODO_PAGO_AGREGADO",
		mensaje=f"Se ha agregado un nuevo método de pago al proveedor '{proveedor.nombre}'.",
		id_microempresa=proveedor.id_microempresa,
		referencia_id=proveedor.id_proveedor,
		db=db
	)
	return metodo

# 7️⃣ Listar métodos de pago activos
def listar_metodos_pago(db: Session, id_proveedor: int, id_microempresa: int = None, solo_activos: bool = True):
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede listar métodos de pago de otra microempresa")
	query = db.query(models.ProveedorMetodoPago).filter_by(id_proveedor=id_proveedor)
	if solo_activos:
		query = query.filter_by(activo=True)
	else:
		query = query.filter_by(activo=False)
	return query.all()

# 8️⃣ Activar/desactivar método de pago
def cambiar_estado_metodo_pago(db: Session, id_metodo_pago: int, activo: bool, id_microempresa: int = None):
	metodo = db.query(models.ProveedorMetodoPago).filter_by(id_metodo_pago=id_metodo_pago).first()
	if not metodo:
		raise HTTPException(status_code=404, detail="Método de pago no encontrado")
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=metodo.id_proveedor).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor del método de pago no encontrado")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede modificar métodos de pago de otra microempresa")
	metodo.activo = activo
	db.commit()
	db.refresh(metodo)
	return metodo

# 9️⃣ Asociar producto a proveedor
def asociar_producto_proveedor(db: Session, id_proveedor: int, data: schemas.ProveedorProductoCreate, id_microempresa: int = None):
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor, estado=True).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede asociar productos a proveedores de otra microempresa")
	producto = db.query(Producto).filter_by(id_producto=data.id_producto).first()
	if not producto:
		raise HTTPException(status_code=404, detail="Producto no encontrado")
	if producto.id_microempresa != proveedor.id_microempresa:
		raise HTTPException(status_code=400, detail="El producto no pertenece a la microempresa del proveedor")
	existe = db.query(models.ProveedorProducto).filter_by(id_proveedor=id_proveedor, id_producto=data.id_producto).first()
	if existe:
		raise HTTPException(status_code=409, detail="El producto ya está asociado a este proveedor")
	rel = models.ProveedorProducto(
		id_proveedor=id_proveedor,
		id_producto=data.id_producto,
		precio_referencia=data.precio_referencia,
		activo=True
	)
	db.add(rel)
	db.commit()
	db.refresh(rel)
	return rel

# 🔟 Listar productos de proveedor
def listar_productos_proveedor(db: Session, id_proveedor: int, id_microempresa: int = None, solo_activos: bool = True):
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede listar productos de proveedores de otra microempresa")
	query = db.query(models.ProveedorProducto).filter_by(id_proveedor=id_proveedor)
	if solo_activos:
		query = query.filter_by(activo=True)
	else:
		query = query.filter_by(activo=False)
	return query.all()

# 1️⃣1️⃣ Activar/desactivar producto del proveedor
def cambiar_estado_producto_proveedor(db: Session, id_proveedor: int, id_producto: int, activo: bool, id_microempresa: int = None):
	rel = db.query(models.ProveedorProducto).filter_by(id_proveedor=id_proveedor, id_producto=id_producto).first()
	if not rel:
		raise HTTPException(status_code=404, detail="Relación proveedor-producto no encontrada")
	proveedor = db.query(models.Proveedor).filter_by(id_proveedor=id_proveedor).first()
	if not proveedor:
		raise HTTPException(status_code=404, detail="Proveedor no encontrado")
	if id_microempresa is not None and proveedor.id_microempresa != id_microempresa:
		raise HTTPException(status_code=403, detail="No puede modificar productos de proveedores de otra microempresa")
	rel.activo = activo
	db.commit()
	db.refresh(rel)
	# Evento: Producto activado/desactivado para proveedor
	from app.notificaciones import service as notif_service
	estado_str = "activado" if activo else "desactivado"
	notif_service.generar_evento(
		tipo_evento="PRODUCTO_" + estado_str.upper(),
		mensaje=f"El producto ID {id_producto} ha sido {estado_str} para el proveedor ID {id_proveedor}.",
		id_microempresa=proveedor.id_microempresa,
		referencia_id=id_producto,
		db=db
	)
	return rel
