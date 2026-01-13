from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.users.schemas import UsuarioResponse

router = APIRouter()

@router.get("/me", response_model=UsuarioResponse)
def get_me(user=Depends(get_current_user)):
    return user
