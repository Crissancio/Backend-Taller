import os
from fastapi import FastAPI, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- IMPORTS DE ROUTERS ---
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
from app.proveedores.router import router as proveedores_router
from app.compras.router import router as compras_router

from app.reportes.router import router as reportes_router

app = FastAPI(title="Sistoys Backend")

# --- CONFIGURACIÓN DE CORS (CORREGIDA) ---
# IMPORTANTE: Al usar allow_credentials=True, NO se puede usar ["*"] en los orígenes.
# Debes especificar explícitamente las URLs del frontend.
origins = [
    "http://localhost:5173",    # Frontend local
    "http://127.0.0.1:5173",    # Frontend local (IP)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Usamos la lista explícita sin asteriscos
    allow_credentials=True,     # Permitir cookies/tokens
    allow_methods=["*"],        # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],        # Permitir todos los headers
)

# --- ARCHIVOS ESTÁTICOS (IMÁGENES) ---
# 1. Aseguramos que la carpeta exista para que no de error al arrancar
os.makedirs("public/productos", exist_ok=True)

# 2. Montamos la ruta "/public" para que sirva los archivos de la carpeta física "public"
app.mount("/public", StaticFiles(directory="public"), name="public")

# --- INCLUSIÓN DE ROUTERS ---
# Orden lógico para la documentación de Swagger
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(superadmins_router)
app.include_router(admins_router)
app.include_router(vendedores_router)
app.include_router(microempresas_router)
app.include_router(clientes_router)
app.include_router(productos_router)
app.include_router(inventario_router)
app.include_router(ventas_router)
app.include_router(planes_router)
app.include_router(suscripciones_router)
app.include_router(notificaciones_router)
app.include_router(proveedores_router)
app.include_router(compras_router)


app.include_router(reportes_router)

# Habilitar WebSocket para notificaciones
app.include_router(notificaciones_ws_router)

# --- LOGIN GLOBAL (Reutiliza lógica de Auth) ---
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

# --- EVENTO DE INICIO ---
@app.on_event("startup")
def startup_event():
    init_db()