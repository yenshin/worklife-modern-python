import uuid

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.vacation import VacationRepository
from app.schema.vacation import VacationRepresentation, VacationRepresentationNoID

router = APIRouter()


@router.get("/{vacation_id}")
def get_vacation(
    session: Session = Depends(get_db), *, vacation_id: uuid.UUID
) -> VacationRepresentation:
    return VacationRepository.get(session=session, id=vacation_id)


@router.put("/{vacation_id}")
def update_vacation(
    session: Session = Depends(get_db),
    *,
    vacation_id: uuid.UUID,
    representation: VacationRepresentationNoID,
) -> VacationRepresentation:
    return VacationRepository.update(
        session=session, id=vacation_id, obj_in=representation
    )


@router.delete("/{vacation_id}")
def delete_vacation(session: Session = Depends(get_db), *, vacation_id: uuid.UUID):
    VacationRepository.delete(session=session, id=vacation_id)
