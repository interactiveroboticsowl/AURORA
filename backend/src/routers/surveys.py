import io
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from src.data.database import get_db as get_db

from ..crud import answers as answers_crud
from ..crud import items as items_crud
from ..crud import pages as pages_crud
from ..crud import surveys as surveys_crud
from ..data import schemas
from ..data.models import Answer, Item, Page, Survey
from ..utils.export import generate_csv

router = APIRouter()


@router.post("/surveys/", response_model=schemas.Survey)
def create_survey(survey: schemas.SurveyCreate, db: Session = Depends(get_db)):
    return surveys_crud.create_survey(db, survey)


@router.get("/surveys/{survey_id}", response_model=schemas.Survey)
def read_survey(survey_id: int, db: Session = Depends(get_db)):
    db_survey = surveys_crud.get_survey(db, survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey


@router.put("/surveys/{survey_id}", response_model=schemas.Survey)
def update_survey(
    survey_id: int, survey: schemas.SurveyUpdate, db: Session = Depends(get_db)
):
    db_survey = surveys_crud.update_survey(db, survey_id, survey)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey


@router.delete("/surveys/{survey_id}", response_model=bool)
def delete_survey(survey_id: int, db: Session = Depends(get_db)):
    success = surveys_crud.delete_survey(db, survey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Survey not found")
    return success


@router.delete("/surveys/{survey_id}/pages/{page_id}", response_model=bool)
def remove_page_from_survey(
    survey_id: int, page_id: int, db: Session = Depends(get_db)
):
    """
    Removes a page from a survey.
    """
    try:
        success = pages_crud.remove_page_from_survey(db, survey_id, page_id)
        if not success:
            raise HTTPException(status_code=404, detail="Page not found in the survey")
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/surveys/{survey_id}/pages/order", response_model=bool)
def reorder_pages_on_survey(
    survey_id: int,
    page_orders: List[schemas.PageItemOrderUpdate],
    db: Session = Depends(get_db),
):
    """
    Reorders pages within a survey.
    """
    try:
        pages_crud.reorder_pages_on_survey(db, survey_id, page_orders)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/surveys/{survey_id}/pages/", response_model=schemas.Page)
def create_page(
    survey_id: int, page: schemas.PageCreate, db: Session = Depends(get_db)
):
    db_survey = surveys_crud.get_survey(db, survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    page.survey_id = survey_id
    return pages_crud.create_page(db, page)


@router.get("/surveys/{survey_id}/pages/", response_model=List[schemas.Page])
def read_pages(survey_id: int, db: Session = Depends(get_db)):
    db_survey = surveys_crud.get_survey(db, survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return pages_crud.get_pages_by_survey(db, survey_id)


@router.get("/surveys/{survey_id}/answers/", response_model=List[schemas.Answer])
def read_answers_by_survey(survey_id: int, db: Session = Depends(get_db)):
    return answers_crud.get_answers_by_survey(db, survey_id)


from sqlalchemy.orm import joinedload


@router.get("/surveys/{survey_id}/export")
def export_survey(
    survey_id: int,
    format: str = Query(..., regex="^(csv|json)$"),
    db: Session = Depends(get_db),
):
    try:
        # Fetch survey with pages, items, and answers in a single query
        survey = (
            db.query(Survey)
            .options(
                joinedload(Survey.pages).joinedload(Page.items).joinedload(Item.answers)
            )
            .filter(Survey.id == survey_id)
            .first()
        )

        if survey is None:
            raise HTTPException(status_code=404, detail="Survey not found")

        # Convert to dict manually to control the depth and content
        survey_dict = {
            "id": survey.id,
            "title": survey.title,
            "description": survey.description,
            "pages": [],
        }

        for page in survey.pages:
            page_dict = {
                "id": page.id,
                "name": page.name,
                "description": page.description,
                "order": page.order,
                "items": [],
            }

            for item in page.items:
                item_dict = {
                    "id": item.id,
                    "title": getattr(item, "title", None),
                    "prompt": getattr(item, "prompt", None),
                    "item_type": getattr(item, "item_type", None),
                    "question_type": getattr(item, "question_type", None),
                    "options": getattr(item, "options", None),
                    "answers": [
                        {
                            "id": answer.id,
                            "value": answer.value,
                            "participant_id": answer.participant_id,
                            "created_at": (
                                answer.created_at.isoformat()
                                if answer.created_at
                                else None
                            ),
                            "updated_at": (
                                answer.updated_at.isoformat()
                                if answer.updated_at
                                else None
                            ),
                        }
                        for answer in item.answers
                    ],
                }
                page_dict["items"].append(item_dict)

            survey_dict["pages"].append(page_dict)

        logging.info(f"Exporting survey {survey_id} with answers")

        if format == "json":
            return JSONResponse(content=survey_dict)
        elif format == "csv":
            csv_content = generate_csv(survey_dict)
            filename = f"survey_{survey_id}_with_answers.csv"
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )
    except Exception as e:
        logging.error(f"Error exporting survey {survey_id}: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
