from datetime import datetime
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .enums import ItemType, QuestionType


class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ApplicationBase(BaseModel):
    ros_version: str


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    ros_version: Optional[str] = None
    build_version: Optional[int] = None


class Application(ApplicationBase):
    id: int
    project_id: int
    build_version: int

    model_config = ConfigDict(from_attributes=True)


class ApplicationWithStatus(Application):
    status: str


class RepoBase(BaseModel):
    git_url: str
    git_branch: str
    access_token: Optional[str] = None


class RepoCreate(RepoBase):
    pass


class Repo(RepoBase):
    id: int
    application_id: int

    model_config = ConfigDict(from_attributes=True)


class RepoUpdate(BaseModel):
    git_url: Optional[str] = None
    git_branch: Optional[str] = None
    access_token: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PortMapping(BaseModel):
    internal_port: int = Field(
        ..., gt=0, description="Container port must be a positive integer"
    )
    external_port: Optional[int] = Field(gt=0, description="Host port must be a positive integer", default=None)


class ContainerFormSchema(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, description="Name is required")
    dockerfile: str = Field(
        ..., min_length=1, description="Dockerfile path is required"
    )
    ports: List[PortMapping] = []


class ContainerCreate(ContainerFormSchema):
    pass


class ContainerBase(BaseModel):
    name: str
    dockerfile: str
    ports: Optional[List[PortMapping]]


class Container(ContainerBase):
    id: int
    application_id: int

    class Config:
        from_attributes = True


class LogTopicBase(BaseModel):
    topic: str
    application_id: int


class LogTopicCreate(LogTopicBase):
    pass


class LogTopic(LogTopicBase):
    id: int    

    model_config = ConfigDict(from_attributes=True)


# Extended models for nested relationships
class ProjectWithApplication(Project):
    application: Optional[Application]


class ApplicationWithRelations(Application):
    project: Project
    repo: Optional[Repo]
    containers: List[Container] = []
    log_topics: List[LogTopic] = []


class PublicationBase(BaseModel):
    name: str
    project_id: int
    application_only: bool
    start_date: datetime
    end_date: Optional[datetime] = None
    collect_data: bool
    redirect_url: Optional[str] = None
    allow_anonymous: bool


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(BaseModel):
    name: Optional[str] = None
    application_only: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    collect_data: Optional[bool] = None
    redirect_url: Optional[str] = None
    allow_anonymous: Optional[bool] = None


class Publication(PublicationBase):
    id: int
    link_uuid: UUID

    model_config = ConfigDict(from_attributes=True)


class ParticipantBase(BaseModel):
    external_id: Optional[str] = None
    external_survey_id: Optional[str] = None
    external_session_id: Optional[str] = None


class ParticipantCreate(ParticipantBase):
    pass


class Participant(ParticipantBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Base schema for all items
class ItemBase(BaseModel):
    title: Optional[str] = None  # Title for questions, text
    prompt: Optional[str] = None  # For questions or text content
    item_type: ItemType  # Defines the type (question, image, video, text)


# Schema for creating a new item
class ItemCreate(ItemBase):
    question_type: Optional[QuestionType] = (
        None  # Only relevant if item_type is "question"
    )
    options: Optional[List[str]] = None  # Multiple-choice options for questions
    scale_min: Optional[int] = None  # For scale questions
    scale_max: Optional[int] = None  # For scale questions
    statements: Optional[List[str]] = None  # For matrix scale questions
    matrix_options: Optional[List[str]] = None  # For matrix scale response options
    image_url: Optional[str] = None  # URL for image items
    video_url: Optional[str] = None  # URL for video items
    text_content: Optional[str] = None  # For static text or statement content


# Schema for updating an existing item
class ItemUpdate(ItemBase):
    question_type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    statements: Optional[List[str]] = None
    matrix_options: Optional[List[str]] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    text_content: Optional[str] = None


# Full schema for an item, used for reading
class Item(ItemBase):
    id: int
    question_type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    statements: Optional[List[str]] = None
    matrix_options: Optional[List[str]] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    text_content: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PageBase(BaseModel):
    name: str
    description: Optional[str] = None
    survey_id: int
    back_button_disabled: bool = False
    application_enabled: bool = False


class PageCreate(PageBase):
    items: Optional[List[int]] = []


class PageUpdate(PageBase):
    items: Optional[List[int]] = []


class Page(PageBase):
    id: int
    items: List[Item] = []
    order: int

    model_config = ConfigDict(from_attributes=True)


class PageItemOrderUpdate(BaseModel):
    id: int
    order: int


class PageAddItemRequest(BaseModel):
    item_id: int


class PageItemOrderUpdateList(BaseModel):
    items: List[PageItemOrderUpdate]


# Update Survey schemas to use Pages containing Items
class SurveyBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int


class SurveyCreate(SurveyBase):
    pass


class SurveyPut(SurveyBase):
    id: int


class SurveyUpdate(SurveyBase):
    pages: List[PageUpdate] = []


# Schema for a single survey answer
class SurveyAnswer(BaseModel):
    item_id: int  # Changed from question_id to item_id
    page_id: int
    answer: Union[
        str, int, dict
    ]  # Can be a string, number, or JSON (for matrix questions)


# Schema for submitting participant survey data
class ParticipantSurveySubmission(BaseModel):
    participant_id: int
    survey_id: int
    start_time: Optional[datetime] = None
    submit_time: Optional[datetime] = None
    answers: List[SurveyAnswer]


# Schema for reading participant survey data
class ParticipantSurvey(BaseModel):
    id: int
    participant_id: int
    survey_id: int
    start_time: datetime
    submit_time: Optional[datetime] = None
    answers: List[SurveyAnswer]

    model_config = ConfigDict(from_attributes=True)


class ItemResponse(BaseModel):
    id: int
    title: Optional[str]
    prompt: Optional[str]
    item_type: Optional[str]
    question_type: Optional[str]
    options: Optional[List[str]]
    scale_min: Optional[int]
    scale_max: Optional[int]
    statements: Optional[List[str]]
    matrix_options: Optional[List[str]]
    image_url: Optional[str]
    video_url: Optional[str]
    text_content: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ItemBase(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    item_type: Optional[ItemType] = None
    question_type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    statements: Optional[List[str]] = None
    matrix_options: Optional[List[str]] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    text_content: Optional[str] = None


class AnswerBase(BaseModel):
    participant_id: int
    item_id: int
    page_id: int
    value: Any  # Using Any to allow for flexible answer types


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int


class Survey(SurveyBase):
    id: int
    pages: List[Page] = []

    model_config = ConfigDict(from_attributes=True)


# Survey.model_rebuild()


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
