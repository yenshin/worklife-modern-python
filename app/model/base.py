import uuid as uid

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class BaseModel(MappedAsDataclass, DeclarativeBase):
    id: Mapped[uid.UUID] = mapped_column(
        postgresql.UUID,
        primary_key=True,
        index=True,
        nullable=False,
    )
