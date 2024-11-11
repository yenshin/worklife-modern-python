from app.schema.base import BaseRepresentation


class EmployeeRepresentation(BaseRepresentation):
    first_name: str
    last_name: str
