from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session

from app.model.employee import EmployeeModel
from app.model.vacation import VacationModel
from app.repository.base import BaseRepository
from app.schema import VacationRepresentationNoID


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

    def _remove_overlap_in_db(self, session: Session, vacation_ids: list[UUID]):
        session.execute(delete(VacationModel).where(VacationModel.id.in_(vacation_ids)))

    def _overlap_preparation(self, session: Session, obj_in: VacationModel):
        found_vacations = self._search_overlap(session, obj_in)
        to_delete = _prepare_overlap_merging(found_vacations, obj_in)
        self._remove_overlap_in_db(session, to_delete)

    def create(self, session: Session, obj_in: VacationModel):
        self._overlap_preparation(session, obj_in)
        session.add(obj_in)
        return obj_in

    def update(self, session: Session, id: UUID, obj_in: VacationRepresentationNoID):
        user_id = session.scalars(
            select(VacationModel.user_id).where(VacationModel.id == id)
        ).one()
        self.delete(session, id)
        session.flush()
        return self.create(
            session,
            VacationModel(
                id=id,
                user_id=user_id,
                vacation_type=obj_in.vacation_type,
                start_date=obj_in.start_date,
                end_date=obj_in.end_date,
            ),
        )


def _prepare_overlap_merging(
    found_vacations: Sequence[VacationModel], vacation_target: VacationModel
) -> list[UUID]:
    if len(found_vacations) == 0:
        return []
    true_begin = vacation_target.start_date
    true_end = vacation_target.end_date
    for vacation in found_vacations:
        if vacation.vacation_type != vacation_target.vacation_type:
            msg = "can't merge date of different type"
            raise ValueError(msg)
        if vacation.start_date <= true_begin <= vacation.end_date:
            true_begin = vacation.start_date
        if vacation.start_date <= true_end <= vacation.end_date:
            true_end = vacation.end_date
    vacation_target.start_date = true_begin
    vacation_target.end_date = true_end
    return [vacation.id for vacation in found_vacations]


VacationRepository = _VacationRepository(model=VacationModel)
