import os

os.environ["DATABASE_URL"] = "sqlite://"

from app.database import Base, get_db
from app.main import app
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
            os.environ["DATABASE_URL"],
            connect_args={
                    "check_same_thread": False,
            },
            poolclass=StaticPool
        )

Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()

app.dependency_overrides[get_db] = override_get_db
