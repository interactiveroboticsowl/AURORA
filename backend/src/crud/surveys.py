from typing import Optional

from sqlalchemy.orm import Session

from ..data.models import Survey
from ..data import schemas


# Survey CRUD operations
def create_survey(db: Session, survey: schemas.SurveyCreate) -> Survey:
    db_survey = Survey(**survey.model_dump())
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


def get_survey(db: Session, survey_id: int) -> Optional[Survey]:
    return db.query(Survey).filter(Survey.id == survey_id).first()


def update_survey(
    db: Session, survey_id: int, survey: schemas.SurveyUpdate
) -> Optional[Survey]:
    db_survey = get_survey(db, survey_id)
    if db_survey:
        update_data = survey.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_survey, key, value)
        db.commit()
        db.refresh(db_survey)
    return db_survey


def delete_survey(db: Session, survey_id: int) -> bool:
    db_survey = get_survey(db, survey_id)
    if db_survey:
        db.delete(db_survey)
        db.commit()
        return True
    return False