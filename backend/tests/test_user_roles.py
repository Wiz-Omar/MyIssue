import pytest
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.role import RoleName
from app.services.user_role import UserRoleService
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.testclient import TestClient


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

    user_admin = db_session.query(User).filter_by(email="john.doe@gmail.com").first()
    user_developer = db_session.query(User).filter_by(email="oyounes57@gmail.com").first()

    roles = db_session.query(Role).all()
    roles_by_name = {r.role_name: r for r in roles}
    role_admin, role_developer = roles_by_name["admin"], roles_by_name["developer"]

    db_session.add(UserRole(user_id=user_admin.id, role_id=role_admin.id))
    db_session.add(UserRole(user_id=user_developer.id, role_id=role_developer.id))
    db_session.commit()

    return client

def test_add_user_role_success(db_session: Session):
    user = User(
        first_name="max", last_name="vilhem",
        email="max_vilhem@hotmail.com", password_hash="irrelevant"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = UserRoleService(db_session)
    user_role = service.add_user_role(RoleName.DEVELOPER, user.id)

    assert user_role.user_id == user.id

    stored = db_session.query(UserRole).filter_by(user_id=user.id).first()
    assert stored is not None
    assert stored.role_id == user_role.role_id

def test_add_user_role_duplicate(db_session: Session):
    user = User(
        first_name="max", last_name="vilhem",
        email="max_vilhem@hotmail.com", password_hash="irrelevant"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = UserRoleService(db_session)
    service.add_user_role(RoleName.DEVELOPER, user.id)

    with pytest.raises(HTTPException) as exc_info:
        service.add_user_role(RoleName.DEVELOPER, user.id)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User already has this role"

def test_has_role_true_and_false(client_with_users: TestClient, db_session: Session):
    admin = db_session.query(User).filter_by(email="john.doe@gmail.com").first()
    service = UserRoleService(db_session)

    assert service.has_role(RoleName.ADMIN, admin.id) is True
    assert service.has_role(RoleName.DEVELOPER, admin.id) is False

def test_add_user_role_as_admin(client_with_users: TestClient, db_session: Session):
    admin = db_session.query(User).filter_by(email="john.doe@gmail.com").first()

    new_user = User(
        first_name="max", last_name="vilhem",
        email="max_vilhem@hotmail.com", password_hash="irrelevant"
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    login_response = client_with_users.post("/auth/login", json={
        "email": admin.email, "password": "123456789"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})

    response = client_with_users.post(f"/users/{new_user.id}/roles", json={
        "role": "developer"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(new_user.id)

def test_add_user_role_as_non_admin(client_with_users: TestClient, db_session: Session):
    developer = db_session.query(User).filter_by(email="oyounes57@gmail.com").first()
    other_user = db_session.query(User).filter_by(email="john.doe@gmail.com").first()

    login_response = client_with_users.post("/auth/login", json={
        "email": developer.email, "password": "1234567890"
    })
    access_token = login_response.json()["access_token"]
    client_with_users.headers.update({"Authorization": f"Bearer {access_token}"})

    response = client_with_users.post(f"/users/{other_user.id}/roles", json={
        "role": "admin"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed to assign roles"
