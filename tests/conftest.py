import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import cache
from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def fake_cache(monkeypatch):
    """Replaces app.core.cache with an in-memory dict for every test.

    Tests shouldn't need a real Redis running to pass (same reasoning as using SQLite
    instead of Postgres for the DB) — but the fake still round-trips through JSON like
    the real cache does, so cache-specific tests can exercise hit/miss/invalidate
    behavior for real, just against this fixture's `store` instead of Redis.
    """
    store: dict[str, str] = {}

    def fake_get_json(key):
        raw = store.get(key)
        return json.loads(raw) if raw is not None else None

    def fake_set_json(key, value, *, ttl_seconds):
        store[key] = json.dumps(value)

    def fake_delete(key):
        store.pop(key, None)

    monkeypatch.setattr(cache, "get_json", fake_get_json)
    monkeypatch.setattr(cache, "set_json", fake_set_json)
    monkeypatch.setattr(cache, "delete", fake_delete)
    yield store
