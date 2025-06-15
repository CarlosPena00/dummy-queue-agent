#!/usr/bin/env python3
"""Script to publish test messages to RabbitMQ queues."""

import argparse
import json
import sys
from typing import Any

import pika


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Publish a test message to RabbitMQ")
    parser.add_argument(
        "--host", default="localhost", help="RabbitMQ host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=5672, help="RabbitMQ port (default: 5672)"
    )
    parser.add_argument(
        "--user", default="guest", help="RabbitMQ username (default: guest)"
    )
    parser.add_argument(
        "--password", default="guest", help="RabbitMQ password (default: guest)"
    )
    parser.add_argument(
        "--queue",
        default="products",
        choices=["products", "stocks", "prices"],
        help="Queue to publish to (default: products)",
    )
    parser.add_argument(
        "--product-code",
        default=f"TEST-{__import__('uuid').uuid4().hex[:8].upper()}",
        help="Product code to use (default: random)",
    )
    return parser.parse_args()


def get_sample_message(queue_name: str, product_code: str) -> dict[str, Any]:
    """Get a sample message based on the queue name."""
    if queue_name == "products":
        return {
            "product_code": product_code,
            "collection": "products",
            "name": f"Test Product {product_code}",
            "description": "This is a test product",
            "category": "Test Category",
            "brand": "TestBrand",
            "price": 99.99,
            "currency": "USD",
            "sku": f"SKU-{product_code}",
            "created_at": f"{__import__('datetime').datetime.now().isoformat()}",
            "updated_at": f"{__import__('datetime').datetime.now().isoformat()}",
        }
    elif queue_name == "stocks":
        return {
            "product_code": product_code,
            "collection": "stocks",
            "quantity": 100,
            "warehouse_id": "WH-MAIN",
            "location": "A1-B2-C3",
            "updated_at": f"{__import__('datetime').datetime.now().isoformat()}",
        }
    elif queue_name == "prices":
        return {
            "product_code": product_code,
            "collection": "prices",
            "price": 99.99,
            "currency": "USD",
            "effective_date": f"{__import__('datetime').datetime.now().isoformat()}",
            "expires_at": f"{
                __import__('datetime')
                .datetime.now()
                .replace(year=__import__('datetime').datetime.now().year + 1)
                .isoformat()
            }",
            "promotion_id": None,
        }
    else:
        raise ValueError(f"Unknown queue name: {queue_name}")


def main() -> None:
    """Publish a test message to RabbitMQ."""
    args = parse_args()

    # Generate the test message
    product_code = args.product_code
    queue_name = args.queue
    message = get_sample_message(queue_name, product_code)

    # Print the message
    print(f"Publishing to queue '{queue_name}':")
    print(json.dumps(message, indent=2))

    # Connect to RabbitMQ
    try:
        connection_params = pika.ConnectionParameters(
            host=args.host,
            port=args.port,
            credentials=pika.PlainCredentials(args.user, args.password),
        )
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        # Ensure the queue exists
        channel.queue_declare(queue=queue_name, durable=True)

        # Publish the message
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent message
                content_type="application/json",
            ),
        )

        print(f"Message published successfully to '{queue_name}' queue")
        connection.close()

    except Exception as e:
        print(f"Error publishing message: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
