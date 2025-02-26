import logging
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from minio import Minio
import minio
from sqlalchemy.orm import Session
from src.crud import projects as crud

from ..data import schemas
from ..data.database import get_db
from ..data.models import (
    Application,
    Project,
    Publication,
    Repo,
    Survey,
)
from ..utils.kubernetes import get_application_status

router = APIRouter()

OBJECT_DOWNLOAD_CHUNK_SIZE = 1024 * 1024 * 2  # 2 mb
SSL_ISSUER = os.getenv("SSL_ISSUER")
MINIO_USER = os.getenv("MINIO_USER")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")


# Project routes
@router.post("/projects/", response_model=schemas.Project)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.flush()

    db_application = Application(project_id=db_project.id, ros_version="1")
    db.add(db_application)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects/", response_model=List[schemas.Project])
async def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects


@router.get("/projects/{project_id}", response_model=schemas.Project)
async def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# Application routes
@router.post("/projects/{project_id}/application", response_model=schemas.Application)
async def create_application(
    project_id: int,
    application: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    existing_application = (
        db.query(Application).filter(Application.project_id == project_id).first()
    )
    if existing_application:
        raise HTTPException(
            status_code=400, detail="An application already exists for this project"
        )

    db_application = Application(**application.model_dump(), project_id=project_id)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get(
    "/projects/{project_id}/publications", response_model=List[schemas.Publication]
)
async def read_project_publications(project_id: int, db: Session = Depends(get_db)):
    publications = (
        db.query(Publication).filter(Publication.project_id == project_id).all()
    )
    return publications


@router.patch("/projects/{project_id}/application", response_model=schemas.Application)
async def patch_project_application(
    project_id: int,
    application: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
):
    db_application = (
        db.query(Application).filter(Application.project_id == project_id).first()
    )
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    logging.error(application.model_dump(exclude_unset=True))

    update_data = application.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_application, key, value)

    db.commit()
    db.refresh(db_application)
    return db_application


@router.get(
    "/projects/{project_id}/application", response_model=schemas.ApplicationWithStatus
)
async def read_project_application(project_id: int, db: Session = Depends(get_db)):
    application = (
        db.query(Application).filter(Application.project_id == project_id).first()
    )

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    application_status = get_application_status(
        f"project-{application.project.name.lower()}", ""
    )

    application_with_status = schemas.ApplicationWithStatus(
        id=application.id,
        project_id=application.project_id,
        ros_version=application.ros_version,
        build_version=application.build_version,
        status=application_status,
    )
    return application_with_status


@router.put("/projects/{project_id}/application", response_model=schemas.Application)
async def update_project_application(
    project_id: int,
    application: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
):
    db_application = (
        db.query(Application).filter(Application.project_id == project_id).first()
    )
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = application.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_application, key, value)

    db.commit()
    db.refresh(db_application)
    return db_application


@router.get(
    "/projects/{project_id}/application/containers",
    response_model=List[schemas.Container],
)
async def read_application_containers(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_containers_by_project(db, project_id)


@router.get(
    "/projects/{project_id}/application/containers/{container_id}",
    response_model=schemas.Container,
)
async def read_container(
    project_id: int, container_id: int, db: Session = Depends(get_db)
):
    db_container = crud.get_container(db, container_id)
    if db_container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return db_container


@router.delete(
    "/projects/{project_id}/application/containers/{container_id}", status_code=204
)
async def delete_container(
    project_id: int, container_id: int, db: Session = Depends(get_db)
):
    result = crud.delete_container(db, container_id)
    if not result:
        raise HTTPException(status_code=404, detail="Container not found")
    return result


# Repo routes
@router.post("/projects/{project_id}/repo", response_model=schemas.Repo)
async def create_project_repo(
    project_id: int,
    repo: schemas.RepoCreate,
    db: Session = Depends(get_db),
):
    logging.error(repo.model_dump())
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    existing_repo = (
        db.query(Repo)
        .join(Application)
        .filter(Application.project_id == project_id)
        .first()
    )
    if existing_repo:
        raise HTTPException(
            status_code=400, detail="A repository already exists for this project"
        )

    db_application = (
        db.query(Application).filter(Application.project_id == project_id).first()
    )
    if db_application is None:
        raise HTTPException(
            status_code=404, detail="Application not found for this project"
        )

    db_repo = Repo(**repo.model_dump(), application=db_application)
    db.add(db_repo)
    db.flush()
    logging.error(
        f"Created repo {db_repo.id} with application_id {db_repo.application_id}"
    )
    db.commit()
    db.refresh(db_repo)
    return db_repo


@router.get("/projects/{project_id}/repo", response_model=schemas.Repo)
async def read_project_repo(project_id: int, db: Session = Depends(get_db)):
    db_repo = (
        db.query(Repo)
        .join(Application)
        .filter(Application.project_id == project_id)
        .first()
    )
    if db_repo is None:
        raise HTTPException(
            status_code=404, detail="Repository not found for this project"
        )
    return db_repo


@router.put("/projects/{project_id}/repo", response_model=schemas.Repo)
async def update_project_repo(
    project_id: int,
    repo: schemas.RepoUpdate,
    db: Session = Depends(get_db),
):
    db_repo = (
        db.query(Repo)
        .join(Application)
        .filter(Application.project_id == project_id)
        .first()
    )
    if db_repo is None:
        raise HTTPException(
            status_code=404, detail="Repository not found for this project"
        )

    update_data = repo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_repo, key, value)

    db.commit()
    db.refresh(db_repo)
    return db_repo


