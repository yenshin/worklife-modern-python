from app.model import EmployeeModel
from app.repository.base import BaseRepository
from sqlalchemy.orm import Session
from uuid import UUID


class _EmployeeRepository(BaseRepository):
    def get_by_id(self, session: Session, employee_id: UUID):
        return self.query(session).filter(self.model.id == employee_id)

    def create(self, session: Session, obj_in: EmployeeModel):
        session.add(obj_in)


EmployeeRepository = _EmployeeRepository(model=EmployeeModel)
