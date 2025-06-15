"""Price consumer module."""

from loguru import logger

from src.consumer.base_consumer import BaseConsumer
from src.mongodb import mongodb
from src.validator.schema_validator import validate_message


class PriceConsumer(BaseConsumer):
    """Consumer for price messages."""

    def __init__(self) -> None:
        """Initialize the price consumer."""
        super().__init__("prices")
        logger.info("Price consumer initialized")

    def process_message(self, message_str: str) -> None:
        """Process a price message.

        Args:
            message_str: The message to process
        """
        document, errors = validate_message(message_str, "prices")
        if errors:
            logger.error(f"Validation failed: {errors}")
            return

        # Ensure MongoDB is connected
        if not mongodb.connected:
            mongodb.connect()

        # Extract the collection name from the document
        collection_name = document.get("collection")
        if not collection_name:
            raise ValueError("Missing collection field in document")

        # Get the product code for logging
        product_code = document.get("product_code", "unknown")

        # Insert the document into MongoDB
        document_id = mongodb.insert_document(collection_name, document)

        if document_id:
            logger.info(
                f"Successfully stored price data for product {product_code}",
                extra={
                    "product_code": product_code,
                    "collection": collection_name,
                    "document_id": document_id,
                    "price": document.get("price", 0.0),
                    "currency": document.get("currency", "USD"),
                },
            )
        else:
            logger.error(f"Failed to store price data for product {product_code}")
            raise RuntimeError(f"Failed to store price data for product {product_code}")
