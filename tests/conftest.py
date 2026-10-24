import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session
from app.deps import get_current_actor, Actor
from app import models

# 1. 创建纯内存 SQLite 数据库
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    # 覆盖数据库 Session
    def get_session_override():
        return session

    # 🌟 覆盖鉴权：直接返回一个拥有所有权限的 super_admin，免去带 Token
    def get_actor_override():
        return Actor(username="test_bot", role="super_admin", permissions=["*"])

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_actor] = get_actor_override
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
