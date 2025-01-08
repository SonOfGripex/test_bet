import aio_pika
import json
import asyncio
from config import settings
from bets.services import update_bet_status


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        body = message.body.decode()
        print(f"Message: {body}")
        try:
            await update_bet_status(json.loads(body))
        except Exception as e:
            print(f'Error: {e}')


async def consume_messages(queue_name):
    try:
        connection = await aio_pika.connect_robust(
            settings.RABBITMQ_URL
        )
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(queue_name)

            await queue.consume(process_message)

            print(f"Messages waiting from {queue_name}...")
            await asyncio.Future()
    except Exception as e:
        print(f"Error: {e}")