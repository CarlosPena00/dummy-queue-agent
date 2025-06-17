"""Unit tests for stock consumer."""

import pytest
from faststream.rabbit import TestRabbitBroker
from pydantic import ValidationError

from src.consumers.stock_consumer import broker
from src.models.stock import StockPayload


@pytest.mark.asyncio
async def test_stockpayload_valid_stock_update():
    """Test stock update processing with valid payload."""
    async with TestRabbitBroker(broker) as test_broker:
        test_payload = StockPayload(
            code_id="TEST123",
            seller_id="SELLER1",
            stock=10.0,
        )

        await test_broker.connect()
        await test_broker.publish(
            message=test_payload.model_dump(),
            queue="stock-updates",
        )


@pytest.mark.asyncio
async def test_stockpayload_missing_code_id():
    """Test stock update fails when code_id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        StockPayload(
            # field "code_id" is required
            seller_id="SELLER1",
            stock=10.0,
        )

    assert "code_id" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_stockpayload_invalid_stock_type():
    """Test stock update fails when stock is not numeric."""
    with pytest.raises(ValidationError) as exc_info:
        StockPayload(
            code_id="TEST123",
            seller_id="SELLER1",
            stock="invalid",
        )

    assert "stock" in str(exc_info.value)
    assert "Input should be a valid number" in str(exc_info.value)


@pytest.mark.asyncio
async def test_stockpayload_none_stock():
    """Test stock update fails when stock is None."""
    with pytest.raises(ValidationError) as exc_info:
        StockPayload(
            code_id="TEST123",
            seller_id="SELLER1",
            stock=None,
        )

    assert "stock" in str(exc_info.value)
    assert "Input should be a valid number" in str(exc_info.value)


@pytest.mark.asyncio
async def test_stockpayload_negative_stock():
    """Test stock update fails when stock is negative."""
    with pytest.raises(ValidationError) as exc_info:
        StockPayload(
            code_id="TEST123",
            seller_id="SELLER1",
            stock=-1.0,  # fail: Non-negative float
        )

    assert "stock" in str(exc_info.value)
    assert "Input should be greater than or equal to 0" in str(exc_info.value)
