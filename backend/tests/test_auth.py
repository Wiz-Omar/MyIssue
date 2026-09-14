from app.main import app
from fastapi.testclient import TestClient


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
