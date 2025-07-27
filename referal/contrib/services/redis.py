__all__ = ()

from contextlib import contextmanager

from django.conf import settings
import redis


pool = None


def get_pool():
    global pool
    if pool:
        return pool

    pool = redis.ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        username=settings.REDIS_USER,
        password=settings.REDIS_USER_PASSWORD,
    )
    return pool  # NoQa


@contextmanager
def get_redis():
    pool = get_pool()
    with redis.Redis(connection_pool=pool) as r:
        yield r
        r.close()


class PhoneUserConfirmRedis:
    expire = settings.REDIS_USER_PHONE_EXPIRATION_TIME
    list_name = 'code_user_phone_confirm'
    key_format = f'{list_name}:%(code)s'

    @classmethod
    def publish(cls, user_id: int, code: str):
        key = cls.key_format % {'code': code}
        with get_redis() as r:
            r.set(key, user_id, cls.expire)

    @classmethod
    def list_codes(cls):
        with get_redis() as r:
            cursor = 0
            keys = []
            while True:
                cursor, partial_keys = r.scan(
                    cursor=cursor,
                    match=f'{cls.list_name}:*',
                )
                keys.extend(partial_keys)
                if cursor == 0:
                    break

            return r.mget(keys)

    @classmethod
    def get(cls, code: str):
        key = cls.key_format % {'code': code}
        with get_redis() as r:
            return r.getdel(key)
