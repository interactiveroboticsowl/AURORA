import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.sql import func

from .database import DBDeclarativeBase as Base

# Association Table for Many-to-Many Relationship with Order
page_item_association = Table(
    "page_item_association",
    Base.metadata,
    Column("page_id", Integer, ForeignKey("pages.id"), primary_key=True),
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("order", Integer, nullable=False),
)


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, nullable=True)
    external_survey_id = Column(String, nullable=True)
    external_session_id = Column(String, nullable=True)
    answers = relationship("Answer", back_populates="participant")

    __table_args__ = (
        UniqueConstraint(
            "external_id",
            "external_survey_id",
            "external_session_id",
            name="uq_participant_external_fields",
        ),
    )


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    application = relationship("Application", back_populates="project", uselist=False, cascade="all, delete")
    survey = relationship("Survey", back_populates="project", uselist=False)
    publications = relationship("Publication", back_populates="project")


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    application_only = Column(Boolean, nullable=False, default=False)
    collect_data = Column(Boolean, nullable=False, default=False)
    link_uuid = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    redirect_url = Column(String, nullable=True)
    allow_anonymous = Column(Boolean, nullable=False, default=False)

    project = relationship("Project", back_populates="publications")

    def is_active(self) -> bool:
        now = datetime.now().date()
        if now < self.start_date.date():
            return False
        if self.end_date is not None and now > self.end_date.date():
            return False
        return True


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    ros_version = Column(Enum("1", "2"), nullable=False)
    project = relationship("Project", back_populates="application")
    repo = relationship("Repo", back_populates="application", uselist=False,cascade="all, delete")
    containers = relationship("Container", back_populates="application", cascade="all, delete")
    log_topics = relationship("LogTopic", back_populates="application", cascade="all, delete")
    build_version = Column(Integer, nullable=False, default=0)


class Repo(Base):
    __tablename__ = "repos"
    id = Column(Integer, primary_key=True)
    application_id = Column(
        Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    git_url = Column(String, nullable=False)
    git_branch = Column(String, nullable=False)
    access_token = Column(String)
    application = relationship("Application", back_populates="repo")


class Container(Base):
    __tablename__ = "containers"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    dockerfile = Column(String, nullable=False)
    application = relationship("Application", back_populates="containers")
    ports = relationship("PortMap", back_populates="container", cascade="all, delete")


class PortMap(Base):
    __tablename__ = "port_maps"
    id = Column(Integer, primary_key=True)
    container_id = Column(Integer, ForeignKey("containers.id", ondelete="CASCADE"), nullable=False)
    internal_port = Column(Integer, nullable=False)
    external_port = Column(Integer)
    container = relationship("Container", back_populates="ports")


class LogTopic(Base):
    __tablename__ = "log_topics"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String, nullable=False)
    application = relationship("Application", back_populates="log_topics")


class ParticipantSurvey(Base):
    __tablename__ = "participant_surveys"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, nullable=False)
    survey_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, default=func.now())
    submit_time = Column(DateTime, nullable=True)

    answers = relationship(
        "SurveyAnswer",
        back_populates="participant_survey",
        cascade="all, delete-orphan",
    )


class SurveyAnswer(Base):
    __tablename__ = "survey_answers"

    id = Column(Integer, primary_key=True, index=True)
    participant_survey_id = Column(
        Integer, ForeignKey("participant_surveys.id"), nullable=False
    )
    item_id = Column(Integer, nullable=False)
    page_id = Column(Integer, nullable=False)
    answer = Column(JSON, nullable=True)
    submit_time = Column(DateTime, default=func.now())

    participant_survey = relationship("ParticipantSurvey", back_populates="answers")


class ItemTemplate(Base):
    __tablename__ = "item_templates"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    item_type = Column(String, nullable=False)
    question_type = Column(String, nullable=True)
    options = Column(JSON, nullable=True)
    scale_min = Column(Integer, nullable=True)
    scale_max = Column(Integer, nullable=True)
    statements = Column(JSON, nullable=True)
    matrix_options = Column(JSON, nullable=True)
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    text_content = Column(Text, nullable=True)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("item_templates.id"), nullable=True)

    pages = relationship(
        "Page", secondary=page_item_association, back_populates="items"
    )
    answers = relationship("Answer", back_populates="item")

    @declared_attr
    def title(cls):
        return Column(String, nullable=True)

    @declared_attr
    def prompt(cls):
        return Column(Text, nullable=True)

    @declared_attr
    def item_type(cls):
        return Column(String, nullable=True)

    @declared_attr
    def question_type(cls):
        return Column(String, nullable=True)

    @declared_attr
    def options(cls):
        return Column(JSON, nullable=True)

    @declared_attr
    def scale_min(cls):
        return Column(Integer, nullable=True)

    @declared_attr
    def scale_max(cls):
        return Column(Integer, nullable=True)

    @declared_attr
    def statements(cls):
        return Column(JSON, nullable=True)

    @declared_attr
    def matrix_options(cls):
        return Column(JSON, nullable=True)

    @declared_attr
    def image_url(cls):
        return Column(String, nullable=True)

    @declared_attr
    def video_url(cls):
        return Column(String, nullable=True)

    @declared_attr
    def text_content(cls):
        return Column(Text, nullable=True)

    template = relationship("ItemTemplate")

    def __getattribute__(self, name):
        if name in (
            "title",
            "prompt",
            "item_type",
            "question_type",
            "options",
            "scale_min",
            "scale_max",
            "statements",
            "matrix_options",
            "image_url",
            "video_url",
            "text_content",
        ):
            value = super().__getattribute__(name)
            if value is None:
                return getattr(self.template, name)
            return value
        return super().__getattribute__(name)


class Survey(Base):
    __tablename__ = "surveys"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    pages = relationship(
        "Page",
        back_populates="survey",
        order_by="Page.order",
        cascade="all, delete-orphan",
    )
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    project = relationship("Project", back_populates="survey")


class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    survey = relationship("Survey", back_populates="pages")
    items = relationship(
        "Item",
        secondary=page_item_association,
        back_populates="pages",
        order_by=page_item_association.c.order,
    )
    back_button_disabled = Column(Boolean, default=False, nullable=False)
    application_enabled = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, nullable=False)
    answers = relationship("Answer", back_populates="page")


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    value = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    page = relationship("Page", back_populates="answers")
    participant = relationship("Participant", back_populates="answers")
    item = relationship("Item", back_populates="answers")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
