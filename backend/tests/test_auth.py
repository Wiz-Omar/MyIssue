import jwt
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient
from tests.conftest import TEST_JWT_ALGORITHM, TEST_JWT_SECRET_KEY, TestingSessionLocal


def test_register_user():
    client = TestClient(app)  

    response = client.post(  
        "/auth/register", json={
                "first_name": "Omar", 
                "last_name": "Younes", 
                "email": "oyounes57@gmail.com", 
                "password": "123456789"}
    )

    data = response.json()

    assert response.status_code == 201  
    assert data["message"] == "User registered successfully"

def test_register_existing_user():
    client = TestClient(app)

    response = client.post(  
        "/auth/register", json={
                "first_name": "Omar", 
                "last_name": "Younes", 
                "email": "oyounes57@gmail.com", 
                "password": "123456789"}
    )

    data = response.json()

    assert response.status_code == 500
    assert data["detail"] == "Database error"

def test_login_user():
    client = TestClient(app)

    response = client.post(
        "/auth/login", json={
            "email": "oyounes57@gmail.com",
            "password": "123456789"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"

    db = TestingSessionLocal()
    user: User = db.query(User).filter_by(email="oyounes57@gmail.com").first()

    payload = jwt.decode(
        data["access_token"], TEST_JWT_SECRET_KEY, algorithms=[TEST_JWT_ALGORITHM]
    )
    assert payload["sub"] == str(user.id)
