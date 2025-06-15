"""Integration tests for MongoDB module."""

import os
from collections.abc import Generator

import pytest
from pymongo.collection import Collection

from src.mongodb import MongoDB


@pytest.fixture
def mongo_test_db() -> Generator[MongoDB, None, None]:
    """Create a test MongoDB instance with a test database."""
    # Use environment variables or fallback to localhost for testing
    test_uri = os.environ.get("TEST_MONGODB_URI", "mongodb://localhost:27017/test_db")

    # Create a test instance (not using singleton for test isolation)
    test_mongo = MongoDB()
    test_mongo.settings = {"uri": test_uri, "db_name": "test_db"}

    # Connect to the test database and handle failures
    connected = test_mongo.connect()
    if not connected:
        test_mongo.disconnect()
        pytest.fail(
            "Failed to connect to MongoDB - check if MongoDB is running and accessible"
        )

    # Connection successful, yield the instance
    yield test_mongo

    # Clean up after the test
    if test_mongo.db is not None:
        for collection_name in ["test_products", "test_stocks"]:
            if collection_name in test_mongo.db.list_collection_names():
                collection: Collection = test_mongo.db[collection_name]
                collection.drop()

    test_mongo.disconnect()


@pytest.mark.integration
def test_mongodb_connect(mongo_test_db: MongoDB) -> None:
    """Test connecting to MongoDB."""
    assert mongo_test_db.connected is True
    assert mongo_test_db.get_collection("test_products") is not None


@pytest.mark.integration
def test_mongodb_insert_document(mongo_test_db: MongoDB) -> None:
    """Test inserting a document into MongoDB."""
    # Test document
    test_doc = {
        "product_code": "TEST-123",
        "collection": "test_products",
        "name": "Test Product",
        "price": 10.99,
    }

    # Insert document
    doc_id = mongo_test_db.insert_document("test_products", test_doc)

    # Verify document was inserted
    assert doc_id is not None

    # Retrieve the document and verify
    collection = mongo_test_db.get_collection("test_products")
    assert collection is not None
    retrieved_doc = collection.find_one({"product_code": "TEST-123"})

    assert retrieved_doc is not None
    assert retrieved_doc["product_code"] == "TEST-123"
    assert retrieved_doc["name"] == "Test Product"


@pytest.mark.integration
def test_mongodb_find_document_by_product_code(mongo_test_db: MongoDB) -> None:
    """Test finding a document by product code."""
    # Test documents
    test_docs = [
        {
            "product_code": "TEST-001",
            "collection": "test_products",
            "name": "Product 1",
            "price": 10.99,
        },
        {
            "product_code": "TEST-002",
            "collection": "test_products",
            "name": "Product 2",
            "price": 20.99,
        },
    ]

    # Insert test documents
    collection = mongo_test_db.get_collection("test_products")
    assert collection is not None
    collection.insert_many(test_docs)

    # Find document by product code
    result = mongo_test_db.find_document_by_product_code("test_products", "TEST-002")

    # Verify the correct document was found
    assert result is not None
    assert result["product_code"] == "TEST-002"
    assert result["name"] == "Product 2"

    # Test looking for non-existent product
    result = mongo_test_db.find_document_by_product_code(
        "test_products", "NON-EXISTENT"
    )
    assert result is None


@pytest.mark.integration
def test_mongodb_find_documents(mongo_test_db: MongoDB) -> None:
    """Test finding documents with a query."""
    # Test documents
    test_docs = [
        {
            "product_code": "STOCK-001",
            "collection": "test_stocks",
            "warehouse_id": "WH-NORTH",
            "quantity": 100,
        },
        {
            "product_code": "STOCK-002",
            "collection": "test_stocks",
            "warehouse_id": "WH-NORTH",
            "quantity": 200,
        },
        {
            "product_code": "STOCK-003",
            "collection": "test_stocks",
            "warehouse_id": "WH-SOUTH",
            "quantity": 150,
        },
    ]

    # Insert test documents
    collection = mongo_test_db.get_collection("test_stocks")
    assert collection is not None
    collection.insert_many(test_docs)

    # Find documents with a query
    results = mongo_test_db.find_documents("test_stocks", {"warehouse_id": "WH-NORTH"})

    # Verify the query results
    assert len(results) == 2
    assert results[0]["warehouse_id"] == "WH-NORTH"
    assert results[1]["warehouse_id"] == "WH-NORTH"

    # Test with empty results
    results = mongo_test_db.find_documents("test_stocks", {"warehouse_id": "WH-EAST"})
    assert len(results) == 0
