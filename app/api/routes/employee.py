from typing import Optional
import uuid

from fastapi import (
    Depends,
    APIRouter,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repository.employee import EmployeeRepository
from app.schema import EmployeeBase
from app.model import EmployeeModel

router = APIRouter()


@router.get("/{employee_id}", response_model=Optional[EmployeeBase])
def get_employee(session: Session = Depends(get_db), *, employee_id: uuid.UUID):
    return EmployeeRepository.get(session=session, id=employee_id)


@router.post("/", response_model=Optional[EmployeeBase])
def create_employee(
    session: Session = Depends(get_db), *, first_name: str, last_name: str
):
    model = EmployeeModel(id=uuid.uuid4(), last_name=last_name, first_name=first_name)
    EmployeeRepository.create(session=session, obj_in=model)

    return model
