from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud import answers as answers_crud
from ..crud import participants as participants_crud
from ..crud import publications as publications_crud
from ..data import schemas
from ..data.database import get_db

router = APIRouter()


@router.post("/participants/", response_model=schemas.Participant)
async def create_participant(
    participant: schemas.ParticipantCreate, db: Session = Depends(get_db)
):
    try:
        db_participant = participants_crud.create_participant(db, participant)
        return db_participant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/participants/{participant_id}", response_model=schemas.Participant)
def read_participant(participant_id: int, db: Session = Depends(get_db)):
    return publications_crud.get_participant(db, participant_id)


@router.get(
    "/participants/{participant_id}/answers/", response_model=List[schemas.Answer]
)
def read_answers_by_participant(participant_id: int, db: Session = Depends(get_db)):
    return answers_crud.get_answers_by_participant(db, participant_id)
