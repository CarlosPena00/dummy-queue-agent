# Data Ingestion Service

A production-grade data ingestion service that consumes messages from RabbitMQ queues, validates the data against schemas, and stores it in MongoDB.

## Features

- Subscribes to multiple RabbitMQ queues with ordered delivery
- Validates JSON messages against strict schemas
- Stores data in MongoDB/DocumentDB based on collection name
- Handles errors with retries and dead-letter queues
- Exposes a FastAPI endpoint for querying data
- Graceful shutdown with proper resource cleanup
- Structured logging with loguru
- Containerized with Docker and docker-compose

## Architecture

The service follows a clean, modular architecture:

- **Consumers**: Handle message consumption from RabbitMQ queues
- **Validators**: Validate incoming messages against schemas
- **Storage**: Store validated data in MongoDB/DocumentDB
- **API**: Query data through FastAPI endpoints

## Requirements

- Python 3.11+
- RabbitMQ
- MongoDB/DocumentDB
- Docker and docker-compose (for containerized deployment)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd data-ingestion-service
   ```

2. Build and run the services:
   ```bash
   docker-compose up -d
   ```

This will start:
- The data ingestion service
- MongoDB
- RabbitMQ with management console

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd data-ingestion-service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.sample`:
   ```bash
   cp .env.sample .env
   # Edit .env with your configuration
   ```

5. Run the service:
   ```bash
   python -m src.main
   ```

## Configuration

Configuration is managed through:
- Environment variables with the `INGEST_` prefix
- `.env` file (for local development)

Key configuration options:

- **RabbitMQ**:
  - `INGEST_RABBITMQ_HOST`: RabbitMQ host
  - `INGEST_RABBITMQ_PORT`: RabbitMQ port
  - `INGEST_RABBITMQ_QUEUES`: List of queues to consume from

- **MongoDB**:
  - `INGEST_MONGODB_URI`: MongoDB connection URI
  - `INGEST_MONGODB_DB_NAME`: MongoDB database name

- **API**:
  - `INGEST_API_HOST`: API host
  - `INGEST_API_PORT`: API port
  - `INGEST_API_WORKERS`: Number of API workers

## Message Format

Messages must be JSON objects with:
- A `collection` field specifying where to store the data
- A mandatory `product_code` field
- Schema-specific fields based on collection type

Example product message:
```json
{
  "product_code": "PROD-123",
  "collection": "products",
  "name": "Sample Product",
  "description": "This is a sample product",
  "category": "Electronics",
  "brand": "SampleBrand",
  "price": 99.99,
  "currency": "USD",
  "sku": "SKU-123-456",
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z"
}
```

## API Endpoints

- `GET /health`: Health check endpoint
- `GET /api/v1/products/{product_code}`: Get product by product code
- `GET /api/v1/stocks/{product_code}`: Get stock data by product code
- `GET /api/v1/prices/{product_code}`: Get price data by product code
- `GET /api/v1/products`: List products with optional filtering

## Testing

Run tests with pytest:

```bash
pytest tests/
```

For unit tests only:
```bash
pytest tests/unit/
```

For integration tests:
```bash
pytest tests/integration/
```

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Use pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Run tests:
   ```bash
   pytest
   ```

## License

MIT

```sh
make

# After update `setup.cfg`
make lockdeps
make deps
```

## Run
```sh
# start docker:
sh scripts/00_start.sh
```


## Add Secrets

Secrets and configmaps should be declared with their respective types in the src.core.settings file.

In the case of secrets, we must only place their values ​​in the .env file (non-versioned file).

```py
python -m src.core.settings
> API_KEY='FOO'
```

> echo 'API_KEY=123' >> .env

```py
python -m src.core.settings
> API_KEY='123'
```
