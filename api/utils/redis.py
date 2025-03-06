import json
import redis
from contextlib import contextmanager

@contextmanager
def redis_connection(db: int):
    r = redis.Redis(host="redis", port=6379, db=db)
    try:
        yield r
    finally:
        r.close()

def serialize_list(list_):
    return json.dumps(list_)

