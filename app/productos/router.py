from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Path, Body, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import schemas, service
from app.core.dependencies import get_current_user
#-----------------imports para notificaciones------
from app.notificaciones import service as notif_service
from app.notificaciones.schemas import NotificacionCreate
from typing import Optional

router = APIRouter(prefix="/productos", tags=["Productos"])

# --- CATEGORÍAS (Endpoints Admin/Microempresa por URL) ---
@router.post("/microempresas/{id_microempresa}/categorias", response_model=schemas.CategoriaResponse)
def crear_categoria_admin(id_microempresa: int = Path(...), categoria: schemas.CategoriaCreate = Body(...), db: Session = Depends(get_db)):
    return service.crear_categoria(db, id_microempresa, categoria)

@router.get("/microempresas/{id_microempresa}/categorias", response_model=list[schemas.CategoriaResponse])
def listar_categorias_activas_admin(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_categorias_activas(db, id_microempresa)

@router.put("/categorias/{id_categoria}", response_model=schemas.CategoriaResponse)
def editar_categoria(id_categoria: int, categoria: schemas.CategoriaUpdate = Body(...), id_microempresa: int = Body(...), db: Session = Depends(get_db)):
    return service.editar_categoria(db, id_categoria, id_microempresa, categoria)

@router.patch("/categorias/{id_categoria}/estado", response_model=schemas.CategoriaResponse)
def cambiar_estado_categoria(id_categoria: int, estado: bool = Body(...), id_microempresa: int = Body(...), db: Session = Depends(get_db)):
    return service.cambiar_estado_categoria(db, id_categoria, id_microempresa, estado)

# --- ENDPOINT DEL PORTAL (PÚBLICO) ---
@router.get("/portal/{id_microempresa}/listado", response_model=list[schemas.ProductoResponse])
def listar_productos_portal_publico(id_microempresa: int, db: Session = Depends(get_db)):
    """
    Lista productos activos y con stock > 0 para el portal público.
    No requiere autenticación.
    """
    return service.listar_productos_portal_publico(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/buscar", response_model=list[schemas.ProductoResponse])
def filtrar_productos_por_microempresa_y_nombre(id_microempresa: int, nombre: str, db: Session = Depends(get_db)):
    return service.filtrar_productos_por_microempresa_y_nombre(db, id_microempresa, nombre)

# --- ENDPOINTS GLOBALES (CATEGORIAS) ---
@router.get("/categoria/activas", response_model=list[schemas.CategoriaResponse])
def listar_categorias_activas_global(db: Session = Depends(get_db)):
    # CORREGIDO: Llama a función sin argumentos de ID
    return service.listar_todas_categorias_activas(db)

@router.get("/categoria/inactivas", response_model=list[schemas.CategoriaResponse])
def listar_categorias_inactivas_global(db: Session = Depends(get_db)):
    return service.listar_categorias_inactivas(db)

@router.post("/{id_producto}/activar", response_model=schemas.ProductoResponse)
def activar_producto(id_producto: int, db: Session = Depends(get_db)):
    result = service.activar_producto(db, id_producto)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result

@router.post("/{id_producto}/desactivar", response_model=schemas.ProductoResponse)
def desactivar_producto(id_producto: int, db: Session = Depends(get_db)):
    result = service.desactivar_producto(db, id_producto)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result

@router.get("/categoria/{id_categoria}", response_model=schemas.CategoriaResponse)
def obtener_categoria(id_categoria: int, db: Session = Depends(get_db)):
    categoria = db.query(service.models.Categoria).filter(service.models.Categoria.id_categoria == id_categoria).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

# --- CATEGORÍAS (Endpoints con Auth Current User) ---
@router.post("/categoria", response_model=schemas.CategoriaResponse)
def crear_categoria(
    categoria: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    id_microempresa = None
    if hasattr(current_user, "admin_microempresa") and current_user.admin_microempresa:
        id_microempresa = current_user.admin_microempresa.id_microempresa
    elif hasattr(current_user, "vendedor") and current_user.vendedor:
        id_microempresa = current_user.vendedor.id_microempresa
    else:
        raise HTTPException(status_code=403, detail="No autorizado para crear categorías")
    
    categoria_data = categoria.dict()
    categoria_data["id_microempresa"] = id_microempresa
    
    # CORREGIDO: Se pasa id_microempresa
    return service.crear_categoria(db, id_microempresa, schemas.CategoriaCreate(**categoria_data))

@router.put("/categoria/{id_categoria}", response_model=schemas.CategoriaResponse)
def actualizar_categoria(id_categoria: int, categoria: schemas.CategoriaUpdate, db: Session = Depends(get_db)):
    result = service.actualizar_categoria(db, id_categoria, categoria)
    if not result:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return result

@router.delete("/categoria/{id_categoria}", response_model=schemas.CategoriaResponse)
def baja_logica_categoria(id_categoria: int, db: Session = Depends(get_db)):
    result = service.baja_logica_categoria(db, id_categoria)
    if not result:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return result

@router.get("/categoria", response_model=list[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return service.listar_categorias(db)

@router.get("/categoria/microempresa/{id_microempresa}", response_model=list[schemas.CategoriaResponse])
def listar_categorias_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return db.query(service.models.Categoria).filter(service.models.Categoria.id_microempresa == id_microempresa).all()

@router.get("/categoria/microempresa/{id_microempresa}/activas", response_model=list[schemas.CategoriaResponse])
def listar_categorias_activas_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_categorias_activas(db, id_microempresa)

@router.get("/categoria/microempresa/{id_microempresa}/inactivas", response_model=list[schemas.CategoriaResponse])
def listar_categorias_inactivas_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_categorias_inactivas(db)

@router.post("/categoria/{id_categoria}/activar", response_model=schemas.CategoriaResponse)
def activar_categoria(id_categoria: int, db: Session = Depends(get_db)):
    categoria = db.query(service.models.Categoria).filter(service.models.Categoria.id_categoria == id_categoria).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    categoria.activo = True
    db.commit()
    db.refresh(categoria)
    return categoria

# --- PRODUCTOS (Lógica Principal con Auth) ---
@router.post("/", response_model=schemas.ProductoResponse)
def crear_producto(
    nombre: str = Form(...),
    descripcion: str = Form(None),
    precio_venta: float = Form(...),
    costo_compra: float = Form(None),
    codigo: str = Form(None),
    estado: bool = Form(True),
    id_categoria: int = Form(...),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    id_microempresa = None
    if hasattr(current_user, "admin_microempresa") and current_user.admin_microempresa:
        id_microempresa = current_user.admin_microempresa.id_microempresa
    elif hasattr(current_user, "vendedor") and current_user.vendedor:
        id_microempresa = current_user.vendedor.id_microempresa
    else:
        raise HTTPException(status_code=403, detail="No autorizado para crear productos")

    imagen_path = None
    if imagen:
        import os
        from uuid import uuid4
        ext = os.path.splitext(imagen.filename)[1]
        filename = f"{uuid4().hex}{ext}"
        os.makedirs(os.path.join("public", "productos"), exist_ok=True)
        save_path = os.path.join("public", "productos", filename)
        with open(save_path, "wb") as f:
            f.write(imagen.file.read())
        imagen_path = f"/public/productos/{filename}"

    producto_data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio_venta": precio_venta,
        "costo_compra": costo_compra,
        "codigo": codigo,
        "imagen": imagen_path,
        "estado": estado,
        "id_categoria": id_categoria,
        "id_microempresa": id_microempresa
    }
    
    # CORREGIDO: Se pasa id_microempresa
    nuevo_producto = service.crear_producto(db, id_microempresa, schemas.ProductoCreate(**producto_data))

    '''
    try:
        notif_data = NotificacionCreate(
            id_microempresa=id_microempresa,
            id_usuario=current_user.id_usuario,
            tipo="STOCK_BAJO",
            mensaje=f"Alerta: Se ha creado el producto '{nuevo_producto.nombre}' con Stock 0. Por favor actualice el inventario."
        )
        notif_service.crear_notificacion(db, notif_data)
    except Exception as e:
        print(f"Error creando notificación: {e}") 
    '''
    return nuevo_producto

@router.put("/{id_producto}", response_model=schemas.ProductoResponse)
def actualizar_producto(id_producto: int, producto: schemas.ProductoUpdate, db: Session = Depends(get_db)):
    result = service.actualizar_producto(db, id_producto, producto)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result

@router.delete("/{id_producto}", response_model=schemas.ProductoResponse)
def eliminar_producto_fisico(id_producto: int, db: Session = Depends(get_db)):
    result = service.eliminar_producto_fisico(db, id_producto)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result

@router.get("/", response_model=list[schemas.ProductoResponse])
def listar_productos_global(db: Session = Depends(get_db)):
    return db.query(service.models.Producto).all()

@router.get("/microempresa/{id_microempresa}", response_model=list[schemas.ProductoResponse])
def listar_productos_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_productos_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/categoria/{id_categoria}", response_model=list[schemas.ProductoResponse])
def listar_productos_por_microempresa_categoria(id_microempresa: int, id_categoria: int, db: Session = Depends(get_db)):
    productos = db.query(service.models.Producto).filter(
        service.models.Producto.id_microempresa == id_microempresa,
        service.models.Producto.id_categoria == id_categoria
    ).all()
    return productos

@router.get("/activos", response_model=list[schemas.ProductoResponse])
def listar_productos_activos(db: Session = Depends(get_db)):
    return db.query(service.models.Producto).filter(service.models.Producto.estado == True).all()

@router.get("/inactivos", response_model=list[schemas.ProductoResponse])
def listar_productos_inactivos(db: Session = Depends(get_db)):
    return db.query(service.models.Producto).filter(service.models.Producto.estado == False).all()

# --- PRODUCTOS CON STOCK GLOBALES (Aquí estaba el error 500) ---
@router.get("/con-stock", response_model=list[schemas.ProductoResponse])
def listar_productos_con_stock(db: Session = Depends(get_db)):
    # CORREGIDO: Llama al servicio
    return service.listar_productos_con_stock_global(db)

@router.get("/sin-stock", response_model=list[schemas.ProductoResponse])
def listar_productos_sin_stock(db: Session = Depends(get_db)):
    # CORREGIDO: Llama al servicio
    return service.listar_productos_sin_stock_global(db)

@router.get("/{id_producto}", response_model=schemas.ProductoResponse)
def obtener_producto_detalle(id_producto: int, db: Session = Depends(get_db)):
    producto = db.query(service.models.Producto).filter(service.models.Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.get("/microempresa/{id_microempresa}/activos-con-stock", response_model=list[schemas.ProductoResponse])
def listar_productos_activos_con_stock_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_productos_activos_con_stock_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/activos", response_model=list[schemas.ProductoResponse])
def listar_productos_activos_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_productos_activos_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/inactivos-sin-stock", response_model=list[schemas.ProductoResponse])
def listar_productos_inactivos_sin_stock_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_productos_inactivos_sin_stock_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/buscar-nombre", response_model=list[schemas.ProductoResponse])
def buscar_productos_por_nombre_microempresa(id_microempresa: int, nombre: str, db: Session = Depends(get_db)):
    return service.buscar_productos_por_nombre_microempresa(db, id_microempresa, nombre)

@router.get("/microempresa/{id_microempresa}/con-stock", response_model=list[schemas.ProductoResponse])
def listar_productos_con_stock_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    return service.listar_productos_con_stock_por_microempresa(db, id_microempresa)

@router.get("/microempresa/{id_microempresa}/sin-stock", response_model=list[schemas.ProductoResponse])
def listar_productos_sin_stock_por_microempresa(id_microempresa: int, db: Session = Depends(get_db)):
    from app.inventario.models import Stock
    productos = db.query(service.models.Producto).join(Stock, service.models.Producto.id_producto == Stock.id_producto).filter(
        service.models.Producto.id_microempresa == id_microempresa,
        Stock.cantidad == 0
    ).all()
    return productos

@router.get("/catalogo/publico")
def obtener_catalogo_portal(db: Session = Depends(get_db)):
    productos = db.query(service.models.Producto).filter(service.models.Producto.estado == True).all()
    return productos

# --- PRODUCTOS (Endpoints por URL con ID explícito) ---
@router.post("/microempresas/{id_microempresa}/productos", response_model=schemas.ProductoResponse)
def crear_producto_por_url(id_microempresa: int, producto: schemas.ProductoCreate = Body(...), db: Session = Depends(get_db)):
    return service.crear_producto(db, id_microempresa, producto)

@router.get("/microempresas/{id_microempresa}/productos", response_model=list[schemas.ProductoResponse])
def listar_productos_con_filtros(id_microempresa: int, id_categoria: int = Query(None), estado: bool = Query(None), db: Session = Depends(get_db)):
    return service.listar_productos(db, id_microempresa, id_categoria, estado)

@router.get("/productos/{id_producto}", response_model=schemas.ProductoResponse)
def obtener_producto_por_id(id_producto: int, db: Session = Depends(get_db)):
    producto = db.query(service.models.Producto).filter(service.models.Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.put("/productos/{id_producto}", response_model=schemas.ProductoResponse)
def editar_producto_por_id(id_producto: int, producto: schemas.ProductoUpdate = Body(...), db: Session = Depends(get_db)):
    return service.editar_producto(db, id_producto, producto)

@router.patch("/productos/{id_producto}/estado", response_model=schemas.ProductoResponse)
def cambiar_estado_producto(id_producto: int, estado: bool = Body(...), db: Session = Depends(get_db)):
    return service.cambiar_estado_producto(db, id_producto, estado)