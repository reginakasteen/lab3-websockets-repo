import redis
from django.conf import settings

redis_client = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)

ONLINE_USERS_KEY = "online_users"


def add_user_online(user_id):
    redis_client.sadd(ONLINE_USERS_KEY, user_id)


def remove_user_online(user_id):
    redis_client.srem(ONLINE_USERS_KEY, user_id)


def get_online_users():
    return [int(uid) for uid in redis_client.smembers(ONLINE_USERS_KEY)]
