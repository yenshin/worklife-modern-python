import json
import uuid
from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.model.vacation import VacationType
from app.repository.employee import EmployeeRepository
from app.repository.vacation import VacationRepository
from app.schema import VacationRepresentation, VacationRepresentationNoID


@pytest.fixture
def api_app():
    from app.main import app

    return app


@pytest.fixture
def api_client(api_app):
    return TestClient(api_app)


@pytest.fixture
def db_session():
    yield from get_db()


def test_create_employee(db_session, api_client):
    username01 = "user" + uuid.uuid4().hex.upper()[0:6]
    username02 = "user" + uuid.uuid4().hex.upper()[0:6]
    username03 = "user" + uuid.uuid4().hex.upper()[0:6]
    username04 = "user" + uuid.uuid4().hex.upper()[0:6]
    usernames = [username01, username02, username03, username04]
    users = []
    for user in usernames:
        resp = api_client.post(
            "/employee", json={"first_name": f"F{user}", "last_name": f"L{user}"}
        )
        assert resp.status_code == status.HTTP_200_OK
        json_val = resp.json()
        assert json_val["first_name"] == f"F{user}"
        assert json_val["last_name"] == f"L{user}"
        users.append(json_val)

    for user in users:
        value = EmployeeRepository.get(db_session, id=user["id"])
        assert value.first_name == user["first_name"]
        assert value.last_name == user["last_name"]


def test_vacation_employee(db_session, api_client):
    username01 = "user" + uuid.uuid4().hex.upper()[0:6]
    resp = api_client.post(
        "/employee",
        json={"first_name": f"F{username01}", "last_name": f"L{username01}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    json_val = resp.json()

    vacation = VacationRepresentation(
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 1),
    )
    url = "/employee/" + json_val["id"] + "/vacation"
    resp = api_client.post(
        url,
        json=json.loads(vacation.model_dump_json()),
    )
    assert resp.status_code == status.HTTP_200_OK
    added_vacation = resp.json()

    model = VacationRepository.get(db_session, id=added_vacation["id"])

    assert VacationRepresentation.model_validate(
        model
    ) == VacationRepresentation.model_validate(added_vacation)

    vacation = VacationRepresentationNoID(
        vacation_type=VacationType.UnpaidLeave,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 1),
    )
    url = "/vacation/" + added_vacation["id"] + "/"
    resp = api_client.put(
        url,
        json=json.loads(vacation.model_dump_json()),
    )
    assert resp.status_code == status.HTTP_200_OK
    updated_vacation = resp.json()

    db_session.expire_all()

    model = VacationRepository.get(db_session, id=added_vacation["id"])
    assert VacationRepresentation.model_validate(
        model
    ) == VacationRepresentation.model_validate(updated_vacation)
