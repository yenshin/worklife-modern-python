import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql as pgs
from sqlalchemy.orm import Mapped, mapped_column

from app.model.base import BaseModel
from app.model.employee import EmployeeModel


class VacationType(enum.Enum):
    UnpaidLeave = "UnpaidLeave"
    PaidLeave = "PaidLeave"


class VacationModel(BaseModel):
    __tablename__ = "vacation"
    user_id: Mapped[UUID] = mapped_column(
        pgs.UUID,
        ForeignKey(EmployeeModel.id, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    vacation_type: Mapped[VacationType] = mapped_column(
        pgs.ENUM(VacationType), index=True, nullable=False
    )
    # INFO: pgsql doesn't have a datetime column, so use timestamp
    start_date: Mapped[datetime] = mapped_column(
        pgs.TIMESTAMP, index=True, nullable=False
    )
    end_date: Mapped[datetime] = mapped_column(
        pgs.TIMESTAMP, index=True, nullable=False
    )
