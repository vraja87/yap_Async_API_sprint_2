import json
from functools import wraps

from db.redis import get_redis


def redis_cache(expire: int = 60):
    """
    Redis caching decorator for asynchronous functions.

    This decorator caches the result of a function call in Redis with a specified expiry time.
    The cache key is generated from the function name, arguments, and keyword arguments.

    :param expire: The time-to-live (TTL) of the cache in seconds. Default is 60.
    :return: The cached result, or the result of the function call if not in cache.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            self_or_none = args[0] if args else None
            is_method = self_or_none is not None and hasattr(self_or_none, '__class__')
            if is_method:
                key_prefix = f"{self_or_none.__class__.__name__}:{func.__name__}:{self_or_none.index}"
            else:
                key_prefix = f"{func.__name__}"

            key = f"{key_prefix}:{args[1:] if is_method else args}:{kwargs}"

            redis = await get_redis()
            cached_value = await redis.get(key)
            if cached_value:
                return json.loads(cached_value)

            result = await func(*args, **kwargs)
            await redis.set(name=key, value=json.dumps(result), ex=expire)
            return result
        return wrapper
    return decorator
