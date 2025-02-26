import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .data.database import engine_db
from .data.models import Base
from .routers.answers import router as answers_router
from .routers.applications import router as applications_router
from .routers.authentication import router as authentication_router
from .routers.items import router as items_router
from .routers.logtopics import router as logtopics_router
from .routers.pages import router as pages_router
from .routers.participants import router as participants_router
from .routers.projects import router as projects_router
from .routers.publications import router as publications_router
from .routers.surveys import router as surveys_router

load_dotenv()
if os.getenv("ENVIRONMENT") == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")


DOMAIN = os.getenv("DOMAIN")

# Initialize database
Base.metadata.create_all(bind=engine_db)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"*.{DOMAIN}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(answers_router, prefix="/api", tags=["answers"])
app.include_router(applications_router, prefix="/api", tags=["applications"])
app.include_router(items_router, prefix="/api", tags=["items"])
app.include_router(logtopics_router, prefix="/api", tags=["logtopics"])
app.include_router(pages_router, prefix="/api", tags=["pages"])
app.include_router(participants_router, prefix="/api", tags=["participants"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(publications_router, prefix="/api", tags=["publications"])
app.include_router(surveys_router, prefix="/api", tags=["surveys"])
app.include_router(authentication_router, prefix="/api", tags=["authentication"])

# TODO: woanders?!
# @app.post("/cleanup")
# async def cleanup(
#     background_tasks: BackgroundTasks,
#     user_id: str,
#     survey_name: str,
# ):
#     if user_id is None:
#         return JSONResponse({"message": "invalid session"}, status_code=400)

#     background_tasks.add_task(cleanup_task, user_id, survey_name)
#     return True
