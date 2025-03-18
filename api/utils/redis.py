import json
import redis
from contextlib import contextmanager
import os

@contextmanager
def redis_connection(db: int):
    r = redis.Redis(
        host=os.environ.get("REDIS_ADDRESS"),
        port=6379,
        username="default",
        password=os.environ.get("REDIS_PASSWORD"),
        db=db,
        socket_timeout=5  # Avoid hanging indefinitely
    )
    try:
        yield r
    finally:
        r.close()

def serialize_list(list_):
    return json.dumps(list_)