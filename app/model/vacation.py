from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects import postgresql as pgs
import enum

from app.model.base import BaseModel
from app.model.employee import EmployeeModel


class VacationType(enum.Enum):
    UnpaidLeave = "UnpaidLeave"
    PaidLeave = "PaidLeave"


class VacationModel(BaseModel):
    __tablename__ = "vacation"
    user_id = Column(
        pgs.UUID,
        ForeignKey(EmployeeModel.id, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    vacation_type = Column(pgs.ENUM(VacationType), index=True, nullable=False)
    # INFO: pgsql doesn't have a datetime column, so use timestamp
    start_date = Column(pgs.TIMESTAMP, index=True, nullable=False)
    end_date = Column(pgs.TIMESTAMP, index=True, nullable=False)
