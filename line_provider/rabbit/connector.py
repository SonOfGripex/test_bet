import aio_pika
from config import settings


class RabbitMQConnection:
    def __init__(self, amqp_url=settings.RABBITMQ_URL):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def __aenter__(self):
        try:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()
            return self
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
            return None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.close()


async def publish_message(rabbitmq_connection, queue_name, message):
    if not rabbitmq_connection or not rabbitmq_connection.channel:
        print("No RabbitMQ connection, message not sent.")
        return

    try:
        await rabbitmq_connection.channel.declare_queue(queue_name)
        await rabbitmq_connection.channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()), routing_key=queue_name
        )
        print(f"Sent message: {message} to queue {queue_name}")
    except Exception as e:
        print(f"Error publishing message: {e}")