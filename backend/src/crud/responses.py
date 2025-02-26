from sqlalchemy.orm import Session

from ..data import schemas
from ..data.models import ParticipantSurvey, SurveyAnswer


def create_participant_survey(
    db: Session, survey_data: schemas.ParticipantSurveySubmission
):
    # Create the participant survey entry
    db_participant_survey = ParticipantSurvey(
        participant_id=survey_data.participant_id,
        survey_id=survey_data.survey_id,
        start_time=survey_data.start_time,
        submit_time=survey_data.submit_time,
    )
    db.add(db_participant_survey)
    db.commit()
    db.refresh(db_participant_survey)

    # Loop through and create survey answers
    for answer in survey_data.answers:
        db_survey_answer = SurveyAnswer(
            participant_survey_id=db_participant_survey.id,
            item_id=answer.item_id,  # Changed from question_id to item_id
            page_id=answer.page_id,
            answer=answer.answer,
        )
        db.add(db_survey_answer)

    db.commit()
    return db_participant_survey


def get_participant_surveys(db: Session, participant_id: int):
    # Retrieve all participant surveys for the given participant
    return (
        db.query(ParticipantSurvey)
        .filter(ParticipantSurvey.participant_id == participant_id)
        .all()
    )
