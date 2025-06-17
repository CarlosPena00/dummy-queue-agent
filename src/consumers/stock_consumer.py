"""Stock consumer module."""

from typing import Literal

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from loguru import logger
from pydantic import BaseModel

from src.core.settings import settings
from src.models.stock import StockPayload

router = APIRouter(prefix="/stock", tags=["stock"])
broker = RabbitBroker(settings.RABBITMQ_URL)
app = FastStream(broker)


class PublishResponse(BaseModel):
    """Response model for publish endpoint.

    Fields:
        status: Status of the publish operation
        message: Description of the operation result
    """

    status: Literal["success", "error"]
    message: str


@router.post(
    "/publish",
    response_model=PublishResponse,
    description="Publish a stock update message to RabbitMQ",
)
async def publish_stock_update(payload: StockPayload) -> PublishResponse:
    """Publish a stock update message.

    Args:
        payload: Stock update data

    Returns:
        PublishResponse: Operation result

    Raises:
        HTTPException: If message publishing fails
    """
    try:
        message = payload.model_dump()
        await broker.publish(
            message=message,
            queue="stock-updates",
        )
    except Exception as e:
        logger.error("Failed to publish stock update: {}", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish stock update",
        ) from e

    return PublishResponse(
        status="success",
        message=f"Stock update message published successfully: {message}",
    )


@broker.subscriber("stock-updates")
async def process_stock_update(msg: StockPayload) -> None:
    """Process stock update messages.

    Args:
        msg: Stock update payload

    The message will be automatically validated against the StockPayload model.
    If validation fails, the message will be rejected.
    """
    logger.info(
        "Stock update received - Product: {}, Seller: {}, Stock: {}",
        msg.code_id,
        msg.seller_id,
        msg.stock,
    )
