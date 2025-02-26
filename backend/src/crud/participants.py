from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.data import models, schemas


def create_participant(db: Session, participant: schemas.ParticipantCreate):
    db_participant = models.Participant(**participant.model_dump())
    db.add(db_participant)
    try:
        db.commit()
        db.refresh(db_participant)
    except IntegrityError:
        db.rollback()
        raise ValueError("A participant with these external fields already exists")
    return db_participant
