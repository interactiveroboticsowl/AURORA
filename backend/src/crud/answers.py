from typing import List, Optional

from sqlalchemy.orm import Session

from ..data import schemas
from ..data.models import Answer, Item, Page


def create_answer(db: Session, answer: schemas.AnswerCreate) -> Answer:
    db_answer = Answer(**answer.model_dump())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


def get_answer(db: Session, answer_id: int) -> Optional[Answer]:
    return db.query(Answer).filter(Answer.id == answer_id).first()


def update_answer(
    db: Session, answer_id: int, answer: schemas.AnswerUpdate
) -> Optional[Answer]:
    db_answer = get_answer(db, answer_id)
    if db_answer:
        update_data = answer.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_answer, key, value)
        db.commit()
        db.refresh(db_answer)
    return db_answer


def delete_answer(db: Session, answer_id: int) -> bool:
    db_answer = get_answer(db, answer_id)
    if db_answer:
        db.delete(db_answer)
        db.commit()
        return True
    return False


def get_answers_by_participant(db: Session, participant_id: int) -> List[Answer]:
    return db.query(Answer).filter(Answer.participant_id == participant_id).all()


def get_answers_by_item(db: Session, item_id: int) -> List[Answer]:
    return db.query(Answer).filter(Answer.item_id == item_id).all()


def get_answers_by_survey(db: Session, survey_id: int) -> List[Answer]:
    return (
        db.query(Answer).join(Item).join(Page).filter(Page.survey_id == survey_id).all()
    )


def get_latest_answer_by_participant_and_item(
    db: Session, participant_id: int, item_id: int
) -> Optional[Answer]:
    return (
        db.query(Answer)
        .filter(
            Answer.participant_id == participant_id,
            Answer.item_id == item_id,
        )
        .order_by(Answer.updated_at.desc())
        .first()
    )
