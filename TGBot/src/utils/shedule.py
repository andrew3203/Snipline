from typing import Any, Callable, Coroutine, TypeVar
import asyncio
import functools


F = TypeVar('F', bound=Callable[..., Coroutine[Any, Any, Any]])

def schedule_coroutine(
    delay: float,
    coro: F,
    *args: Any,
    **kwargs: Any
) -> None:
    """
    Schedule `coro(*args, **kwargs)` to run after `delay` seconds.
    """
    loop = asyncio.get_running_loop()
    loop.call_later(
        delay,
        lambda: asyncio.create_task(coro(*args, **kwargs))
    )

def delayed(delay: float) -> Callable[[F], Callable[..., None]]:
    """
    Decorator factory to schedule an async function to run after `delay` seconds
    instead of running it immediately.
    """
    def decorator(func: F) -> Callable[..., None]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> None:
            if delay > 0:
                schedule_coroutine(delay, func, *args, **kwargs)
            else:
                asyncio.create_task(func(*args, **kwargs))
        return wrapper  # type: ignore
    return decorator
