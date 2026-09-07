import pytest
import db_service

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Store, User


@pytest.fixture
def test_session(monkeypatch):
    test_engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(
        test_engine,
        tables=[
            Store.__table__,
            User.__table__,
        ]
    )

    TestingSession = sessionmaker(bind=test_engine)

    monkeypatch.setattr(db_service, "Session", TestingSession)

    yield TestingSession

    test_engine.dispose()