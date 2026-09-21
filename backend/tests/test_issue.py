import uuid
from datetime import datetime, timedelta, timezone

import pytest
from app.core.security import create_access_token
from app.main import app
from app.models.issue import Issue
from app.models.user import User
from app.schemas.role import RoleName
from app.services.user_role import UserRoleService
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def client_with_users(db_session: Session) -> TestClient:
    client = TestClient(app)
    client.post("/auth/register", json={
        "first_name": "john", "last_name": "doe", 
        "email": "john.doe@gmail.com", "password": "123456789"
    })
    client.post("/auth/register", json={
        "first_name": "omar", "last_name": "youn", 
        "email": "oyounes57@gmail.com", "password": "1234567890"
    })
    client.post("/auth/register", json={
        "first_name": "max", "last_name": "vilhem", 
        "email": "max_vilhem@hotmail.com", "password": "12345678910"
    })

    user_admin: User = db_session.query(User).filter_by(email="john.doe@gmail.com").first()
    user_developer: User = db_session.query(User).filter_by(email="oyounes57@gmail.com").first()
    user_second_developer: User = db_session.query(User).filter_by(email="max_vilhem@hotmail.com").first()

    user_role_service: UserRoleService = UserRoleService(db_session)
    user_role_service.add_user_role(RoleName.ADMIN, user_admin.id)
    user_role_service.add_user_role(RoleName.DEVELOPER, user_developer.id)
    user_role_service.add_user_role(RoleName.DEVELOPER, user_second_developer.id)

    return client

def test_create_issue_variations(client_with_users: TestClient, db_session: Session):
    def assert_response_data(issue_data: dict, 
                            user_id: str, assigned_user_id: str | None = None,
                            description: str | None = None
    ):
        assert issue_data["title"] == "Repeatedly calling the auth refresh endpoint causes db error"
        assert datetime.fromisoformat(issue_data["created_at"]) < datetime.now(timezone.utc)
        assert datetime.fromisoformat(issue_data["updated_at"]) < datetime.now(timezone.utc)
        assert issue_data["created_by"] == user_id
        if assigned_user_id is not None:
            assert issue_data["assigned_user_id"] == assigned_user_id
        if description is not None:
            assert issue_data["description"] == description

    login_response = client_with_users.post("/auth/login", json={
        "email": "john.doe@gmail.com", "password": "123456789"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})

    response = client_with_users.post("/issues", json={
        "title": "Repeatedly calling the auth refresh endpoint causes db error"
    })
    assert response.status_code == 201
    data: dict = response.json()
    user: User = db_session.query(User).filter_by(email="john.doe@gmail.com").first()
    assert_response_data(data, str(user.id))

    description = (
        "After a failed call because of an expired access_token, "
        "an automated call to the refresh endpoint is done, but if "
        "it fails once and then in a loop, a db error eventually "
        "ends the loop."
    )
    response = client_with_users.post("/issues", json={
        "title": "Repeatedly calling the auth refresh endpoint causes db error",
        "description": description
    })
    assert response.status_code == 201
    data: dict = response.json()
    assert_response_data(data, str(user.id), description=description)

    response = client_with_users.post("/issues", json={
        "title": "Repeatedly calling the auth refresh endpoint causes db error",
        "description": description,
        "assigned_user_id": str(user.id)
    })
    assert response.status_code == 201
    data: dict = response.json()
    assert_response_data(data, str(user.id), assigned_user_id=str(user.id), description=description)

def test_developer_can_self_assign(client_with_users: TestClient, db_session: Session):
    user_developer: User = db_session.query(User).filter_by(email="oyounes57@gmail.com").first()
    login_response = client_with_users.post("/auth/login", json={
        "email": user_developer.email, "password": "1234567890"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})

    response = client_with_users.post("/issues", json={
        "title": "Repeatedly calling the auth refresh endpoint causes db error",
        "assigned_user_id": str(user_developer.id)
    })
    assert response.status_code == 201
    data: dict = response.json()
    assert data["created_by"] == str(user_developer.id)
    assert data["assigned_user_id"] == str(user_developer.id)

    response = client_with_users.post("/issues", json={
        "title": "Registering with a an email with an extra dash does not trigger the unique contraint for emails",
    })
    assert response.status_code == 201
    data = response.json()
    response = client_with_users.patch(f"/issues/{data["id"]}/assign", json={
        "user_id": str(user_developer.id)
    })
    assert response.status_code == 200
    data: dict = response.json()
    assert data["created_by"] == str(user_developer.id)
    assert data["assigned_user_id"] == str(user_developer.id)

