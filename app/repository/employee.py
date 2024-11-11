from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.model import EmployeeModel, VacationModel
from app.repository.base import BaseRepository
from app.schema import EmployeeSearchQuery


class _EmployeeRepository(BaseRepository):
    def search(self, session: Session, search_query: EmployeeSearchQuery):
        stmt = select(EmployeeModel).group_by(EmployeeModel.id)
        if search_query.last_name is not None:
            stmt = stmt.where(EmployeeModel.last_name == search_query.last_name)
        if search_query.first_name is not None:
            stmt = stmt.where(EmployeeModel.first_name == search_query.first_name)
        if (
            search_query.vacation_start is not None
            and search_query.vacation_end is not None
        ):
            stmt = stmt.join(VacationModel, EmployeeModel.id == VacationModel.user_id)
            # INFO: type isn't required
            if search_query.vacation_type is not None:
                stmt = stmt.where(
                    VacationModel.vacation_type == search_query.vacation_type
                )

            stmt = stmt.where(
                or_(
                    and_(
                        search_query.vacation_start <= VacationModel.start_date,
                        VacationModel.start_date <= search_query.vacation_end,
                    ),
                    and_(
                        search_query.vacation_start <= VacationModel.end_date,
                        VacationModel.end_date <= search_query.vacation_end,
                    ),
                )
            )
        return session.scalars(stmt).all()


EmployeeRepository = _EmployeeRepository(model=EmployeeModel)
