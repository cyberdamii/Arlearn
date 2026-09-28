import os
import tempfile

_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_dir}/test.db"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    email = f"user{os.urandom(4).hex()}@example.com"
    response = client.post(
        "/api/auth/register",
        json={"email": email, "name": "Test User", "password": "password123", "role": "student"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
