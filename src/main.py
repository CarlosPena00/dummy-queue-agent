"""Main service module."""

import signal
import sys
from multiprocessing import Process
from typing import Optional

import uvicorn
from loguru import logger

from src.api.server import app
from src.consumer.base_consumer import BaseConsumer
from src.core.settings import settings
from src.mongodb import mongodb
from src.validator.schema_validator import validate_message


class ProductConsumer(BaseConsumer):
    """Consumer for product messages."""

    def process_message(self, message_str: str) -> None:
        """Process a product message.

        Args:
            message_str: The message to process
        """
        document, errors = validate_message(message_str, "products")
        if errors:
            logger.error(f"Validation failed: {errors}")
            return

        mongodb.insert_document("products", document)


class StockConsumer(BaseConsumer):
    """Consumer for stock messages."""

    def process_message(self, message_str: str) -> None:
        """Process a stock message.

        Args:
            message_str: The message to process
        """
        document, errors = validate_message(message_str, "stocks")
        if errors:
            logger.error(f"Validation failed: {errors}")
            return

        mongodb.insert_document("stocks", document)


class PriceConsumer(BaseConsumer):
    """Consumer for price messages."""

    def process_message(self, message_str: str) -> None:
        """Process a price message.

        Args:
            message_str: The message to process
        """
        document, errors = validate_message(message_str, "prices")
        if errors:
            logger.error(f"Validation failed: {errors}")
            return

        mongodb.insert_document("prices", document)


def start_api_server() -> None:
    """Start the FastAPI server."""
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )


def start_consumers() -> list[Process]:
    """Start the RabbitMQ consumers.

    Returns:
        List of consumer processes
    """
    consumers = [
        ProductConsumer(settings.PRODUCT_QUEUE),
        StockConsumer(settings.STOCK_QUEUE),
        PriceConsumer(settings.PRICE_QUEUE),
    ]

    processes: list[Process] = []
    for consumer in consumers:
        process = Process(target=consumer.start_consuming)
        process.start()
        processes.append(process)

    return processes


def handle_shutdown(signum: int, _frame: Optional[object]) -> None:
    """Handle shutdown signals.

    Args:
        signum: Signal number
        _frame: Current stack frame (unused)
    """
    logger.info(f"Received signal {signum}, shutting down...")
    mongodb.disconnect()
    sys.exit(0)


def main() -> None:
    """Main service entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    # Connect to MongoDB
    if not mongodb.connect():
        logger.error("Failed to connect to MongoDB")
        sys.exit(1)

    # Start consumers in separate processes
    consumer_processes = start_consumers()

    try:
        # Start API server in main process
        start_api_server()
    finally:
        # Clean up on exit
        for process in consumer_processes:
            process.terminate()
            process.join()
        mongodb.disconnect()


if __name__ == "__main__":
    main()
