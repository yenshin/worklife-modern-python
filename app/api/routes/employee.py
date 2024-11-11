import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.model import EmployeeModel, VacationModel
from app.repository.employee import EmployeeRepository
from app.repository.vacation import VacationRepository
from app.schema import EmployeeRepresentation, EmployeeSearchQuery
from app.schema.vacation import VacationRepresentation

router = APIRouter()


@router.get("/")
def get_employees(
    session: Session = Depends(get_db),
    *,
    search_query: Annotated[EmployeeSearchQuery, Query()],
) -> Sequence[EmployeeRepresentation]:
    return [
        EmployeeRepresentation.model_validate(employee)
        for employee in EmployeeRepository.search(
            session=session, search_query=search_query
        )
    ]


@router.get("/{employee_id}")
def get_employee(
    session: Session = Depends(get_db), *, employee_id: uuid.UUID
) -> EmployeeRepresentation:
    return EmployeeRepresentation.model_validate(
        EmployeeRepository.get(session=session, id=employee_id)
    )


@router.post("/")
def create_employee(
    session: Session = Depends(get_db), *, representation: EmployeeRepresentation
) -> EmployeeRepresentation:
    model = EmployeeModel(
        id=representation.id or uuid.uuid4(),
        last_name=representation.last_name,
        first_name=representation.first_name,
    )
    return EmployeeRepresentation.model_validate(
        EmployeeRepository.create(session=session, obj_in=model)
    )


@router.post("/{employee_id}/vacation")
def create_employee_vacation(
    session: Session = Depends(get_db),
    *,
    employee_id: uuid.UUID,
    representation: VacationRepresentation,
) -> VacationRepresentation:
    employee = EmployeeRepository.get(session=session, id=employee_id)
    if employee is None:
        msg = "Employee not found"
        raise HTTPException(status.HTTP_404_NOT_FOUND, msg)
    model = VacationModel(
        id=representation.id or uuid.uuid4(),
        user_id=employee_id,
        vacation_type=representation.vacation_type,
        start_date=representation.start_date,
        end_date=representation.end_date,
    )
    return VacationRepresentation.model_validate(
        VacationRepository.create(session=session, obj_in=model)
    )
