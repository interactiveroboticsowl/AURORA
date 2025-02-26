import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.crud import authentication as crud
from src.data import schemas
from src.data.database import get_db

router = APIRouter()


@router.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    is_first_user = not crud.check_admin_exists(db)

    return crud.create_user(db, user, admin=is_first_user)


@router.post("/auth/verify", response_model=schemas.User)
def verify_credentials(user: schemas.UserLogin, db: Session = Depends(get_db)):

    if user.username == os.getenv("ADMIN_USERNAME") and user.password == os.getenv(
        "ADMIN_PASSWORD"
    ):
        try:
            return crud.create_user(
                db,
                schemas.UserCreate(username=user.username, password=user.password),
                admin=True,
            )
        except ValueError:
            pass

    db_user = crud.get_user(db, user.username)

    if not db_user or not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return db_user
