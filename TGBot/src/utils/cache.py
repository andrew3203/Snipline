import asyncio
import json
import time
from collections import OrderedDict
from pydantic import BaseModel
from functools import wraps
from typing import Any, Generic, TypeVar

Value = TypeVar("Value")

class AsyncLRUCache(Generic[Value]):
    def __init__(self, max_age: int, maxsize: int, model_class: type[Value]):
        self.cache: OrderedDict[Any, Value] = OrderedDict()
        self.max_age = max_age
        self.maxsize = maxsize
        self.lock = asyncio.Lock()
        self.model_class = model_class

    def __len__(self) -> int:
        return len(self.cache)

    async def __get__(self, key: Any) -> Value | None:
        return await self.get(key=key)

    async def __set__(self, key: Any, value: Value) -> None:
         return await self.set(key=key, value=value)

    async def get(self, key: Any) -> Value | None:
        async with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.max_age:
                    self.cache.move_to_end(key)
                    return value
                else:
                    del self.cache[key]
            return None

    async def set(self, key: Any, value: Value) -> None:
        async with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = (value, time.time())
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)
    
    async def mset(self, data: dict[str, str]) -> None:
        async with self.lock:
            for k, v in data.items():
                data = self.model_class.model_validate_json(v)
                value = data
                self.cache[k] = (value, time.time())
    
    async def dumps(self) -> dict[str, str]:
        async with self.lock:
            return {
                k: v[0].model_dump_json() if isinstance(v[0], BaseModel) else json.dumps(v[0])
                for k, v in self.cache.items()
            }
    async def dumps_keys(self) -> str:
        async with self.lock:
            return json.dumps(list(self.cache.keys()))



def async_lru_cache(max_age: int = 60, maxsize: int = 128):
    """
    Decorator that implements an async LRU cache.
    - different cache for each class instances

    :param max_age: The maximum age of an item in the cache in seconds.
    :param maxsize: The maximum size of the cache (count of items).
    """
    cache = AsyncLRUCache[dict](max_age, maxsize)

    def decorator(fn):
        @wraps(fn)
        async def wrapped(*args, **kwargs):
            """
            Check the cache for a result, and if not found, call the function
            and store the result in the cache.
            """

            hashable_kwargs = {}
            for key, value in kwargs.items():
                try:
                    if isinstance(value, list):
                        for v in value:
                            hash(v)
                        value = tuple(value)

                    hash(value)
                    hashable_kwargs[key] = value
                except TypeError:
                    continue

            cache_key = (args, frozenset(hashable_kwargs.items()))
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            result = await fn(*args, **kwargs)
            await cache.set(cache_key, result)
            return result

        return wrapped

    return decorator
