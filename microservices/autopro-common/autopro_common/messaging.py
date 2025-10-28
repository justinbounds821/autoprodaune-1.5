"""
RabbitMQ messaging utilities with async support (aio-pika)
"""
import os
import json
from typing import Any, Callable, Dict, Optional, Union
from functools import wraps

import aio_pika
from aio_pika import Message, DeliveryMode, Connection, Channel, Queue
from aio_pika.abc import AbstractIncomingMessage

from .logging import get_logger

logger = get_logger(__name__)


class RabbitMQConnection:
    """RabbitMQ connection manager"""

    def __init__(self, amqp_url: str):
        """
        Initialize RabbitMQ connection
        
        Args:
            amqp_url: AMQP connection URL (amqp://user:pass@host:port/)
        """
        self.amqp_url = amqp_url
        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def close(self) -> None:
        """Close RabbitMQ connection"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("RabbitMQ connection closed")

    async def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
        auto_delete: bool = False,
    ) -> Queue:
        """
        Declare a queue
        
        Args:
            queue_name: Name of the queue
            durable: Queue survives broker restart
            auto_delete: Queue deleted when no consumers
            
        Returns:
            Declared queue
        """
        if not self.channel:
            raise RuntimeError("Channel not initialized. Call connect() first.")
        
        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable,
            auto_delete=auto_delete,
        )
        logger.info(f"Queue declared: {queue_name}")
        return queue


class RabbitMQProducer:
    """RabbitMQ message producer"""

    def __init__(self, connection: RabbitMQConnection):
        """
        Initialize producer
        
        Args:
            connection: RabbitMQ connection instance
        """
        self.connection = connection

    async def publish(
        self,
        queue_name: str,
        message: Union[Dict[str, Any], str],
        priority: int = 0,
        persistent: bool = True,
    ) -> bool:
        """
        Publish message to queue
        
        Args:
            queue_name: Target queue name
            message: Message payload (dict will be JSON serialized)
            priority: Message priority (0-9, higher = more priority)
            persistent: Message survives broker restart
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            if not self.connection.channel:
                raise RuntimeError("Channel not initialized")

            # Serialize message
            if isinstance(message, dict):
                body = json.dumps(message).encode()
            else:
                body = str(message).encode()

            # Create message
            msg = Message(
                body=body,
                delivery_mode=DeliveryMode.PERSISTENT if persistent else DeliveryMode.NOT_PERSISTENT,
                priority=priority,
            )

            # Publish to default exchange with routing key = queue name
            await self.connection.channel.default_exchange.publish(
                msg,
                routing_key=queue_name,
            )

            logger.debug(f"Published message to queue: {queue_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish message to {queue_name}: {e}")
            return False


class RabbitMQConsumer:
    """RabbitMQ message consumer"""

    def __init__(self, connection: RabbitMQConnection):
        """
        Initialize consumer
        
        Args:
            connection: RabbitMQ connection instance
        """
        self.connection = connection

    async def consume(
        self,
        queue_name: str,
        callback: Callable[[Dict[str, Any]], Any],
        auto_ack: bool = False,
    ) -> None:
        """
        Start consuming messages from queue
        
        Args:
            queue_name: Queue to consume from
            callback: Async function to handle messages (receives dict payload)
            auto_ack: Automatically acknowledge messages
        """
        try:
            # Declare queue
            queue = await self.connection.declare_queue(queue_name)

            logger.info(f"Started consuming from queue: {queue_name}")

            # Start consuming
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process(ignore_processed=auto_ack):
                        try:
                            # Deserialize message
                            payload = json.loads(message.body.decode())
                            
                            # Call handler
                            await callback(payload)
                            
                            logger.debug(f"Processed message from {queue_name}")
                            
                        except Exception as e:
                            logger.error(f"Error processing message from {queue_name}: {e}")
                            # Message will be rejected and requeued

        except Exception as e:
            logger.error(f"Error consuming from {queue_name}: {e}")
            raise


# Global RabbitMQ connection
_mq_connection: Optional[RabbitMQConnection] = None


async def init_rabbitmq(amqp_url: Optional[str] = None) -> RabbitMQConnection:
    """
    Initialize global RabbitMQ connection
    
    Args:
        amqp_url: AMQP URL (defaults to RABBITMQ_URL env var)
        
    Returns:
        Initialized RabbitMQConnection instance
    """
    global _mq_connection
    
    if amqp_url is None:
        amqp_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    _mq_connection = RabbitMQConnection(amqp_url)
    await _mq_connection.connect()
    
    return _mq_connection


def get_mq_connection() -> RabbitMQConnection:
    """
    Get global RabbitMQ connection
    
    Returns:
        RabbitMQConnection instance
        
    Raises:
        RuntimeError: If RabbitMQ not initialized
    """
    if _mq_connection is None:
        raise RuntimeError("RabbitMQ not initialized. Call init_rabbitmq() first.")
    return _mq_connection


def get_producer() -> RabbitMQProducer:
    """
    Get RabbitMQ producer instance
    
    Returns:
        RabbitMQProducer instance
    """
    connection = get_mq_connection()
    return RabbitMQProducer(connection)


def get_consumer() -> RabbitMQConsumer:
    """
    Get RabbitMQ consumer instance
    
    Returns:
        RabbitMQConsumer instance
    """
    connection = get_mq_connection()
    return RabbitMQConsumer(connection)