def test_admin_can_assign_developer(client_with_users: TestClient, db_session: Session):
    user_admin: User = db_session.query(User).filter_by(email="john.doe@gmail.com").first()
    user_developer: User = db_session.query(User).filter_by(email="oyounes57@gmail.com").first()

    login_response = client_with_users.post("/auth/login", json={
        "email": user_admin.email, "password": "123456789"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})
    
    response = client_with_users.post("/issues", json={
        "title": "Repeatedly calling the auth refresh endpoint causes db error",
        "assigned_user_id": str(user_developer.id)
    })
    assert response.status_code == 201
    data: dict = response.json()
    assert data["created_by"] == str(user_admin.id)
    assert data["assigned_user_id"] == str(user_developer.id)

def test_developer_cannot_assign_others(client_with_users: TestClient, db_session: Session):
    user_developer_assignor: User = db_session.query(User).filter_by(email="max_vilhem@hotmail.com").first()
    user_developer_assignee: User = db_session.query(User).filter_by(email="oyounes57@gmail.com").first()

    login_response = client_with_users.post("/auth/login", json={
        "email": user_developer_assignor.email, "password": "12345678910"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})
    
    response = client_with_users.post("/issues", json={
        "title": "Repeatedly calling the auth refresh endpoint causes db error",
    })
    assert response.status_code == 201
    data: dict = response.json()
    issue_id: str = data["id"]
    assert data["created_by"] == str(user_developer_assignor.id)

    response = client_with_users.patch(f"/issues/{issue_id}/assign", json={
        "user_id": str(user_developer_assignee.id)
    })
    assert response.status_code == 403
    data: dict = response.json()
    assert data["detail"] == "Not allowed to assign user to issue"

def test_issue_fetch(client_with_users: TestClient, db_session: Session):
    #logged in fetch
    login_response = client_with_users.post("/auth/login", json={
        "email": "max_vilhem@hotmail.com", "password": "12345678910"
    })
    data = login_response.json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})

    response = client_with_users.post("/issues", json={
        "title": "Repeatedly calling the auth refresh endpoint causes db error",
    })
    assert response.status_code == 201
    issue_create_data = response.json()

    response = client_with_users.get(f"issues/{issue_create_data["id"]}")
    assert response.status_code == 200
    issue_fetch_data = response.json()

    assert issue_create_data["id"] == issue_fetch_data["id"]

    #logged out fetch
    logout_response = client_with_users.post("/auth/logout", json={
        "refresh_token": refresh_token
    })
    assert logout_response.status_code == 200
    #mock expiration of access token
    user: User = db_session.query(User).filter_by(email="max_vilhem@hotmail.com").first()
    expired_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(seconds=-1)  #already expired access token
    )
    client_with_users.headers.update({"Authorization": f"Bearer {expired_token}"})

    response = client_with_users.get(f"issues/{issue_create_data["id"]}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_issue_update_success(client_with_users: TestClient, db_session: Session):
    login_response = client_with_users.post("/auth/login", json={
        "email": "john.doe@gmail.com", "password": "123456789"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})

    create_response = client_with_users.post("/issues", json={
        "title": "Original title",
        "description": "Original description"
    })
    assert create_response.status_code == 201
    issue_id = create_response.json()["id"]

    update_response = client_with_users.patch(f"/issues/{issue_id}", json={
        "title": "Updated title",
        "description": "Updated description"
    })
    assert update_response.status_code == 200
    updated_data = update_response.json()

    assert updated_data["id"] == issue_id
    assert updated_data["title"] == "Updated title"
    assert updated_data["description"] == "Updated description"

    user = db_session.query(User).filter_by(email="john.doe@gmail.com").first()
    issue = db_session.query(Issue).filter_by(id=issue_id).first()
    assert issue.title == "Updated title"
    assert issue.description == "Updated description"
    assert issue.created_by == user.id  #unchanged by update


def test_issue_update_not_found(client_with_users: TestClient):
    login_response = client_with_users.post("/auth/login", json={
        "email": "john.doe@gmail.com", "password": "123456789"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})

    fake_issue_id = uuid.uuid4()

    update_response = client_with_users.patch(f"/issues/{fake_issue_id}", json={
        "title": "This issue will not be added",
        "description": "will not be applied as a description"
    })
    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Issue not found"