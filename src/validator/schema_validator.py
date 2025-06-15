"""Schema validator module for validating incoming messages."""

import json
from json.decoder import JSONDecodeError
from typing import Any
from typing import TypedDict
from typing import Union

from loguru import logger


class ProductSchema(TypedDict):
    """Product schema definition.

    Fields:
        product_code: Unique product identifier
        name: Product name
        description: Product description
        category: Product category
        brand: Product brand
    """

    product_code: str
    name: str
    description: str
    category: str
    brand: str


class StockSchema(TypedDict):
    """Stock schema definition.

    Fields:
        product_code: Product identifier
        warehouse_id: Warehouse identifier
        quantity: Stock quantity
        location: Stock location in warehouse
    """

    product_code: str
    warehouse_id: str
    quantity: int
    location: str


class PriceSchema(TypedDict):
    """Price schema definition.

    Fields:
        product_code: Product identifier
        currency: Price currency code
        base_price: Original price
        discount_percentage: Discount percentage
        final_price: Final price after discount
    """

    product_code: str
    currency: str
    base_price: float
    discount_percentage: float
    final_price: float


# Define a union type for all possible schema types
SchemaType = Union[type[ProductSchema], type[StockSchema], type[PriceSchema]]


def validate_document(document: dict[str, Any], schema_type: SchemaType) -> list[str]:
    """Validate a document against a schema.

    Args:
        document: The document to validate
        schema_type: The schema type to validate against

    Returns:
        A list of validation errors
    """
    errors: list[str] = []

    # Get required fields from the schema
    required_fields = schema_type.__annotations__.keys()

    # Check for missing required fields
    for field in required_fields:
        if field not in document:
            errors.append(f"Missing required field: {field}")
            continue

        # Type checking based on schema
        expected_type = schema_type.__annotations__[field]
        value = document[field]

        if not isinstance(value, expected_type):
            errors.append(
                f"Invalid type for field {field}: expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    return errors


def validate_json_string(json_str: str) -> str:
    """Validate that a string is valid JSON.

    Args:
        json_str: The string to validate

    Returns:
        The validated JSON string

    Raises:
        ValueError: If the string is not valid JSON
    """
    try:
        json.loads(json_str)
        return json_str
    except JSONDecodeError as err:
        raise ValueError(f"Invalid JSON: {err!s}") from err


def get_schema_for_collection(collection_name: str) -> SchemaType:
    """Get the schema type for a collection.

    Args:
        collection_name: The collection name

    Returns:
        The schema type for the collection

    Raises:
        ValueError: If the collection name is not recognized
    """
    schema_map: dict[str, SchemaType] = {
        "products": ProductSchema,
        "stocks": StockSchema,
        "prices": PriceSchema,
    }

    if collection_name not in schema_map:
        raise ValueError(f"Unknown collection: {collection_name}")

    return schema_map[collection_name]


def validate_message(
    message_str: str, collection_name: str
) -> tuple[dict[str, Any], list[str]]:
    """Validate a message string against a collection schema.

    Args:
        message_str: The message string to validate
        collection_name: The collection name to validate against

    Returns:
        A tuple of (parsed document, list of validation errors)
    """
    try:
        # First validate JSON format
        validate_json_string(message_str)
        document = json.loads(message_str)

        if not isinstance(document, dict):
            return {}, ["Message must be a JSON object"]

        # Get and validate against schema
        schema_type = get_schema_for_collection(collection_name)
        validation_errors = validate_document(document, schema_type)

        return document, validation_errors

    except (ValueError, JSONDecodeError) as e:
        logger.error(f"Error validating message: {e}")
        return {}, [str(e)]
    except Exception as e:
        logger.error(f"Unexpected error during message validation: {e}")
        return {}, [f"Validation error: {e}"]
