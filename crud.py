from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- User Functions ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Field Functions ---
def get_fields_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Field).filter(models.Field.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_field(db: Session, field: schemas.FieldCreate, user_id: int):
    db_field = models.Field(**field.model_dump(), owner_id=user_id)
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field