from typing import Optional
from uuid import UUID, uuid4

from kubernetes.client.api_client import os
from kubernetes.client.configuration import logging
from sqlalchemy.orm import Session

from ..data import models, schemas

DOMAIN = os.getenv("DOMAIN")


def get_endpoints(db: Session, application_id: int, participant_id: int) -> list[str]:
    db_application = (
        db.query(models.Application)
        .filter(models.Application.id == application_id)
        .first()
    )

    db_participant = (
        db.query(models.Participant)
        .filter(models.Participant.id == participant_id)
        .first()
    )

    endpoints = []
    logging.info(db_application.containers)
    for container in db_application.containers:
        for port_mapping in container.ports:
            if (
                port_mapping.internal_port == 8080
                or port_mapping.internal_port == "8080"
                or port_mapping.internal_port == 80
                or port_mapping.internal_port == "80"
                or port_mapping.internal_port == 8000
                or port_mapping.internal_port == "8000"
            ):
                endpoints.append(
                    f"{db_participant.id}{container.name}{port_mapping.internal_port}.{DOMAIN}"
                )
    return endpoints


def get_participant(db: Session, participant_id: int) -> Optional[models.Participant]:
    return (
        db.query(models.Participant)
        .filter(models.Participant.id == participant_id)
        .first()
    )


def create_publication(db: Session, publication: schemas.PublicationCreate):
    db_publication = models.Publication(**publication.model_dump(), link_uuid=uuid4())
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return db_publication


def get_publication(db: Session, publication_id: int):
    return (
        db.query(models.Publication)
        .filter(models.Publication.id == publication_id)
        .first()
    )


def get_publication_by_uuid(db: Session, link_uuid: str):
    link_uuid_obj = UUID(link_uuid)
    return (
        db.query(models.Publication)
        .filter(models.Publication.link_uuid == link_uuid_obj)
        .first()
    )


def get_publications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Publication).offset(skip).limit(limit).all()


def update_publication(
    db: Session, publication_id: int, publication: schemas.PublicationUpdate
):
    db_publication = (
        db.query(models.Publication)
        .filter(models.Publication.id == publication_id)
        .first()
    )
    if db_publication:
        update_data = publication.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_publication, key, value)
        db.commit()
        db.refresh(db_publication)
    return db_publication


def delete_publication(db: Session, publication_id: int):
    db_publication = (
        db.query(models.Publication)
        .filter(models.Publication.id == publication_id)
        .first()
    )
    if db_publication:
        db.delete(db_publication)
        db.commit()
    return db_publication
