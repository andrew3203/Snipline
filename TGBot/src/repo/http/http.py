import asyncio
import logging
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

import aiohttp
import httpx

from src.utils.exceptions import CoreException


logger = logging.getLogger(__name__)


def async_request():
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                async with httpx.AsyncClient() as client:
                    return await func(*args, client=client, **kwargs)
            except Exception as e:
                message = f"Failed to {func.__name__.upper()} response {str(e)}"
                logger.error(message)
                raise CoreException(msg=message, code=500) from e

        return wrapper

    return decorator


class HttpRepo:
    """
    This class is used to make http requests
    """

    @async_request()
    async def get(
        self,
        headers: dict[str, str],
        url: str,
        rise_error: bool = True,
        **kwargs,
    ) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.get(url, headers=headers, **kwargs)
        rise_error = kwargs.get("rise_error", True)
        if rise_error:
            response.raise_for_status()
        return response.json()

    @async_request()
    async def get_connent(
        self,
        headers: dict[str, str],
        url: str,
        rise_error: bool = True,
        **kwargs,
    ) -> Any:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.get(url, headers=headers, **kwargs)
        if rise_error:
            response.raise_for_status()
        return response.content

    @async_request()
    async def post(
        self,
        headers: dict[str, str],
        url: str,
        data: dict[str, Any],
        rise_error: bool = True,
        **kwargs,
    ) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.post(url, headers=headers, json=data, **kwargs)
        if rise_error:
            response.raise_for_status()
        return response.json()

    @async_request()
    async def post_content(
        self,
        headers: dict[str, str],
        url: str,
        data: dict[str, Any],
        rise_error: bool = True,
        **kwargs,
    ) -> Any:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.post(url, headers=headers, json=data, **kwargs)
        if rise_error:
            response.raise_for_status()
        return response.content

    @async_request()
    async def put(
        self,
        headers: dict[str, str],
        url: str,
        data: dict[str, Any],
        rise_error: bool = True,
        **kwargs,
    ) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.put(url, headers=headers, json=data, **kwargs)
        if rise_error:
            response.raise_for_status()
        return response.json()

    @async_request()
    async def delete(
        self,
        headers: dict[str, str],
        url: str,
        rise_error: bool = True,
        **kwargs,
    ) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.delete(url, headers=headers, **kwargs)
        rise_error = kwargs.get("rise_error", True)
        if rise_error:
            response.raise_for_status()
        return response.json()

    async def fetch_image(self, url: str, try_count: int = 3) -> bytes:
        for try_number in range(try_count):
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        content = await response.read()
                        return content
            except Exception as e:
                if try_number + 1 == try_count:
                    raise CoreException(msg=f"Failed to fetch image: {str(e)}\n url: {url}", status_code=500) from e
                await asyncio.sleep(5)
        else:
            raise CoreException(msg=f"Failed to fetch image: try_count=0\n url: {url}", status_code=500)
