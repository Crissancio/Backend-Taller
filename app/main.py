from fastapi import FastAPI

from app.microempresas.router import router as microempresas_router
from app.users.router import router as users_router
from app.auth.router import router as auth_router
from app.database.init_db import init_db

from app.auth.base_user import Usuario  # sin SuperAdmin
from app.auth.models import SuperAdmin
from app.users.models import AdminMicroempresa, Vendedor
from app.microempresas.models import Microempresa, Suscripcion, Plan

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(microempresas_router)

@app.on_event("startup")
def startup_event():
    init_db()
