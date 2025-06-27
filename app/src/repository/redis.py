import json
import logging
from uuid import uuid4
from typing import Any, Awaitable, Callable

import asyncio
from redis.asyncio import Redis, ConnectionPool
from config.settings import settings

logger = logging.getLogger(__name__)


class RedisConnector:
    def __init__(self, stream_name: str, stop_event: asyncio.Event):
        self.stream_name = stream_name
        self.group_name = f"{stream_name}_g"
        self.worker_name = f"{stream_name}_w_{str(uuid4())[:5]}"
        self.stop_event = stop_event
        self._queue: asyncio.Queue = asyncio.Queue()
        self.task1: asyncio.Task | None = None
        self.task2: asyncio.Task | None = None

        self.redis = Redis(
            connection_pool=ConnectionPool.from_url(
                url=settings.REDIS_URL,
                max_connections=2,
                socket_timeout=110,
                db=0,
                encoding="utf-8",
                socket_connect_timeout=110,
                health_check_interval=25,
                retry_on_timeout=True,
                decode_responses=True,
            )
        )

    async def _ensure_group_exists(self):
        try:
            await self.redis.xgroup_create(
                self.stream_name, self.group_name, id="0", mkstream=True
            )
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                logger.error(
                    f"🔴 Error creating Redis stream group: {e}", exc_info=True
                )

    async def proccess_read_loop(
        self, handle: Callable[[list[dict]], Awaitable[bool]], count: int = 1
    ):
        async def _handle(data_raw: str | None | dict, msg_id: str):
            try:
                if not data_raw:
                    logger.warning("Error in message handler")
                    return
                data_raw_ = (
                    data_raw
                    if isinstance(data_raw, str)
                    else list(data_raw.values())[0]
                )
                parsed = json.loads(data_raw_)
                success = await handle(parsed)
                if success:
                    await self.redis.xack(self.stream_name, self.group_name, msg_id)
            except Exception as e:
                logger.error(f"⚠️ Error in message handler: {e}", exc_info=True)

        await self._ensure_group_exists()
        block_ms = 100_000  # 100 seconds
        try:
            messages = await self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.worker_name,
                streams={self.stream_name: ">"},
                count=count,
                block=block_ms,
            )

            for _, entries in messages:
                for msg_id, data in entries:
                    key = data.get("key")
                    if not key or key is None:
                        await _handle(data_raw=data, msg_id=msg_id)
                        continue

                    data_raw = await self.redis.get(key)
                    await _handle(data_raw=data_raw, msg_id=msg_id)

        except Exception as e:
            logger.error(f"🔴 Redis read loop error: {e}", exc_info=True)
            await asyncio.sleep(2)

    async def _read_loop(
        self, handle: Callable[[list[dict]], Awaitable[bool]], count: int = 1
    ):
        while not self.stop_event.is_set():
            await self.proccess_read_loop(handle=handle, count=count)

    async def xadd(self, data: Any):
        if data and len(data) > 0:
            await self._queue.put(data)
        else:
            logger.warning(f"Empty data was not pushed, to {self.stream_name}")

    async def send_msg(self, data: Any):
        await self.redis.xadd(self.stream_name, data, maxlen=10000, approximate=True)
        logger.info(f"Sent {len(data)} articles to redis")

    async def _push_loop(self):
        while not self.stop_event.is_set():
            data = await self._queue.get()
            if data is None:
                break
            try:
                await self.redis.xadd(
                    self.stream_name, data, maxlen=10000, approximate=True
                )
                logger.info(f"Sent {len(data)} articles to redis")
            except Exception as e:
                logger.error(f"🔴 Redis error: {e}", exc_info=True)

    async def start_push(self):
        self.task2 = asyncio.create_task(self._push_loop())

    async def start_read(
        self, handle: Callable[[dict], Awaitable[bool]], count: int = 1
    ):
        self.task1 = asyncio.create_task(self._read_loop(handle, count=count))

    async def stop(self):
        self.stop_event.set()
