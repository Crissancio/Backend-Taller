import os
from fastapi import FastAPI, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.microempresas.router import router as microempresas_router
from app.users.router import router as users_router
from app.auth.router import router as auth_router
from app.auth import service as auth_service
from app.auth.schemas import TokenResponse
from app.database.session import get_db
from app.database.init_db import init_db
from app.planes.router import router as planes_router
from app.suscripciones.router import router as suscripciones_router
from app.superadmins.router import router as superadmins_router
from app.admins.router import router as admins_router

from app.vendedores.router import router as vendedores_router
from app.clientes.router import router as clientes_router
from app.productos.router import router as productos_router
from app.inventario.router import router as inventario_router

from app.notificaciones.router import router as notificaciones_router
from app.notificaciones.websocket import router as notificaciones_ws_router
from app.ventas.router import router as ventas_router

from app.auth.base_user import Usuario  # sin SuperAdmin
from app.auth.models import SuperAdmin
from app.users.models import AdminMicroempresa, Vendedor
from app.microempresas.models import Microempresa
from app.planes.models import Plan
from app.suscripciones.models import Suscripcion



app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Agregamos ambas variaciones por seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# -- IMAGENES 
# 1. Aseguramos que la carpeta exista para que no de error al arrancar
os.makedirs("public/productos", exist_ok=True)

# 2. Montamos la ruta "/public" para que sirva los archivos de la carpeta física "public"
app.mount("/public", StaticFiles(directory="public"), name="public")


# Ordenar routers para que Swagger muestre primero usuarios, luego roles, luego otros módulos
app.include_router(users_router)
app.include_router(clientes_router)
app.include_router(superadmins_router)
app.include_router(admins_router)
app.include_router(vendedores_router)
app.include_router(microempresas_router)
app.include_router(planes_router)
app.include_router(suscripciones_router)
app.include_router(auth_router)
app.include_router(productos_router)
app.include_router(inventario_router)
app.include_router(notificaciones_router)
app.include_router(ventas_router)

# Habilitar WebSocket para notificaciones
app.include_router(notificaciones_ws_router)

# Ruta /login en la raíz, reutilizando la lógica de auth
@app.post("/login", response_model=TokenResponse, tags=["Auth"])
def login_root(
    username: str = Form(..., description="Correo electrónico"),
    password: str = Form(...),
    db = Depends(get_db)
):
    token = auth_service.login(db, username, password)
    if not token:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": token}


@app.on_event("startup")
def startup_event():
    init_db()
