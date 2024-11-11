from app.schema.base import BaseRepresentation
from app.model.vacation import VacationType
from datetime import datetime
from pydantic import model_validator
from typing_extensions import Self
from pydantic import BaseModel


class VacationRepresentationNoID(BaseModel):
    vacation_type: VacationType
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.start_date.weekday() > 5 or self.end_date.weekday() > 5:
            raise ValueError("date should not be in the weekend")
        if self.end_date < self.start_date:
            raise ValueError("end date should terminate after begin")
        return self


class VacationRepresentation(BaseRepresentation, VacationRepresentationNoID): ...
