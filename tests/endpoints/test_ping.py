from fastapi.testclient import TestClient

from src.server import app

client = TestClient(app)


def test_ping_endpoint():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
