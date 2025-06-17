"""Integration tests for stock service."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_health_check():
    response = client.get("/ping")
    assert response.status_code == 200
