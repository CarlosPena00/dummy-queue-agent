"""Integration tests for FastAPI lifespan with RabbitMQ broker."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.server import lifespan
from src.consumers.stock_consumer import broker


@pytest.mark.integration
def test_lifespan_with_testclient():
    """Test the lifespan function using TestClient.

    This test verifies that the FastAPI application can start and stop
    with the lifespan function managing the broker connection.
    """
    with TestClient(FastAPI(lifespan=lifespan)) as client:
        client.get("/")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rabbitmq_broker_connection():
    """Test direct connection to RabbitMQ broker.

    This test verifies that we can connect to and disconnect from the broker.
    """
    await broker.start()
    await broker.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_lifespan_broker_connection():
    """Test that the lifespan function correctly connects to the RabbitMQ broker.

    This test uses a real RabbitMQ connection to verify the lifespan functionality.
    """
    test_app = FastAPI()
    broker_connected = False

    async def test_lifespan():
        nonlocal broker_connected
        async with lifespan(test_app):
            await broker.publish(
                message={"test": "connection"},
                queue="test-connection",
            )
            broker_connected = True

    await test_lifespan()
    assert broker_connected, "RabbitMQ broker connection failed during lifespan"
