from fastapi import FastAPI

from app.microempresas.router import router as microempresas_router
from app.users.router import router as users_router
from app.auth.router import router as auth_router
from app.database.init_db import init_db
from app.planes.router import router as planes_router
from app.suscripciones.router import router as suscripciones_router
from app.superadmins.router import router as superadmins_router
from app.admins.router import router as admins_router
from app.vendedores.router import router as vendedores_router

from app.auth.base_user import Usuario  # sin SuperAdmin
from app.auth.models import SuperAdmin
from app.users.models import AdminMicroempresa, Vendedor
from app.microempresas.models import Microempresa
from app.planes.models import Plan
from app.suscripciones.models import Suscripcion

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(microempresas_router)
app.include_router(planes_router)
app.include_router(suscripciones_router)
app.include_router(superadmins_router)
app.include_router(admins_router)
app.include_router(vendedores_router)

@app.on_event("startup")
def startup_event():
    init_db()
