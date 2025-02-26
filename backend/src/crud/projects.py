from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from src.data import schemas

from ..data.models import Application, Container, PortMap, Project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()


def get_container(db: Session, container_id: int) -> Optional[Container]:
    return (
        db.query(Container)
        .options(joinedload(Container.ports))
        .filter(Container.id == container_id)
        .first()
    )


def delete_container(db: Session, container_id: int) -> bool:
    try:
        db_container = get_container(db, container_id)
        if db_container is None:
            return False
        db.delete(db_container)

        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        return False


def get_containers_by_project(db: Session, project_id: int) -> List[Container]:
    return (
        db.query(Container)
        .options(joinedload(Container.ports))
        .join(Application)
        .filter(Application.project_id == project_id)
        .all()
    )


def update_container(
    db: Session, container_id: int, container: schemas.ContainerFormSchema
) -> Optional[Container]:
    db_container = get_container(db, container_id)
    if db_container is None:
        return None

    for key, value in container.model_dump(exclude_unset=True).items():
        if key != "ports":
            setattr(db_container, key, value)

    if container.ports is not None:
        db.query(PortMap).filter(PortMap.container_id == container_id).delete()

        for port in container.ports:
            db_port = PortMap(container_id=container_id, **port.model_dump())
            db.add(db_port)

    db.commit()
    db.refresh(db_container)
    return db_container


def create_container_for_project(
    db: Session, container: schemas.ContainerFormSchema, project_id: int
) -> Optional[Container]:
    db_project = get_project(db, project_id)

    if db_project is None:
        return None

    db_application = db_project.application
    db_container = Container(
        application=db_application,
        **container.model_dump(exclude_unset=True, exclude={"ports"})
    )

    db.add(db_container)
    db.flush()

    for port in container.ports:
        db_port = PortMap(container=db_container, **port.model_dump())
        print(db_port)
        db.add(db_port)

    db.commit()
    db.refresh(db_container, ["ports"])
    return db_container
