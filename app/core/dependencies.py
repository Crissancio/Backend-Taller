
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import SECRET_KEY, ALGORITHM
from app.database.session import get_db
from app.users.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_user_role(user, db: Session):
    """Devuelve el rol principal del usuario: 'superadmin', 'adminmicroempresa', 'vendedor' o 'usuario'"""
    # SuperAdmin
    if hasattr(user, 'super_admin') and user.super_admin:
        return 'superadmin'
    # AdminMicroempresa
    if hasattr(user, 'admin_microempresa') and user.admin_microempresa:
        return 'adminmicroempresa'
    # Vendedor
    if hasattr(user, 'vendedor') and user.vendedor:
        return 'vendedor'
    return 'usuario'


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)

    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=401)

    return user
