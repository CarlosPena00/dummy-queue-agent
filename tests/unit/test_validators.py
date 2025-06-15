"""Unit tests for schema validators."""

import json

import pytest

from src.validator.schema_validator import ProductSchema
from src.validator.schema_validator import StockSchema
from src.validator.schema_validator import validate_document
from src.validator.schema_validator import validate_json_string
from src.validator.schema_validator import validate_message


def test_validate_product_document() -> None:
    """Test validating a product document."""
    # Valid product document
    document = {
        "product_code": "TEST-001",
        "name": "Test Product",
        "description": "A test product",
        "category": "Test",
        "brand": "Test Brand",
    }

    errors = validate_document(document, ProductSchema)
    assert not errors

    # Invalid product document (missing required field)
    invalid_doc = {
        "product_code": "TEST-001",
        "name": "Test Product",
        # missing description
        "category": "Test",
        "brand": "Test Brand",
    }

    errors = validate_document(invalid_doc, ProductSchema)
    assert errors
    assert "Missing required field: description" in errors


def test_validate_stock_document() -> None:
    """Test validating a stock document."""
    # Valid stock document
    document = {
        "product_code": "TEST-001",
        "warehouse_id": "WH-001",
        "quantity": 100,
        "location": "A1-B2",
    }

    errors = validate_document(document, StockSchema)
    assert not errors

    # Invalid stock document (wrong type)
    invalid_doc = {
        "product_code": "TEST-001",
        "warehouse_id": "WH-001",
        "quantity": "100",  # should be int
        "location": "A1-B2",
    }

    errors = validate_document(invalid_doc, StockSchema)
    assert errors
    assert any("Invalid type for field quantity" in error for error in errors)


def test_validate_json_string() -> None:
    """Test JSON string validation."""
    # Valid JSON
    valid_json = '{"key": "value"}'
    assert validate_json_string(valid_json) == valid_json

    # Invalid JSON
    invalid_json = '{"key": value"'  # missing quote
    with pytest.raises(ValueError, match="Invalid JSON"):
        validate_json_string(invalid_json)


def test_validate_message() -> None:
    """Test message validation."""
    # Valid product message
    valid_message = json.dumps(
        {
            "product_code": "TEST-001",
            "name": "Test Product",
            "description": "A test product",
            "category": "Test",
            "brand": "Test Brand",
        }
    )

    document, errors = validate_message(valid_message, "products")
    assert not errors
    assert document["product_code"] == "TEST-001"

    # Invalid JSON
    invalid_json = '{"key": value"'  # missing quote
    document, errors = validate_message(invalid_json, "products")
    assert errors
    assert "Invalid JSON" in errors[0]

    # Invalid collection
    document, errors = validate_message(valid_message, "invalid_collection")
    assert errors
    assert "Unknown collection" in errors[0]
