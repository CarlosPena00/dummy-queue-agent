from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)


def test_dummy():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
