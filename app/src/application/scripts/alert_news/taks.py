import asyncio
import logging

from apscheduler.triggers.cron import CronTrigger

from src.repository.redis import RedisConnector
from ..base_taks import BaseTask

logger = logging.getLogger(__name__)


async def read(data: dict):
    logger.info("Alert news")


class NewsAlertTask(BaseTask):
    def __init__(self, trigger: CronTrigger, name: str, **kwargs):
        self._name = name
        self._trigger = trigger
        self.connector = RedisConnector(
            stream_name="news",
            stop_event=asyncio.Event(),
        )

    async def handle(self):
        await self.connector.proccess_read_loop(read, count=100)

    async def start(self):
        pass

    async def stop(self):
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def trigger(self) -> CronTrigger:
        return self._trigger
