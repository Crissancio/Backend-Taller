from sqlalchemy.orm import Session
from app.users.models import Usuario

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()
