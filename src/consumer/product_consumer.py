"""Product consumer module."""

from loguru import logger

from src.consumer.base_consumer import BaseConsumer
from src.mongodb import mongodb
from src.validator.schema_validator import validate_message


class ProductConsumer(BaseConsumer):
    """Consumer for product messages."""

    def __init__(self) -> None:
        """Initialize the product consumer."""
        super().__init__("products")
        logger.info("Product consumer initialized")

    def process_message(self, message_str: str) -> None:
        """Process a product message.

        Args:
            message_str: The message to process
        """
        document, errors = validate_message(message_str, "products")
        if errors:
            logger.error(f"Validation failed: {errors}")
            return

        # Ensure MongoDB is connected
        if not mongodb.connected:
            mongodb.connect()

        # Insert the document into MongoDB
        document_id = mongodb.insert_document("products", document)

        if document_id:
            product_code = document.get("product_code", "unknown")
            logger.info(
                f"Successfully stored product data with code {product_code}",
                extra={
                    "product_code": product_code,
                    "collection": "products",
                    "document_id": document_id,
                },
            )
        else:
            raise RuntimeError("Failed to store product data in MongoDB")
