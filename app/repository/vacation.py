from datetime import datetime
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from pytest import Session
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.model.employee import EmployeeModel
from app.model.vacation import VacationModel
from app.repository.base import BaseRepository
from app.schema import VacationRepresentation, VacationRepresentationNoID


class _VacationRepository(BaseRepository):
    def _search_overlap(
        self, session: Session, vacation_target: VacationModel
    ) -> Sequence[VacationModel]:
        stmt = select(VacationModel)
        stmt = stmt.join(EmployeeModel, EmployeeModel.id == VacationModel.user_id)
        stmt = stmt.where(EmployeeModel.id == vacation_target.user_id)
        stmt = stmt.where(
            or_(
                and_(
                    vacation_target.start_date <= VacationModel.start_date,
                    VacationModel.start_date <= vacation_target.end_date,
                ),
                and_(
                    vacation_target.start_date <= VacationModel.end_date,
                    VacationModel.end_date <= vacation_target.end_date,
                ),
            )
        )
        return session.scalars(stmt).all()

    def _check_overlap(self, session: Session, vacation_target: VacationModel):
        found_vacations = self._search_overlap(session, vacation_target)
        true_begin = None
        true_end = None
        for vacation in found_vacations:
            if vacation.vacation_type != vacation_target.vacation_type:
                msg = "can't merge date of different type"
                raise Exception(msg)
            if true_begin is None:
                true_begin = vacation.start_date
            elif true_begin > vacation.start_date:
                true_begin = vacation.start_date
            if true_end is None:
                true_end = vacation.end_date
            elif true_end < vacation.end_date:
                true_end = vacation.start_date
        vacation_target.start_date = true_begin
        vacation_target.end_date = true_end
        session.remove_all(found_vacations)

    def create(self, session, obj_in):
        self._check_overlap(session, obj_in)
        session.add(obj_in)
        return obj_in

    def update(self, session, id: UUID, obj_in):
        self.delete(session, obj_in.id)
        return self.create(session, obj_in)


VacationRepository = _VacationRepository(model=VacationModel)
