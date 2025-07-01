"""Core settings module for the data ingestion service."""

from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

# Define the base directory
BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # General settings
    APP_NAME: str = "data-ingestion-service"
    LOG_LEVEL: str = "INFO"

    # RabbitMQ settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_URL: str = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
    RABBITMQ_QUEUES: list[str] = ["products", "stocks", "prices"]
    RABBITMQ_DLQ_SUFFIX: str = "_dlq"

    # MongoDB settings
    MONGODB_URI: str = "mongodb://localhost:27017/data_ingestion"
    MONGODB_DB_NAME: str = "data_ingestion"

    # Configuration for environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Create a global settings instance
settings = Settings()
