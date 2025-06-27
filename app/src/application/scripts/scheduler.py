from datetime import UTC
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.application.scripts.repoprts.taks import ReportTask
from src.application.scripts.alert_news.taks import NewsAlertTask
from src.application.scripts.subscription.taks import SubscriptionTask


from .base_taks import BaseTask


class Scheduler:
    def __init__(self, tasks: list[BaseTask]):
        self.scheduler = AsyncIOScheduler()
        self.tasks = tasks

    def setup_jobs(self):
        for taks in self.tasks:
            self.scheduler.add_job(
                func=taks.handle,
                name=taks.name,
                trigger=taks.trigger,
                misfire_grace_time=30,
                max_instances=1,
            )

    async def start(self):
        for task in self.tasks:
            await task.start()
        self.setup_jobs()
        self.scheduler.start()

    async def shutdown(self, wait: bool = False):
        self.scheduler.shutdown(wait=wait)
        for task in self.tasks:
            await task.stop()


async def run():
    tasks = [
        ReportTask(
            trigger=CronTrigger(hour=7, minute=0, timezone=UTC),
            name="morning_report",
            h=12,
        ),
        ReportTask(
            trigger=CronTrigger(hour=17, minute=0, timezone=UTC),
            name="evening_reports",
            h=12,
        ),
        NewsAlertTask(
            trigger=CronTrigger(minute="*/5", timezone=UTC), name="alert_news"
        ),
        SubscriptionTask(
            trigger=CronTrigger(minute=0, timezone=UTC), name="subscription"
        ),
    ]
    scheduler = Scheduler(tasks=tasks)
    await scheduler.start()
    return scheduler
