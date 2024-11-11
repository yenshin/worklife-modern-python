from app.model.vacation import VacationModel
from app.repository.base import BaseRepository
from uuid import UUID


class _VacationRepository(BaseRepository):
    def update(self, session, id: UUID, obj_in):
        data = self.get(session, id=id)
        data.vacation_type = obj_in.vacation_type
        data.start_date = obj_in.start_date
        data.end_date = obj_in.end_date
        return data


VacationRepository = _VacationRepository(model=VacationModel)
