import os

import pytest
from app.models.role import Role

os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/myissue_test"
TEST_JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"] = "8681459bddd74cd4bdf90bb164f48ea06442d768837fbd17af1fa202f0d06eb7"
TEST_JWT_ALGORITHM = os.environ["JWT_ALGORITHM"] = "HS256"

import app.models
from app.database import Base, get_db
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ["DATABASE_URL"])

TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    session.add_all([Role(role_name="admin"), Role(role_name="developer")])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

def override_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()

app.dependency_overrides[get_db] = override_get_db
