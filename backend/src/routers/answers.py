from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud import answers as answers_crud
from ..data import schemas
from ..data.database import get_db

router = APIRouter()


@router.post("/answers/", response_model=schemas.Answer)
def create_answer(answer: schemas.AnswerCreate, db: Session = Depends(get_db)):
    return answers_crud.create_answer(db, answer)


@router.get("/answers/{answer_id}", response_model=schemas.Answer)
def read_answer(answer_id: int, db: Session = Depends(get_db)):
    db_answer = answers_crud.get_answer(db, answer_id)
    if db_answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    return db_answer


@router.put("/answers/{answer_id}", response_model=schemas.Answer)
def update_answer(
    answer_id: int, answer: schemas.AnswerUpdate, db: Session = Depends(get_db)
):
    db_answer = answers_crud.update_answer(db, answer_id, answer)
    if db_answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    return db_answer


@router.delete("/answers/{answer_id}", response_model=bool)
def delete_answer(answer_id: int, db: Session = Depends(get_db)):
    success = answers_crud.delete_answer(db, answer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Answer not found")
    return success
