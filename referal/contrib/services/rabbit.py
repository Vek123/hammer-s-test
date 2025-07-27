__all__ = ()

from contextlib import contextmanager
import json

from django.conf import settings
import pika


PHONE_NOTIFICATION_QUEUE = 'phone_notifications'

conn_params = pika.ConnectionParameters(
    settings.RABBITMQ_HOST,
    settings.RABBITMQ_PORT,
    credentials=pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD,
    ),
    connection_attempts=5,
    retry_delay=1,
)


@contextmanager
def get_connection():
    conn = pika.BlockingConnection(conn_params)
    yield conn
    conn.close()


@contextmanager
def get_rabbit(queue_name: str):
    with get_connection() as conn:
        ch = conn.channel()
        ch.queue_declare(queue_name)
        yield ch
        ch.close()


class PhoneNotificationRabbit:
    queue = PHONE_NOTIFICATION_QUEUE

    @classmethod
    def publish(cls, receivers, msg):
        with get_rabbit(cls.queue) as rabbit:
            data = {'receivers': receivers, 'msg': msg}
            rabbit.basic_publish(
                exchange='',
                routing_key=cls.queue,
                body=json.dumps(data),
            )
