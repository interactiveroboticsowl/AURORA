from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.data import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def check_admin_exists(db: Session):
    return (
        db.query(models.User).filter(models.User.is_admin == True).first() is not None
    )


def create_user(db: Session, user: schemas.UserCreate, admin=False):
    existing_user = get_user(db, user.username)
    if existing_user:
        raise ValueError("Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username, hashed_password=hashed_password, is_admin=admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
