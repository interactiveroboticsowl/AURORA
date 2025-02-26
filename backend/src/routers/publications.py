from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..crud import publications as publications_crud
from ..data import schemas
from ..data.database import get_db
from ..tasks.tasks import deploy_task

router = APIRouter()


@router.post("/publications/", response_model=schemas.PublicationCreate)
def create_publication(
    publication: schemas.PublicationCreate, db: Session = Depends(get_db)
):
    return publications_crud.create_publication(db=db, publication=publication)


@router.get("/publications/", response_model=List[schemas.Publication])
def read_publications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    publications = publications_crud.get_publications(db, skip=skip, limit=limit)
    return publications


@router.get("/publications/uuid/{link_uuid}", response_model=schemas.Publication)
def read_publication_by_uuid(link_uuid: str, db: Session = Depends(get_db)):
    db_publication = publications_crud.get_publication_by_uuid(db, link_uuid=link_uuid)
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    if not db_publication.is_active():
        raise HTTPException(status_code=403, detail="Publication not active")
    return db_publication


@router.get("/publications/{publication_id}", response_model=schemas.Publication)
def read_publication(publication_id: int, db: Session = Depends(get_db)):
    db_publication = publications_crud.get_publication(
        db, publication_id=publication_id
    )
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return db_publication


@router.put("/publications/{publication_id}", response_model=schemas.Publication)
def update_publication(
    publication_id: int,
    publication: schemas.PublicationUpdate,
    db: Session = Depends(get_db),
):
    db_publication = publications_crud.update_publication(
        db, publication_id=publication_id, publication=publication
    )
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return db_publication


@router.delete("/publications/{publication_id}", response_model=schemas.Publication)
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    db_publication = publications_crud.delete_publication(
        db, publication_id=publication_id
    )
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return db_publication


@router.get("/publications/{publication_id}/deploy/{participant_id}")
def deploy_publication(
    publication_id: int,
    participant_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_publication = publications_crud.get_publication(
        db, publication_id=publication_id
    )
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    if not db_publication.is_active():
        raise HTTPException(status_code=403, detail="Publication not active")
    db_participant = publications_crud.get_participant(
        db, participant_id=participant_id
    )
    if db_participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not db_publication.allow_anonymous and not db_participant.external_id:
        raise HTTPException(
            status_code=403, detail="This publication does not allow anonymous users"
        )
    endpoints = publications_crud.get_endpoints(
        db,
        application_id=db_publication.project.application.id,
        participant_id=db_participant.id,
    )
    if not endpoints:
        raise HTTPException(
            status_code=404, detail="Endpoints not found for this publication"
        )
    background_tasks.add_task(
        deploy_task, db_publication.project.name.lower(), str(db_participant.id)
    )
    return JSONResponse(content={"endpoints": endpoints})
