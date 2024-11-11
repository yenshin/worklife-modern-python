import json
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.model.vacation import VacationModel, VacationType
from app.repository.employee import EmployeeRepository
from app.repository.vacation import VacationRepository, _prepare_overlap_merging
from app.schema import VacationRepresentation, VacationRepresentationNoID
from app.schema.employee import EmployeeRepresentation, EmployeeSearchQuery


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


@pytest.fixture
def create_user(api_client, db_session):
    users = []

    def _create_user(username: str):
        resp = api_client.post(
            "/employee",
            json={"first_name": f"F{username}", "last_name": f"L{username}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        json_val = resp.json()
        assert json_val["first_name"] == f"F{username}"
        assert json_val["last_name"] == f"L{username}"
        users.append(json_val)
        return json_val

    try:
        yield _create_user
    finally:
        for user in users:
            EmployeeRepository.delete(db_session, id=uuid.UUID(user["id"]))


@pytest.fixture
def users(create_user):
    username01 = "user" + uuid.uuid4().hex.upper()[0:6]
    username02 = "user" + uuid.uuid4().hex.upper()[0:6]
    username03 = "user" + uuid.uuid4().hex.upper()[0:6]
    username04 = "user" + uuid.uuid4().hex.upper()[0:6]
    usernames = [username01, username02, username03, username04]
    users = []
    for user in usernames:
        json_val = create_user(user)
        users.append(json_val)
    return users


def test_create_employee(db_session, users):
    for user in users:
        value = EmployeeRepository.get(db_session, id=user["id"])
        assert value is not None
        assert value.first_name == user["first_name"]
        assert value.last_name == user["last_name"]


def test_vacation_employee(db_session, api_client, create_user):
    username01 = "user" + uuid.uuid4().hex.upper()[0:6]
    json_val = create_user(username01)
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

    # TODO test delete from api


def test_search_employee(db_session, api_client, users):
    monday = 5
    month = 2
    vacationsu1 = [
        (datetime(2024, month, monday), datetime(2024, month, monday + 2)),
        (datetime(2024, month, monday + 3), datetime(2024, month, monday + 4)),
        (datetime(2024, month, monday + 8), datetime(2024, month, monday + 10)),
    ]
    url = "/employee/" + users[0]["id"] + "/vacation"
    for vacationtime in vacationsu1:
        vacation = VacationRepresentationNoID(
            vacation_type=VacationType.UnpaidLeave,
            start_date=vacationtime[0],
            end_date=vacationtime[1],
        )
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

    vacationsu2 = [
        (datetime(2024, month, monday + 2), datetime(2024, month, monday + 10))
    ]
    url = "/employee/" + users[1]["id"] + "/vacation"
    for vacationtime in vacationsu2:
        vacation = VacationRepresentationNoID(
            vacation_type=VacationType.PaidLeave,
            start_date=vacationtime[0],
            end_date=vacationtime[1],
        )
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

    vacationsu3 = [(datetime(2024, month, monday), datetime(2024, month, monday + 10))]
    url = "/employee/" + users[2]["id"] + "/vacation"
    for vacationtime in vacationsu3:
        vacation = VacationRepresentationNoID(
            vacation_type=VacationType.UnpaidLeave,
            start_date=vacationtime[0],
            end_date=vacationtime[1],
        )
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

    vacationsu4 = [(datetime(2024, month, monday), datetime(2024, month, monday + 10))]
    url = "/employee/" + users[3]["id"] + "/vacation"
    for vacationtime in vacationsu4:
        vacation = VacationRepresentationNoID(
            vacation_type=VacationType.PaidLeave,
            start_date=vacationtime[0],
            end_date=vacationtime[1],
        )
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

    # INFO: do the search
    url = f"/employee?first_name={users[0]['first_name']}"
    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    res_data = res.json()
    assert len(res_data) == 1
    assert str(EmployeeRepresentation.model_validate(res_data[0]).id) == users[0]["id"]

    url = f"/employee?last_name={users[1]['last_name']}"
    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    res_data = res.json()
    assert len(res_data) == 1
    assert str(EmployeeRepresentation.model_validate(res_data[0]).id) == users[1]["id"]

    url = f"/employee?vacation_type={VacationType.PaidLeave.value}&vacation_start={datetime(2024, month, monday).isoformat()}&vacation_end={datetime(2024, month, monday + 10).isoformat()}"
    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    res_data = res.json()
    assert len(res_data) == 2

    url = f"/employee?vacation_type={VacationType.UnpaidLeave.value}&vacation_start={datetime(2024, month, monday).isoformat()}&vacation_end={datetime(2024, month, monday + 10).isoformat()}"
    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    res_data = res.json()
    assert len(res_data) == 2


def test_employee_seach_query():
    EmployeeSearchQuery(first_name="toto", last_name="tata")
    with pytest.raises(ValueError, match="if vacation, both date must be specified"):
        EmployeeSearchQuery(
            first_name="toto", last_name="tata", vacation_type=VacationType.PaidLeave
        )
    with pytest.raises(ValueError, match="if vacation, both date must be specified"):
        EmployeeSearchQuery(
            first_name="toto",
            last_name="tata",
            vacation_type=VacationType.PaidLeave,
            vacation_start=datetime.now(),
        )
    with pytest.raises(ValueError, match="if vacation, both date must be specified"):
        EmployeeSearchQuery(
            first_name="toto",
            last_name="tata",
            vacation_type=VacationType.PaidLeave,
            vacation_end=datetime.now(),
        )
    EmployeeSearchQuery(
        first_name="toto",
        last_name="tata",
        vacation_type=VacationType.PaidLeave,
        vacation_start=datetime.now(),
        vacation_end=datetime.now() + timedelta(seconds=1),
    )
    with pytest.raises(ValueError, match="start must be equal or less than end"):
        EmployeeSearchQuery(
            first_name="toto",
            last_name="tata",
            vacation_type=VacationType.PaidLeave,
            vacation_start=datetime.now() + timedelta(days=1),
            vacation_end=datetime.now(),
        )


def test_vacation_merging_algorithm():
    vac1 = VacationModel(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 1),  # INFO this is monday
        end_date=datetime(2024, 1, 5),
    )
    vac2 = VacationModel(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 8),  # INFO this is monday
        end_date=datetime(2024, 1, 10),
    )

    vac_target = VacationModel(
        id=uuid.UUID("10000000-0000-0000-0000-000000000000"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 2),  # INFO this is monday
        end_date=datetime(2024, 1, 9),
    )
    to_merge = [vac1, vac2]
    result = _prepare_overlap_merging(to_merge, vac_target)
    assert result[0] == vac1.id
    assert result[1] == vac2.id
    assert vac_target.start_date == vac1.start_date
    assert vac_target.end_date == vac2.end_date

    vac3 = VacationModel(
        id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 12),  # INFO this is monday
        end_date=datetime(2024, 1, 16),
    )
    vac_target = VacationModel(
        id=uuid.UUID("10000000-0000-0000-0000-000000000000"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 4),  # INFO this is monday
        end_date=datetime(2024, 1, 12),
    )
    to_merge = [vac1, vac2, vac3]
    result = _prepare_overlap_merging(to_merge, vac_target)
    assert result[0] == vac1.id
    assert result[1] == vac2.id
    assert result[2] == vac3.id
    assert vac_target.start_date == vac1.start_date
    assert vac_target.end_date == vac3.end_date

    vac2.vacation_type = VacationType.UnpaidLeave
    to_merge = [vac1, vac2, vac3]
    with pytest.raises(ValueError, match="can't merge date of different type"):
        _prepare_overlap_merging(to_merge, vac_target)


# TODO: fix the code to manage this case
def _test_merging_complexecase():
    """
    i is time unit in days
    1, 2, 3 are vacation
    t is the target vacation that should be merged
    r is the expected result

    i-i-i-i-i-i-i-i-i
    1-1   2---2   3-3
        t-------t
    r---------------r
    """
    vac1 = VacationModel(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
    )

    vac2 = VacationModel(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 4),
        end_date=datetime(2024, 1, 6),
    )

    vac3 = VacationModel(
        id=uuid.UUID("10000000-0000-0000-0000-000000000003"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 8),
        end_date=datetime(2024, 1, 9),
    )

    vac_target = VacationModel(
        id=uuid.UUID("10000000-0000-0000-0000-000000000000"),
        user_id=uuid.UUID(int=0),
        vacation_type=VacationType.PaidLeave,
        start_date=datetime(2024, 1, 3),
        end_date=datetime(2024, 1, 7),
    )
    to_merge = [vac1, vac2, vac3]
    result = _prepare_overlap_merging(to_merge, vac_target)
    assert result[0] == vac1.id
    assert result[1] == vac2.id
    assert result[2] == vac3.id
    assert vac_target.start_date == vac1.start_date
    assert vac_target.end_date == vac3.end_date