@router.post(
    "/projects/{project_id}/application/containers/", response_model=schemas.Container
)
async def create_container(
    project_id: int,
    container: schemas.ContainerFormSchema,
    db: Session = Depends(get_db),
):
    result = crud.create_container_for_project(db, container, project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.put(
    "/projects/{project_id}/application/containers/{container_id}",
    response_model=schemas.Container,
)
async def update_container(
    project_id: int,
    container_id: int,
    container: schemas.ContainerFormSchema,
    db: Session = Depends(get_db),
):
    result = crud.update_container(db, container_id, container)
    if result is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return result


@router.post("/projects/{project_id}/survey", response_model=schemas.Survey)
async def create_project_survey(
    project_id: int,
    survey: schemas.SurveyBase,
    db: Session = Depends(get_db),
):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    existing_survey = db.query(Survey).filter(Survey.project_id == project_id).first()
    if existing_survey:
        raise HTTPException(
            status_code=400, detail="An application already exists for this project"
        )

    db_survey = Survey(**survey.model_dump(), project_id=project_id)
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


@router.get("/projects/{project_id}/survey", response_model=schemas.Survey)
async def get_project_survey(project_id: int, db: Session = Depends(get_db)):
    db_survey = db.query(Survey).filter(Survey.project_id == project_id).first()
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found for this project")
    return db_survey


@router.put("/projects/{project_id}/survey", response_model=schemas.Survey)
async def update_project_survey(
    project_id: int,
    survey: schemas.SurveyUpdate,
    db: Session = Depends(get_db),
):
    db_survey = db.query(Survey).filter(Survey.project_id == project_id).first()
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = survey.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_survey, key, value)

    db.commit()
    db.refresh(db_survey)
    return db_survey


@router.get("/projects/{project_id}/rosbag")
def list_project_rosbag_data(project_id: int, db: Session = Depends(get_db)):
    client = Minio(
        "myminio-hl.minio-tenant.svc.cluster.local:9000",
        MINIO_USER,
        MINIO_PASSWORD,
        secure=True,
        cert_check=False,
    )

    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        objects = client.list_objects(
            "rosbags",
            prefix=f"{project.name}/",
            recursive=True,
        )
    except minio.error.S3Error as e:
        logging.warning("Error retrieving list of s3 objects. Does the prefix exist?")
        logging.warning(e)
        return HTTPException(status_code=404, detail="No objects found.")

    return [obj.object_name for obj in objects]


@router.get("/storage/download/{object_path:path}", response_class=StreamingResponse)
def get_storage_object_data(object_path: str):
    client = Minio(
        "myminio-hl.minio-tenant.svc.cluster.local:9000",
        MINIO_USER,
        MINIO_PASSWORD,
        secure=True,
        cert_check=False,
    )

    # test first chunk
    object_response = client.get_object(
        "rosbags", object_name=object_path, length=OBJECT_DOWNLOAD_CHUNK_SIZE
    )

    if object_response.status == 404:
        return HTTPException(status_code=404, detail=f"Object {object_path} not found")    

    def iterfile():
        object_response = client.get_object(
            "rosbags", object_name=object_path
        )
        yield from object_response

    # def iterfile():
    #     offset = 0

    #     while True:
    #         object_response = client.get_object(
    #             "rosbags",
    #             object_name=object_path,
    #             offset=offset,
    #             length=offset + OBJECT_DOWNLOAD_CHUNK_SIZE,
    #         )
    #         offset += OBJECT_DOWNLOAD_CHUNK_SIZE

    #         if object_response.status == 206 or object_response.status == 416:
    #             break

    #         yield object_response.data

    object_name = object_path.replace("/", "_")    

    headers = {"Content-Disposition": f"attachment; filename={object_name}"}
    return StreamingResponse(
        iterfile(), headers=headers, media_type="application/octet-stream"
    )
