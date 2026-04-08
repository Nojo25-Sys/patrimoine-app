import os
os.environ["SECRET_KEY"] = "test_secret_key_for_tests_only"
os.environ["MAIL_FROM"] = "test@test.com"
os.environ["MAIL_PASSWORD"] = "test_password"
os.environ["DATABASE_URL"] = "sqlite:///./test_patrimoine.db"

import pytest, sys
sys.path.insert(0, ".")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

engine = create_engine("sqlite:///./test_patrimoine.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def reset_db():
    from database import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(reset_db):
    from database import get_db
    from main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def registered_user(client):
    data = {"username": "testuser", "email": "test@example.com", "password": "Passw0rd!"}
    resp = client.post("/users/", json=data)
    assert resp.status_code == 201
    return data

@pytest.fixture
def auth_headers(client, registered_user):
    resp = client.post("/login", data={"username": registered_user["username"], "password": registered_user["password"]})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

@pytest.fixture
def sample_patrimoine(client, auth_headers):
    data = {"nom": "Cathédrale de Lomé", "type": "Religieux", "ville": "Lomé", "latitude": 6.1375, "longitude": 1.2123}
    resp = client.post("/patrimoines/", json=data, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()