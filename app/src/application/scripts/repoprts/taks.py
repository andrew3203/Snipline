import asyncio
from datetime import datetime, UTC, timedelta
import logging

from apscheduler.triggers.cron import CronTrigger

from src.application.scripts.repoprts.report_generator import ReportGenerator
from src.repository.redis import RedisConnector
from ..base_taks import BaseTask

logger = logging.getLogger(__name__)


class ReportTask(BaseTask):
    def __init__(self, trigger: CronTrigger, name: str, **kwargs):
        self._name = name
        self._trigger = trigger
        self.connector = RedisConnector(
            stream_name="notifications",
            stop_event=asyncio.Event(),
        )
        self.generator = ReportGenerator()
        self.kwargs = kwargs or {}

    async def handle(self):
        await self.connector.start_push()
        try:
            await self.generator.generate_reports(
                date_from=datetime.now(UTC) - timedelta(hours=self.kwargs.get("h", 12)),
                redis_connector=self.connector,
            )
        except Exception as e:
            logger.error(f"Task error {str(e)}")
        await self.connector.stop()

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
