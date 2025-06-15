"""Core settings module for the data ingestion service."""

from pathlib import Path
from typing import Any

from loguru import logger
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

# Define the base directory
BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings."""

    # General settings
    APP_NAME: str = "data-ingestion-service"
    LOG_LEVEL: str = "INFO"

    # RabbitMQ settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_QUEUES: list[str] = ["products", "stocks", "prices"]
    RABBITMQ_PREFETCH_COUNT: int = 10
    RABBITMQ_RETRY_DELAY: int = 5
    RABBITMQ_MAX_RETRIES: int = 3
    RABBITMQ_DLQ_SUFFIX: str = ".dlq"

    # MongoDB settings
    MONGODB_URI: str = "mongodb://localhost:27017/data_ingestion"
    MONGODB_DB_NAME: str = "data_ingestion"

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1

    # Configuration for environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def get_rabbitmq_url(self) -> str:
        """Get the RabbitMQ connection URL."""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"

    def get_mongodb_settings(self) -> dict[str, Any]:
        """Get MongoDB connection settings."""
        return {
            "uri": self.MONGODB_URI,
            "db_name": self.MONGODB_DB_NAME,
        }


# Create a global settings instance
settings = Settings()


# Configure loguru logger
logger.remove()
logger.add(
    f"{BASE_DIR}/logs/{{time:YYYY-MM-DD}}.log",
    rotation="1 day",
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}",
    serialize=True,
)
logger.add(
    lambda msg: print(msg),
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
