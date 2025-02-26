from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..crud import publications as publications_crud
from ..data.database import get_db
from ..data.models import Application
from ..tasks.tasks import deploy_task

router = APIRouter()


@router.post("/applications/{application_id}/deploy")
async def deploy_application(
    application_id: int,
    participant_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Check if the project and application exist
    db_application = (
        db.query(Application).filter(Application.id == application_id).first()
    )

    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    endpoints = publications_crud.get_endpoints(
        db, application_id=application_id, participant_id=participant_id
    )

    if not endpoints:
        raise HTTPException(
            status_code=404, detail="Endpoints not found for this application"
        )

    # Deploy the application
    background_tasks.add_task(
        deploy_task, db_application.project.name.lower(), str(participant_id)
    )
    return JSONResponse(content={"endpoints": endpoints})
