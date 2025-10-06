"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db


# Test database setup
@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_db] = get_session_override
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
