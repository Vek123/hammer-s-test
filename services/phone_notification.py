__all__ = ()

import asyncio
import os

from faststream import FastStream, Logger
from faststream import rabbit

RABBIT_USER = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
RABBIT_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')
RABBIT_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBIT_PORT = os.environ.get('RABBITMQ_PORT', '5672')

PHONE_NOTIFICATION_QUEUE = 'phone_notifications'

broker = rabbit.RabbitBroker(
    f'amqp://{RABBIT_USER}:{RABBIT_PASS}@{RABBIT_HOST}:{RABBIT_PORT}',
)
app = FastStream(broker)

queue = rabbit.RabbitQueue(PHONE_NOTIFICATION_QUEUE)


async def send_phone_msg(receivers: list[str], msg: str) -> None:
    await asyncio.sleep(1.5)
    print(f'Receivers: {receivers}; msg: {msg}')  # NoQA


@broker.subscriber(queue)
async def handle_phone_notification(logger: Logger, data: dict) -> None:
    receivers = data['receivers']
    msg = data['msg']
    await send_phone_msg(receivers, msg)
    logger.info('Phone notification has been processed')


async def main() -> None:
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
