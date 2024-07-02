
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from src.database import metadata, Base
from src.config import (DB_HOST_TEST, DB_NAME_TEST, DB_PASS_TEST, DB_PORT_TEST,
                        DB_USER_TEST)
from src.main import app


DATABASE_URL_TEST = f"postgresql+psycopg2://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"
engine_test = create_engine(DATABASE_URL_TEST, echo=True)
session_test = sessionmaker(bind=engine_test)


@pytest.fixture(scope="module")
def session_db():
    with session_test() as session:
        yield session


@pytest.fixture(scope="session")
def test_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield
    # Base.metadata.drop_all(bind=engine_test)
    # Base.metadata.create_all(bind=engine_test)

@pytest.fixture
def client():
    return TestClient(app)

