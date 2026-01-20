from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.auth.base_user import Usuario
from app.users.models import AdminMicroempresa, Vendedor
from app.microempresas.models import Microempresa
from app.planes.models import Plan  # Importar Plan desde su módulo
from app.suscripciones.models import Suscripcion  # Importar Suscripcion desde su módulo

DATABASE_URL = "sqlite:///./test.db"  # o tu URL real
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
