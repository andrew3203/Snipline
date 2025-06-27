from datetime import datetime
import logging
from typing import Any

from sqlmodel import select, col, and_, func, BOOLEAN
from sqlmodel.ext.asyncio.session import AsyncSession

from src.application.llm.report import LLMReport
from src.db import get_async_session, get_async_session_t
from src.models.filters import UserFilter
from src.models.news import NewsItem
from src.models.report import NewsReport
from src.repository.redis import RedisConnector

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self):
        self.llm = LLMReport()

    async def fetch_filter_results(
        self, session: AsyncSession, filter_dict: dict, date_from: datetime
    ) -> set[int]:
        query = select(NewsItem.id).where(
            and_(col(NewsItem.is_ready).is_(True), NewsItem.published_at >= date_from)
        )

        if category := filter_dict.get("category"):
            query = query.where(NewsItem.category == category)
        if subcats := filter_dict.get("subcategories"):
            query = query.where(func.jsonb_exists_any(NewsItem.subcategories, subcats))
        if comps := filter_dict.get("companies"):
            query = query.where(func.jsonb_exists_any(NewsItem.companies, comps))
        if locs := filter_dict.get("locations"):
            query = query.where(func.jsonb_exists_any(NewsItem.locations, locs))
        if names := filter_dict.get("names"):
            query = query.where(func.jsonb_exists_any(NewsItem.names, names))
        if prios := filter_dict.get("priority"):
            query = query.where(col(NewsItem.priority).in_(prios))

        result = await session.exec(query)
        return set(result.scalars().all())

    async def get_active_user_filters(self, session: AsyncSession) -> list[UserFilter]:
        stmt = select(UserFilter).where(
            func.cast(UserFilter.filters["is_active"], BOOLEAN).is_(True)
        )
        result = await session.exec(stmt)
        return result.all()

    async def deduplicate_filters(
        self, session: AsyncSession, date_from: datetime
    ) -> list[dict[str, Any]]:
        all_filters = await self.get_active_user_filters(session)
        seen_map: dict[frozenset, dict] = {}

        for group in all_filters:
            filters = group.filters
            news_ids = await self.fetch_filter_results(session, filters, date_from)
            key = frozenset(news_ids)
            lang = filters.get("answer_lang", "en")

            if key not in seen_map:
                seen_map[key] = {
                    "news_ids": list(news_ids),
                    "filter_ids": [group.id],
                    "user_ids": [group.user_id],
                    "answer_langs": [lang],
                }
            else:
                seen_map[key]["filter_ids"].append(group.id)
                if group.user_id not in seen_map[key]["user_ids"]:
                    seen_map[key]["user_ids"].append(group.user_id)
                if lang not in seen_map[key]["answer_langs"]:
                    seen_map[key]["answer_langs"].append(lang)

        return list(seen_map.values())

    async def _get_data(self, date_from: datetime) -> list[dict]:
        data = []
        async for session in get_async_session():
            results = await self.deduplicate_filters(session, date_from)
            for entry in results:
                news_stmt = select(NewsItem).where(
                    col(NewsItem.id).in_(entry["news_ids"])
                )
                news_result = await session.exec(news_stmt)
                news_list = news_result.all()
                data.append(
                    {
                        "news_list": news_list,
                        "entry": entry,
                    }
                )
        return data

    async def _save_data(self, models: list[NewsReport]) -> None:
        async for session in get_async_session_t():
            for m in models:
                session.add(m)
            await session.commit()

    async def generate_reports(
        self,
        date_from: datetime,
        redis_connector: RedisConnector,
    ) -> None:
        data = await self._get_data(date_from=date_from)
        models = []
        for item in data:
            entry = item["entry"]
            for lang in entry["answer_langs"]:
                content = await self.llm.get_report(
                    data=item["news_list"], answer_lang=lang
                )
                for filter_id in entry["filter_ids"]:
                    for user_id in entry["user_ids"]:
                        report = NewsReport(
                            content=content,
                            lang=lang,
                            news_ids=entry["news_ids"],
                            filter_id=filter_id,
                            user_id=user_id,
                            reaction=0,
                            delivered_at=None,
                        )
                        models.append(report)

                        payload = {
                            "user_id": user_id,
                            "news_count": len(entry["news_ids"]),
                            "content": content,
                            "mode": "raw",
                        }
                        logger.info(f"Pushed {payload=}")
                        await redis_connector.xadd(payload)

        await self._save_data(models=models)
