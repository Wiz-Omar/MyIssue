import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from app.main import app
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import TokenResponse
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import TEST_JWT_ALGORITHM, TEST_JWT_SECRET_KEY


def test_register_user(db_session: Session):
    client = TestClient(app)

    users: list[User] = db_session.query(User).filter_by(email="john.doe@gmail.com").all()
    assert len(users) == 0

    response = client.post(  
        "/auth/register", json={
                "first_name": "john", 
                "last_name": "doe", 
                "email": "john.doe@gmail.com", 
                "password": "123456789"}
    )

    users: list[User] = db_session.query(User).filter_by(email="john.doe@gmail.com").all()
    assert len(users) == 1

    data: dict = response.json()

    assert response.status_code == 201  
    assert data["id"] == str(users[0].id)
    assert data["first_name"] == "john"
    assert data["last_name"] == "doe"
    assert data["email"] == "john.doe@gmail.com"
    parsed_date = datetime.fromisoformat(data["signup_date"])
    assert parsed_date < datetime.now(timezone.utc)
    # Check that the response model is UserReponse, not User; meaning password_hash is omitted
    assert not data.get("password_hash")

def test_register_existing_user(db_session: Session):
    client = TestClient(app)

    _ = client.post(  
        "/auth/register", json={
                "first_name": "john", 
                "last_name": "doe", 
                "email": "john.doe@gmail.com", 
                "password": "123456789"}
    )
    response = client.post(  
        "/auth/register", json={
                "first_name": "john", 
                "last_name": "doe", 
                "email": "john.doe@gmail.com", 
                "password": "123456789"}
    )

    data: dict = response.json()
    assert response.status_code == 500
    assert data["detail"] == "Database error"

def test_login_user(db_session: Session):
    client = TestClient(app)

    _ = client.post(  
        "/auth/register", json={
                "first_name": "john", 
                "last_name": "doe", 
                "email": "john.doe@gmail.com", 
                "password": "123456789"}
    )
    user: User = db_session.query(User).filter_by(email="john.doe@gmail.com").first()

    response = client.post(
        "/auth/login", json={
            "email": "john.doe@gmail.com",
            "password": "123456789"
        }
    )

    assert response.status_code == 200
    data: dict = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]

    payload = jwt.decode(
        data["access_token"], TEST_JWT_SECRET_KEY, algorithms=[TEST_JWT_ALGORITHM]
    )
    assert payload["sub"] == str(user.id)

    refresh_token_hash = hashlib.sha256(data["refresh_token"].encode()).hexdigest()
    refresh_token: RefreshToken | None = db_session.query(RefreshToken).filter_by(token_hash=refresh_token_hash).first()
    assert refresh_token
    # Check that the refresh token expires in more than 6 days (set to 7)
    assert refresh_token.expires_at > (datetime.now(timezone.utc) + timedelta(days=6))
    assert refresh_token.user_id == user.id

def test_refresh(db_session: Session):
    client = TestClient(app)

    _ = client.post(  
        "/auth/register", json={
                "first_name": "john", 
                "last_name": "doe", 
                "email": "john.doe@gmail.com", 
                "password": "123456789"}
    )
    user: User = db_session.query(User).filter_by(email="john.doe@gmail.com").first()

    login_response = client.post(
            "/auth/login", json={
                "email": "john.doe@gmail.com",
                "password": "123456789"
            }
    )
    tokens_before_refresh: list[RefreshToken] = db_session.query(RefreshToken).filter_by(user_id=user.id).all()
    # Check that the login added a refresh token to the table
    assert len(tokens_before_refresh) == 1
    original_token: RefreshToken = tokens_before_refresh[0]

    refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": login_response.json()["refresh_token"]}
    )

    data: TokenResponse = refresh_response.json()
    assert refresh_response.status_code == 200
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]
    new_raw_refresh_token: str = data["refresh_token"]

    tokens_after_refresh: list[RefreshToken] = db_session.query(RefreshToken).filter_by(user_id=user.id).all()
    # Check that the refresh triggered a rotation of the refresh token, not added a new
    assert len(tokens_after_refresh) == 1
    new_token: RefreshToken = tokens_after_refresh[0]

    # Check that the new refresh token after refreshing is a rotated token, not the same
    assert original_token.id != new_token.id
    assert original_token.token_hash != new_token.token_hash
    assert hashlib.sha256(new_raw_refresh_token.encode()).hexdigest() == new_token.token_hash

def test_logout_user(db_session):
    client = TestClient(app)

    _ = client.post(  
        "/auth/register", json={
                "first_name": "john", 
                "last_name": "doe", 
                "email": "john.doe@gmail.com", 
                "password": "123456789"}
    )
    user: User = db_session.query(User).filter_by(email="john.doe@gmail.com").first()

    login_response = client.post(
            "/auth/login", json={
                "email": "john.doe@gmail.com",
                "password": "123456789"
            }
    )
    assert login_response.status_code == 200
    original_refresh_tokens: list[RefreshToken] = db_session.query(RefreshToken).filter_by(user_id=user.id).all()
    assert len(original_refresh_tokens) == 1

    raw_refresh_token: str = login_response.json()["refresh_token"]
    logout_response = client.post(
        "/auth/logout", json={"refresh_token": raw_refresh_token}
    )
    assert logout_response.status_code == 200
    new_refresh_tokens: list[RefreshToken] = db_session.query(RefreshToken).filter_by(user_id=user.id).all()
    # Check that logging out deleted the refresh token from the table
    assert len(new_refresh_tokens) == 0

    false_refresh_response = client.post(
            "/auth/refresh", json={"refresh_token": raw_refresh_token}
    )
    # Check that the refresh endpoint requires a current valid refresh token before rotating to a new
    assert false_refresh_response.status_code == 401
    assert false_refresh_response.json()["detail"] == "Invalid or expired refresh token"
