# Scripts Directory

This directory contains utility scripts for running and testing the data ingestion service.

## Available Scripts

### `00_start_docker.sh`

Starts all services defined in the docker-compose.yml file.

```bash
# Start all services
./scripts/00_start_docker.sh

# Start in detached mode
./scripts/00_start_docker.sh -d

# Start specific service
./scripts/00_start_docker.sh app
```

### `01_start_uvicorn.sh`

Starts just the FastAPI server using uvicorn.

```bash
# Start FastAPI server with auto-reload (for development)
./scripts/01_start_uvicorn.sh
```

### `02_start_service.sh`

Starts the complete data ingestion service (both RabbitMQ consumers and API server).

```bash
# Start the complete service
./scripts/02_start_service.sh
```

### `03_run_tests.sh`

Runs the tests using pytest.

```bash
# Run all tests
./scripts/03_run_tests.sh

# Run specific test file
./scripts/03_run_tests.sh tests/unit/test_validators.py

# Run with coverage
./scripts/03_run_tests.sh --cov=src tests/
```

### `04_publish_test_message.py`

Publishes a test message to a RabbitMQ queue.

```bash
# Publish a test message to the products queue
./scripts/04_publish_test_message.py

# Publish to a specific queue
./scripts/04_publish_test_message.py --queue stocks

# With custom product code
./scripts/04_publish_test_message.py --product-code CUSTOM-001

# With custom RabbitMQ connection
./scripts/04_publish_test_message.py --host rabbitmq --port 5672 --user guest --password guest
```

## Usage Notes

These scripts are designed to be run from the project root directory. Make sure to grant execute permissions if needed:

```bash
chmod +x scripts/*.sh scripts/*.py
```
