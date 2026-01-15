
from pydantic import BaseModel, validator, ValidationError
from pydantic import field_validator
from typing import Optional




class PlanBase(BaseModel):
    nombre: str
    precio: float
    limite_productos: int
    limite_admins: int
    limite_vendedores: int
    activo: bool = True
    descripcion: Optional[str] = None

    @field_validator('precio')
    @classmethod
    def precio_no_negativo(cls, v, info):
        if not isinstance(v, (int, float)):
            raise ValueError('El precio debe ser un número')
        if v < 0:
            raise ValueError('El precio no puede ser negativo')
        return v

    @field_validator('limite_productos', 'limite_admins', 'limite_vendedores')
    @classmethod
    def limites_no_negativos(cls, v, info):
        if not isinstance(v, int):
            raise ValueError(f'{info.field_name} debe ser un número entero')
        if v < 0:
            raise ValueError(f'{info.field_name} no puede ser negativo')
        return v

class PlanCreate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id_plan: int
    class Config:
        from_attributes = True
