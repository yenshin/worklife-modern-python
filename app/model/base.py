import uuid as uid

from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import as_declarative


class CustomUUID(postgresql.UUID):
    python_type = uid.UUID


@as_declarative()
class BaseModel:
    id = Column(
        postgresql.UUID,
        primary_key=True,
        index=True,
        default=uid.uuid4,
        nullable=False,
    )
