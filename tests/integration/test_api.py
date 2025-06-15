"""Integration tests for FastAPI endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_mongodb():
    """Create a mocked MongoDB instance for API testing."""
    with patch("src.api.server.mongodb") as mock_db:
        # Set up the connected property
        mock_db.connected = True
        yield mock_db


@pytest.mark.integration
def test_health_check(test_client: TestClient) -> None:
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.integration
def test_get_product_success(test_client: TestClient, mock_mongodb) -> None:
    """Test successfully getting a product by product code."""
    # Mock the find_document_by_product_code method to return a test document
    mock_mongodb.find_document_by_product_code.return_value = {
        "product_code": "TEST-001",
        "collection": "products",
        "name": "Test Product",
        "description": "Test Description",
        "category": "Test Category",
        "brand": "Test Brand",
        "price": 10.0,
        "currency": "USD",
        "sku": "SKU-123",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    # Make the API request
    response = test_client.get("/api/v1/products/TEST-001")

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["product_code"] == "TEST-001"
    assert data["name"] == "Test Product"

    # Verify that the MongoDB method was called correctly
    mock_mongodb.find_document_by_product_code.assert_called_once_with(
        "products", "TEST-001"
    )


@pytest.mark.integration
def test_get_product_not_found(test_client: TestClient, mock_mongodb) -> None:
    """Test getting a non-existent product."""
    # Mock the find_document_by_product_code method to return None
    mock_mongodb.find_document_by_product_code.return_value = None

    # Make the API request
    response = test_client.get("/api/v1/products/NON-EXISTENT")

    # Check the response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.integration
def test_get_stock_success(test_client: TestClient, mock_mongodb) -> None:
    """Test successfully getting stock data by product code."""
    # Mock the find_document_by_product_code method to return a test document
    mock_mongodb.find_document_by_product_code.return_value = {
        "product_code": "TEST-001",
        "collection": "stocks",
        "quantity": 100,
        "warehouse_id": "WAREHOUSE-1",
        "location": "A1-B2-C3",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    # Make the API request
    response = test_client.get("/api/v1/stocks/TEST-001")

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["product_code"] == "TEST-001"
    assert data["quantity"] == 100
    assert data["warehouse_id"] == "WAREHOUSE-1"

    # Verify that the MongoDB method was called correctly
    mock_mongodb.find_document_by_product_code.assert_called_once_with(
        "stocks", "TEST-001"
    )


@pytest.mark.integration
def test_list_products(test_client: TestClient, mock_mongodb) -> None:
    """Test listing products with filtering."""
    # Mock the find_documents method
    mock_mongodb.find_documents.return_value = [
        {
            "product_code": "TEST-001",
            "collection": "products",
            "name": "Test Product 1",
            "description": "Description 1",
            "category": "Category A",
            "brand": "Brand X",
            "price": 10.0,
            "currency": "USD",
            "sku": "SKU-001",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        },
        {
            "product_code": "TEST-002",
            "collection": "products",
            "name": "Test Product 2",
            "description": "Description 2",
            "category": "Category A",
            "brand": "Brand Y",
            "price": 20.0,
            "currency": "USD",
            "sku": "SKU-002",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        },
    ]

    # Make the API request with filters
    response = test_client.get(
        "/api/v1/products?category=Category%20A&brand=Brand%20X&limit=10"
    )

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["product_code"] == "TEST-001"
    assert data[1]["product_code"] == "TEST-002"

    # Verify that the MongoDB method was called correctly with the query
    mock_mongodb.find_documents.assert_called_once()
    call_args = mock_mongodb.find_documents.call_args[0]
    assert call_args[0] == "products"
    assert "category" in call_args[1]
    assert call_args[1]["category"] == "Category A"
    assert "brand" in call_args[1]
