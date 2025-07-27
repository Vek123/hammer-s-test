__all__ = ()

import re

from django.conf import settings
from django.utils import timezone


class Redis:
    def __init__(self):
        self.storage = {}

    def _check_expired(self, key, value):
        if value['expire'] < timezone.now():
            self.storage.pop(key, None)
            return True

        return False

    def set_val(self, key, val, expire_time):
        self.storage[key] = {
            'val': val,
            'expire': timezone.now() + timezone.timedelta(seconds=expire_time),
        }

    def get(self, key):
        value = self.storage.get(key)
        if not value:
            return None

        if self._check_expired(key, value):
            return None

        return value['val']

    def mget(self, keys):
        res = []
        for key in keys:
            res.append(self.get(key))

        return res

    def getdel(self, key):
        value = self.storage.pop(key, None)
        if not value:
            return None

        if self._check_expired(key, value):
            return None

        return value['val']

    def scan(self, match):
        match = re.compile(match)
        keys = []
        for key, value in [*self.storage.items()]:
            if self._check_expired(key, value):
                continue

            if match.fullmatch(key):
                keys.append(key)

        return keys


class PhoneUserConfirmRedis:
    list_name = 'code_user_phone_confirm'
    key_format = f'{list_name}:%(code)s'

    def __init__(self):
        self.redis = Redis()

    def publish(self, user_id: int, code: str):
        key = self.key_format % {'code': code}
        self.redis.set_val(
            key,
            user_id,
            settings.REDIS_USER_PHONE_EXPIRATION_TIME,
        )

    def list_codes(self):
        match = f'{self.list_name}:.*'
        keys = self.redis.scan(match)
        return [key.split(':')[1] for key in keys]

    def get(self, code: str):
        key = self.key_format % {'code': code}
        return self.redis.getdel(key)
