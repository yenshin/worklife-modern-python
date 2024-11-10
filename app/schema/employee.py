from app.schema.base import BaseRepresentation


class EmployeeBase(BaseRepresentation):
    first_name: str
    last_name: str
