"""MongoDB connection module."""

import time
from typing import Any
from typing import Optional
from typing import TypeVar
from typing import cast

from loguru import logger
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from pymongo.errors import PyMongoError
from pymongo.results import InsertOneResult

from src.core.settings import settings

T = TypeVar("T", bound=dict[str, Any])


class MongoDB:
    """MongoDB connection class."""

    def __init__(self) -> None:
        """Initialize MongoDB connection."""
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.connected = False
        self.settings = settings.get_mongodb_settings()

    def connect(self) -> bool:
        """Connect to MongoDB."""
        try:
            # Connect to MongoDB with retry
            retry_attempts = 5
            retry_delay = 5

            for attempt in range(retry_attempts):
                try:
                    self.client = MongoClient(self.settings["uri"])
                    # Force a command to check the connection
                    self.client.admin.command("ping")
                    self.db = self.client[self.settings["db_name"]]
                    self.connected = True
                    logger.info("Successfully connected to MongoDB")
                    break
                except ConnectionFailure as e:
                    if attempt < retry_attempts - 1:
                        logger.warning(
                            f"MongoDB connection attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {retry_delay} seconds..."
                        )
                        time.sleep(retry_delay)
                    else:
                        logger.error(
                            f"Failed to connect to MongoDB after {retry_attempts}"
                            " attempts"
                        )
                        raise

            return self.connected
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        try:
            if self.client is not None:
                self.client.close()
        finally:
            self.client = None
            self.db = None
            self.connected = False
            logger.info("MongoDB connection closed")

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a MongoDB collection by name."""
        if not self.connected or self.db is None:
            if not self.connect():
                logger.error(
                    f"Failed to get collection '{collection_name}': "
                    "not connected to MongoDB"
                )
                return None

        return self.db[collection_name] if self.db is not None else None

    def insert_document(
        self, collection_name: str, document: dict[str, Any]
    ) -> Optional[str]:
        """Insert a document into a collection.

        Args:
            collection_name: The collection name to insert into
            document: The document to insert

        Returns:
            The document ID if successful, None otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return None

            result: InsertOneResult = collection.insert_one(document)
            logger.info(
                f"Document inserted into '{collection_name}' with ID: "
                f"{result.inserted_id}"
            )
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error inserting document into '{collection_name}': {e}")
            return None

    def find_documents(
        self, collection_name: str, query: dict[str, Any], limit: int = 100
    ) -> list[dict[str, Any]]:
        """Find documents in a collection based on a query.

        Args:
            collection_name: The collection name to query
            query: The query filter
            limit: Maximum number of documents to return

        Returns:
            A list of matching documents
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return []

            cursor = collection.find(query).limit(limit)
            return cast(list[dict[str, Any]], list(cursor))
        except PyMongoError as e:
            logger.error(f"Error querying '{collection_name}': {e}")
            return []

    def find_document_by_product_code(
        self, collection_name: str, product_code: str
    ) -> Optional[dict[str, Any]]:
        """Find a document by product code.

        Args:
            collection_name: The collection to query
            product_code: The product code to look for

        Returns:
            The matching document or None if not found
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return None

            result = collection.find_one({"product_code": product_code})
            return cast(Optional[dict[str, Any]], result)
        except PyMongoError as e:
            logger.error(
                f"Error finding document by product code '{product_code}': {e}"
            )
            return None


# Create a singleton instance
mongodb = MongoDB()
