import os
from typing import Iterable

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import RelationshipProperty, sessionmaker

from ..utils.sqlalchemy import classproperty

if os.getenv("KUBERNETES_PORT"):
    SQLALCHEMY_DATABASE_URL = "sqlite:////db/survey_platform.db?check_same_thread=False"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./survey_platform.db?check_same_thread=False"
engine_db = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocalSurveyDesign = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_db
)


# taken from https://github.com/absent1706/sqlalchemy-mixins/blob/master/sqlalchemy_mixins/serialize.py, MIT
class DBDeclarativeBase(declarative_base()):
    __abstract__ = True

    @classproperty
    def columns(cls):
        return inspect(cls).columns.keys()

    @classproperty
    def relations(cls):
        """Return a `list` of relationship names or the given model"""
        return [
            c.key for c in cls.__mapper__.attrs if isinstance(c, RelationshipProperty)
        ]

    @classproperty
    def hybrid_properties(cls):
        items = inspect(cls).all_orm_descriptors
        return [item.__name__ for item in items if isinstance(item, hybrid_property)]

    def to_dict(self, nested=False, hybrid_attributes=False, exclude=None):
        """Return dict object with model's data.

        :param nested: flag to return nested relationships' data if true
        :type: bool
        :param hybrid_attributes: flag to include hybrid attributes if true
        :type: bool
        :return: dict
        """
        result = dict()

        if exclude is None:
            view_cols = self.columns
        else:
            view_cols = filter(lambda e: e not in exclude, self.columns)

        for key in view_cols:
            result[key] = getattr(self, key)

        if hybrid_attributes:
            for key in self.hybrid_properties:
                result[key] = getattr(self, key)

        if nested:
            for key in self.relations:
                obj = getattr(self, key)

                if isinstance(obj, DBDeclarativeBase):
                    result[key] = obj.to_dict(hybrid_attributes=hybrid_attributes)
                elif isinstance(obj, Iterable):
                    result[key] = [
                        o.to_dict(hybrid_attributes=hybrid_attributes)
                        for o in obj
                        if isinstance(o, DBDeclarativeBase)
                    ]

        return result


def get_db():
    db = SessionLocalSurveyDesign()
    try:
        yield db
    finally:
        db.close()
