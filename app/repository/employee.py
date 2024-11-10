from app.model import EmployeeModel
from app.repository.base import BaseRepository


class _EmployeeRepository(BaseRepository):
    def get_by_id(self, session, employee_id):
        return self.query(session).filter(self.model.id == employee_id)


EmployeeRepository = _EmployeeRepository(model=EmployeeModel)
