import json
import logging
import threading
import queue
from typing import Any, Callable
from uuid import uuid4

from redis import ConnectionPool, Redis
from src.config import settings
from src.utils.serialise import to_json_list



logger = logging.getLogger(__name__)


class RedisConnector:
    __slots__ = (
        "q",
        "stream_name",
        "group_name",
        "worker_name",
        "ex",
        "redis",
        "redis_thread",
        "read_redis_thread",
        "read_event",
        "push_event",
    )

    def __init__(self, stream_name: str, event: threading.Event):
        self.q = queue.Queue()
        self.stream_name = stream_name
        self.group_name = f"{stream_name}_g"
        self.worker_name = f"{stream_name}_w_{str(uuid4())[:5]}"
        self.ex = 60 * 60 * 24 * 4
        
        pool = ConnectionPool.from_url(
            url=settings.REDIS_URL,
            max_connections=5,
            socket_timeout=30,
            db=0,
            encoding="utf-8",
            socket_connect_timeout=20,
            health_check_interval=30,
            retry_on_timeout=True,
            decode_responses=True,
        )
        self.redis = Redis(connection_pool=pool)
        self.redis_thread = None
        self.read_redis_thread = None
        self.read_event = event
        self.push_event = threading.Event()
    
    def xadd(self, data: Any):
        if data:
            self.q.put(data)
    
    def start_reading(self, handle: Callable):
        try:
            self.redis.xgroup_create(self.stream_name, self.group_name, id="0", mkstream=True)
        except Exception:
            pass
        
        def read():
            block = 1 * 60 * 100
            while not self.read_event.is_set():
                try:
                    messages = self.redis.xreadgroup(
                        self.group_name, self.worker_name,
                        {self.stream_name: ">"},
                        block=block,
                        count=5,
                    )
                    for _, entries in messages:
                        for msg_id, data in entries:
                            key = data["key"]
                            data_raw = self.redis.get(key)
                            if not data_raw:
                                logger.warning(f"⚠️ No Data found for key: {key}")
                                continue
                            try:
                                parsed = json.loads(data_raw)
                                if handle(parsed):
                                    self.redis.xack(self.stream_name, self.group_name, msg_id)
                            except Exception as inner_e:
                                logger.error(f"⚠️ Error in message handler: {inner_e}", exc_info=True)

                except Exception as e:
                    logger.error(f"🔴 Redis read error: {e}", exc_info=True)

        self.read_redis_thread = threading.Thread(target=read, daemon=True)
        self.read_redis_thread.start()
    
    def stop_reading(self):
        if self.read_redis_thread:
            self.read_event.set()
            self.read_redis_thread.join()

    def send_msg(self, data: Any):
        key = f"{uuid4()}-{len(data)}"
        value = to_json_list(data)
        self.redis.set(key, value, ex=self.ex)
        self.redis.xadd(self.stream_name, {"key": key}, maxlen=10000, approximate=True)
        logger.info(f"Sent {len(data)} articles to redis")

    def redis_worker(self):
        while not self.push_event.is_set():
            data = self.q.get()
            if data is None:
                break
            try:
                self.send_msg(data=data)
            except Exception as e:
                logger.error(f"🔴 Redis error: {e}", exc_info=True)

    def start(self):
        self.redis_thread = threading.Thread(target=self.redis_worker, daemon=True)
        self.redis_thread.start()

    def stop(self):
        if self.redis_thread:
            self.push_event.set()
            self.q.put(None)
            self.redis_thread.join()