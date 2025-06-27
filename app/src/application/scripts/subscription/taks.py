import asyncio
import logging

from apscheduler.triggers.cron import CronTrigger

from src.application.scripts.subscription.core import CoreSubscription
from src.repository.redis import RedisConnector
from ..base_taks import BaseTask

logger = logging.getLogger(__name__)


class SubscriptionTask(BaseTask):
    def __init__(self, trigger: CronTrigger, name: str, **kwargs):
        self._name = name
        self._trigger = trigger
        self.connector = RedisConnector(
            stream_name="notifications",
            stop_event=asyncio.Event(),
        )
        self.core = CoreSubscription(connector=self.connector)

    async def handle(self):
        await self.core.check_day_subscriptions()
        await self.core.check_subscriptions()
        await self.core.check_gift_promo()

    async def start(self):
        await self.connector.start_push()
        await self.core.start()

    async def stop(self):
        await self.core.stop()
        await self.connector.stop()

    @property
    def name(self) -> str:
        return self._name

    @property
    def trigger(self) -> CronTrigger:
        return self._trigger
