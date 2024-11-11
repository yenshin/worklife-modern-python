from dataclasses import dataclass
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.model.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


@dataclass
class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def _query(self, session: Session, *_, **kwargs):
        filters = [getattr(self.model, k) == v for k, v in kwargs.items()]
        return session.query(self.model).filter(*filters)

    def get(self, session: Session, *_, **kwargs):
        return self._query(session, **kwargs).one_or_none()

    def get_many(self, session: Session, *_, **kwargs):
        return self._query(session, **kwargs).all()

    def create(self, session: Session, obj_in: ModelType):
        session.add(obj_in)
        return obj_in

    def delete(self, session: Session, id: UUID):
        session.delete(self.get(session, id=id))
