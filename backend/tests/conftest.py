import os

os.environ["DATABASE_URL"] = "sqlite://"
TEST_JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"] = "8681459bddd74cd4bdf90bb164f48ea06442d768837fbd17af1fa202f0d06eb7"
TEST_JWT_ALGORITHM = os.environ["JWT_ALGORITHM"] = "HS256"

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
