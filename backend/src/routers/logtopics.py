from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..data import schemas
from ..data.database import get_db
from ..data.models import LogTopic

router = APIRouter()


# LogTopic routes
@router.post("/logtopics/", response_model=schemas.LogTopic)
async def create_logtopic(
    logtopic: schemas.LogTopicCreate, db: Session = Depends(get_db)
):
    db_logtopic = LogTopic(**logtopic.model_dump())
    db.add(db_logtopic)
    db.commit()
    db.refresh(db_logtopic)
    return db_logtopic


@router.get("/logtopics/", response_model=List[schemas.LogTopic])
async def read_logtopics(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    logtopics = db.query(LogTopic).offset(skip).limit(limit).all()
    return logtopics
