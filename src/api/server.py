"""API server module for data query."""

from typing import Any
from typing import Optional

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from src.core.settings import settings
from src.mongodb import mongodb


# Define Pydantic models for API responses
class ProductResponse(BaseModel):
    """Product response model."""

    product_code: str
    name: str
    description: str
    category: str
    brand: str
    price: float
    currency: str
    sku: str
    created_at: str
    updated_at: str


class StockResponse(BaseModel):
    """Stock response model."""

    product_code: str
    quantity: int
    warehouse_id: str
    location: str
    updated_at: str


class PriceResponse(BaseModel):
    """Price response model."""

    product_code: str
    price: float
    currency: str
    effective_date: str
    expires_at: Optional[str] = None
    promotion_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str


# Create FastAPI application
app = FastAPI(
    title="Data Ingestion API",
    description="API for querying ingested data",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")  # type: ignore[misc]
async def startup_event() -> None:
    """Connect to MongoDB on startup."""
    logger.info("Starting up API server")
    if not mongodb.connected:
        mongodb.connect()


@app.on_event("shutdown")  # type: ignore[misc]
async def shutdown_event() -> None:
    """Disconnect from MongoDB on shutdown."""
    logger.info("Shutting down API server")
    if mongodb.connected:
        mongodb.disconnect()


@app.get("/health", response_model=dict[str, str])  # type: ignore[misc]
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get(
    "/api/v1/products/{product_code}",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse}},
)  # type: ignore[misc]
async def get_product(product_code: str) -> JSONResponse:
    """Get product by product code.

    Args:
        product_code: The product code to look up

    Returns:
        The product data

    Raises:
        HTTPException: If the product is not found
    """
    logger.info(f"Looking up product with code: {product_code}")

    document = mongodb.find_document_by_product_code("products", product_code)

    if not document:
        logger.warning(f"Product not found: {product_code}")
        raise HTTPException(
            status_code=404, detail=f"Product not found: {product_code}"
        )

    return JSONResponse(content=document)


@app.get(
    "/api/v1/stocks/{product_code}",
    response_model=StockResponse,
    responses={404: {"model": ErrorResponse}},
)  # type: ignore[misc]
async def get_stock(product_code: str) -> JSONResponse:
    """Get stock data by product code.

    Args:
        product_code: The product code to look up

    Returns:
        The stock data

    Raises:
        HTTPException: If the stock data is not found
    """
    logger.info(f"Looking up stock data for product: {product_code}")

    document = mongodb.find_document_by_product_code("stocks", product_code)

    if not document:
        logger.warning(f"Stock data not found for product: {product_code}")
        raise HTTPException(
            status_code=404, detail=f"Stock data not found for product: {product_code}"
        )

    return JSONResponse(content=document)


@app.get(
    "/api/v1/prices/{product_code}",
    response_model=PriceResponse,
    responses={404: {"model": ErrorResponse}},
)  # type: ignore[misc]
async def get_price(product_code: str) -> JSONResponse:
    """Get price data by product code.

    Args:
        product_code: The product code to look up

    Returns:
        The price data

    Raises:
        HTTPException: If the price data is not found
    """
    logger.info(f"Looking up price data for product: {product_code}")

    document = mongodb.find_document_by_product_code("prices", product_code)

    if not document:
        logger.warning(f"Price data not found for product: {product_code}")
        raise HTTPException(
            status_code=404, detail=f"Price data not found for product: {product_code}"
        )

    return JSONResponse(content=document)


@app.get("/api/v1/products", response_model=list[ProductResponse])  # type: ignore[misc]
async def list_products(
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    brand: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Get a list of products with optional filtering.

    Args:
        limit: Maximum number of results to return
        category: Filter by category
        brand: Filter by brand

    Returns:
        List of products matching the filter criteria
    """
    query: dict[str, Any] = {}

    if category:
        query["category"] = category
    if brand:
        query["brand"] = brand

    documents = mongodb.find_documents("products", query, limit=limit)

    return documents


def run_server() -> None:
    """Run the FastAPI server with uvicorn."""
    import uvicorn

    logger.info(f"Starting API server at {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "src.api.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
