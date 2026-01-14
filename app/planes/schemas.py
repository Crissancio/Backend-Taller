from pydantic import BaseModel
from typing import Optional

class PlanBase(BaseModel):
    nombre: str
    precio: float
    limite_usuarios: int
    descripcion: Optional[str] = None

class PlanCreate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id_plan: int
    class Config:
        from_attributes = True
