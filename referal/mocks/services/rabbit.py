__all__ = ()


from collections import defaultdict, deque

from contrib.services.rabbit import PHONE_NOTIFICATION_QUEUE


class Rabbit:
    def __init__(self):
        self.queues = defaultdict(deque)

    def publish(self, queue_name, data):
        self.queues[queue_name].append(data)

    def pop(self, queue_name):
        self.queues[queue_name].popleft()


class PhoneNotificationRabbit:
    queue = PHONE_NOTIFICATION_QUEUE

    def __init__(self):
        self.rabbit = Rabbit()

    def publish(self, receivers, msg):
        data = {'receivers': receivers, 'msg': msg}
        self.rabbit.publish(self.queue, data)
