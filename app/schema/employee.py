from datetime import datetime
from typing import Self

from pydantic import BaseModel, model_validator

from app.model.vacation import VacationType
from app.schema.base import BaseRepresentation


class EmployeeRepresentation(BaseRepresentation):
    first_name: str
    last_name: str


class EmployeeSearchQuery(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    vacation_type: VacationType | None = None
    vacation_start: datetime | None = None
    vacation_end: datetime | None = None

    @model_validator(mode="after")
    def check_vacation_query_parameter(self) -> Self:
        if self.vacation_type is not None and (
            self.vacation_start is None or self.vacation_end is None
        ):
            raise ValueError("if vacation, both date must be specified")
        if (self.vacation_start is None and self.vacation_end is not None) or (
            self.vacation_start is not None and self.vacation_end is None
        ):
            raise ValueError("if vacation, both date must be specified")
        return self
