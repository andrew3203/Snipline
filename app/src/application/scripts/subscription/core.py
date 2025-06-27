import asyncio
from datetime import datetime, UTC, timedelta
from typing import Literal

from sqlmodel import select, col

from src.db import get_async_session
from src.models.subscription import UserSubscription
from src.repository.redis import RedisConnector


class CoreSubscription:
    def __init__(self, connector: RedisConnector):
        self._queue = asyncio.Queue[UserSubscription]()
        self._connector = connector
        self._event = asyncio.Event()
        self.task: asyncio.Task | None = None

    async def check_subscriptions(self):
        async for session in get_async_session():
            start_date = datetime.now(UTC) - timedelta(hours=1)
            end_date = datetime.now(UTC) + timedelta(hours=1)
            items_raw = await session.exec(
                select(UserSubscription).where(
                    col(UserSubscription.end_date).between(start_date, end_date),
                    col(UserSubscription.is_active).is_(True),
                )
            )
            for item in items_raw.all():
                await self._queue.put(item)

    async def check_gift_promo(self):
        async for session in get_async_session():
            start_date = datetime.now(UTC) - timedelta(days=1, hours=1)
            end_date = datetime.now(UTC) + timedelta(hours=23)
            items_raw = await session.exec(
                select(UserSubscription).where(
                    col(UserSubscription.end_date).between(start_date, end_date),
                    col(UserSubscription.is_active).is_(False),
                )
            )
            for item in items_raw.all():
                await self.gift_promo(item=item)

    async def check_day_subscriptions(self):
        async for session in get_async_session():
            start_date = datetime.now(UTC) + timedelta(hours=23)
            end_date = datetime.now(UTC) + timedelta(days=1, hours=1)
            items_raw = await session.exec(
                select(UserSubscription).where(
                    col(UserSubscription.end_date).between(start_date, end_date),
                    col(UserSubscription.is_active).is_(True),
                )
            )
            items = items_raw.all()
        for item in items:
            await self.send_notification(item=item, key="expires_in_day")

    async def send_notification(
        self,
        item: UserSubscription,
        key: Literal["expires_in_day", "expired"],
    ) -> None:
        await self._connector.xadd(
            data={
                "mode": "node",
                "user_id": item.user_id,
                "flow_key": "subscription_notification",
                "key": key,
            }
        )

    async def gift_promo(self, item: UserSubscription) -> None:
        pass

    async def cancel_subscription(self, item: UserSubscription) -> None:
        async for session in get_async_session():
            model_raw = await session.exec(
                select(UserSubscription).where(UserSubscription.id == item.id)
            )
            model = model_raw.one()
            model.is_active = False
            session.add(model)
            await session.commit()

    async def start_check(self):
        while not self._event.is_set():
            item = await self._queue.get()
            if item.end_date >= datetime.now(UTC):
                await self.cancel_subscription(item=item)
                await self.send_notification(item=item, key="expired")
            else:
                await self._queue.put(item)
                await asyncio.sleep(10)

    async def start(self):
        self.task = asyncio.create_task(self.start_check())

    async def stop(self):
        self._event.set()
        if self.task:
            await self.task
