"""Base consumer module for RabbitMQ message processing."""

import threading
import time
from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import cast

import pika
from loguru import logger
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError
from pika.exceptions import ConnectionClosedByBroker
from pika.exceptions import StreamLostError
from pika.spec import Basic
from pika.spec import BasicProperties

from src.core.settings import settings


class BaseConsumer(ABC):
    """Base consumer class for RabbitMQ message processing."""

    def __init__(self, queue_name: str):
        """Initialize consumer with queue name.

        Args:
            queue_name: The queue to consume messages from
        """
        self.queue_name = queue_name
        self.dlq_name = f"{queue_name}{settings.RABBITMQ_DLQ_SUFFIX}"
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None
        self.is_consuming = False
        self.should_stop = False
        self._consumer_tag: Optional[str] = None
        # For graceful shutdown
        self._closing_event = threading.Event()
        self._connection_attempts = 0
        self._max_connection_attempts = 10

    def connect(self) -> bool:
        """Establish connection to RabbitMQ.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Reset connection attempt counter if we're not in a retry cycle
            if (
                self._connection_attempts == 0
                or self._connection_attempts > self._max_connection_attempts
            ):
                self._connection_attempts = 1

            logger.info(
                f"Connecting to RabbitMQ (attempt {self._connection_attempts})..."
            )

            # Create connection parameters with automatic recovery enabled
            parameters = pika.URLParameters(settings.get_rabbitmq_url())
            parameters.heartbeat = 600  # Heartbeat timeout in seconds
            parameters.blocked_connection_timeout = (
                300  # Blocked connection timeout in seconds
            )

            # Establish connection
            self.connection = pika.BlockingConnection(parameters)

            # Create channel
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=settings.RABBITMQ_PREFETCH_COUNT)

            # Ensure queue and DLQ exist
            self._setup_queues()

            logger.info(
                f"Successfully connected to RabbitMQ, consuming from {self.queue_name}"
            )
            return True

        except Exception as e:
            if self._connection_attempts < self._max_connection_attempts:
                retry_delay = min(
                    settings.RABBITMQ_RETRY_DELAY * (2**self._connection_attempts), 60
                )
                self._connection_attempts += 1
                logger.warning(
                    f"Failed to connect to RabbitMQ: {e}. "
                    f"Retrying in {retry_delay} seconds (attempt "
                    f"{self._connection_attempts})..."
                )
                time.sleep(retry_delay)
                return self.connect()
            else:
                logger.error(
                    f"Failed to connect to RabbitMQ after {self._connection_attempts} "
                    f"attempts: {e}"
                )
                return False

    def _setup_queues(self) -> None:
        """Set up the necessary queues and exchanges.

        Creates the main queue and dead-letter queue if they don't already exist.
        """
        if not self.channel:
            logger.error("Cannot setup queues: Channel not established")
            return

        # Declare the dead-letter queue
        self.channel.queue_declare(
            queue=self.dlq_name,
            durable=True,
            arguments={
                "x-message-ttl": 1000 * 60 * 60 * 24 * 7,  # 7 days
            },
        )

        # Declare the main queue with dead-letter configuration
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": self.dlq_name,
            },
        )

    def _initialize_consumption(self) -> bool:
        """Initialize consumer and start consuming messages.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if not self.connection or not self.channel:
            if not self.connect():
                logger.error("Failed to start consumer: Could not connect to RabbitMQ")
                return False

        if self.channel is None:
            return False

        self.is_consuming = True
        self._consumer_tag = self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self._process_message_wrapper
        )
        logger.info(f"Started consuming from queue: {self.queue_name}")
        return True

    def _handle_consumption_error(self, error: Exception) -> None:
        """Handle errors that occur during message consumption.

        Args:
            error: The exception that occurred
        """
        if isinstance(error, (ConnectionClosedByBroker, StreamLostError)):
            logger.warning(f"Connection lost: {error}. Reconnecting...")
            self._reconnect()
        elif isinstance(error, AMQPError):
            logger.error(f"AMQP error: {error}. Reconnecting...")
            self._reconnect()
        else:
            logger.error(f"Unexpected error during message consumption: {error}")
            if not self.should_stop:
                self._reconnect()

    def _run_consumption_loop(self) -> None:
        """Run the main consumption loop."""
        while not self.should_stop:
            try:
                if self.channel and not self.channel.is_closed:
                    self.channel.start_consuming()
                else:
                    self._reconnect()
            except Exception as e:
                self._handle_consumption_error(e)

    def start_consuming(self) -> None:
        """Start consuming messages from the queue."""
        if self.should_stop:
            self.should_stop = False

        try:
            if not self._initialize_consumption():
                return
            self._run_consumption_loop()
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            self.stop_consuming()

    def _reconnect(self) -> None:
        """Reconnect to RabbitMQ after a connection failure."""
        if self.should_stop:
            return

        # Close existing connection if any
        self._close_connection()

        # Try to reconnect
        reconnect_delay = 5
        logger.info(f"Attempting to reconnect in {reconnect_delay} seconds...")
        time.sleep(reconnect_delay)

        if self.connect() and self.channel is not None:
            logger.info("Reconnected to RabbitMQ")
            # Restart consuming
            if self.is_consuming:
                self._consumer_tag = self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self._process_message_wrapper,
                )
        else:
            logger.error("Failed to reconnect to RabbitMQ")

    def _process_message_wrapper(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        """Process a message from the queue.

        Args:
            channel: The channel the message was received on
            method: The method frame
            properties: Message properties
            body: Message body
        """
        delivery_tag = cast(int, method.delivery_tag)
        message_id = properties.message_id or "unknown"

        try:
            message_str = body.decode("utf-8")
            logger.info(f"Processing message {message_id}")

            try:
                self.process_message(message_str)
                if channel.is_open:
                    channel.basic_ack(delivery_tag=delivery_tag)
                    logger.info(f"Successfully processed message {message_id}")

            except ValueError as e:
                logger.error(
                    f"Validation error for message {message_id}: {e}",
                    extra={"errors": e.args, "message_id": message_id},
                )
                # Reject invalid messages directly to DLQ
                if channel.is_open:
                    channel.basic_reject(delivery_tag=delivery_tag, requeue=False)

            except Exception as e:
                logger.error(
                    f"Error processing message {message_id}: {e}",
                    extra={"message_id": message_id},
                )
                # Requeue message for retry
                if channel.is_open:
                    channel.basic_reject(delivery_tag=delivery_tag, requeue=True)

        except UnicodeDecodeError as e:
            logger.error(
                f"Failed to decode message {message_id}: {e}",
                extra={"message_id": message_id},
            )
            if channel.is_open:
                channel.basic_reject(delivery_tag=delivery_tag, requeue=False)

        except Exception as e:
            logger.error(
                f"Unexpected error processing message {message_id}: {e}",
                extra={"message_id": message_id},
            )
            if channel.is_open:
                channel.basic_reject(delivery_tag=delivery_tag, requeue=True)

    @abstractmethod
    def process_message(self, message_str: str) -> None:
        """Process a message from the queue.

        Args:
            message_str: The message body as a string
        """
        pass

    def stop_consuming(self) -> None:
        """Stop consuming messages and close the connection."""
        logger.info(f"Stopping consumer for queue: {self.queue_name}")
        self.should_stop = True
        self.is_consuming = False

        if self.channel and self._consumer_tag:
            try:
                self.channel.basic_cancel(self._consumer_tag)
            except Exception as e:
                logger.warning(f"Error canceling consumer: {e}")

        self._close_connection()
        self._closing_event.set()
        logger.info(f"Consumer stopped for queue: {self.queue_name}")

    def wait_for_shutdown(self, timeout: Optional[float] = None) -> bool:
        """Wait for the consumer to shut down.

        Args:
            timeout: Maximum time to wait in seconds or None to wait indefinitely

        Returns:
            True if the consumer shut down, False if timeout occurred
        """
        return self._closing_event.wait(timeout)

    def _close_connection(self) -> None:
        """Close the connection to RabbitMQ."""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()

            if self.connection and not self.connection.is_closed:
                self.connection.close()

        except Exception as e:
            logger.warning(f"Error closing connection: {e}")
        finally:
            self.channel = None
            self.connection = None
