import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.model.base import BaseModel


class EmployeeModel(BaseModel):
    __tablename__ = "employee"

    first_name: Mapped[str] = mapped_column(sa.String)
    last_name: Mapped[str] = mapped_column(sa.String)
