import redis
from django.conf import settings


class Redis(object):
    def __init__(self):
        self.pool_connection = redis.ConnectionPool(
            host=settings.REDIS['default']['HOST'],
            port=settings.REDIS['default']['PORT'],
            password=settings.REDIS['default']['PASSWORD']
        )
        self.connection = redis.StrictRedis(connection_pool=self.pool_connection)

    def redis_add_refresh_token(self, username, refresh_token, *args, **kwargs):
        self.connection.select(0)
        self.connection.set(refresh_token, username, int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].seconds))
        self.connection.close()
        return True

    def redis_get_refresh_token(self, refresh_token, *args, **kwargs):
        self.connection.select(0)
        refresh = self.connection.get(refresh_token)
        self.connection.close()
        return refresh

    def redis_delete_refresh_token(self, refresh_token, *args, **kwargs):
        self.connection.select(0)
        self.connection.delete(refresh_token)
        self.connection.close()
        return True

    def redis_set_new_refresh_token(self, new_refresh_token, old_refresh_token, username, *args, **kwargs):
        self.connection.select(0)
        self.connection.delete(old_refresh_token)
        self.connection.set(new_refresh_token, username, int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].seconds))
        self.connection.close()
        return True

    def redis_check_exists_refresh_token(self, refresh_token, *args, **kwargs):
        self.connection.select(0)
        refresh = self.connection.get(refresh_token)
        self.connection.close()
        if refresh:
            return True
        return False
