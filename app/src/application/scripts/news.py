import asyncio
from datetime import datetime, UTC
import logging

from src.application.llm.summarize import LLMSummarize
from src.application.services.catogory import NewsCategoryService
from src.repository.redis import RedisConnector
from src.db import get_async_session
from src.models import NewsItem

logger = logging.getLogger(__name__)


async def create_items(articles: list[dict]) -> list[NewsItem]:
    article_items: list[NewsItem] = []
    async for session in get_async_session():
        for a in articles:
            item = NewsItem(
                title=a["article"]["title"],
                content=a["article"]["text"],
                summary="",
                source_url=a["link"],
                lang=a["lang"],
                category=None,
                subcategories=[],
                companies=[],
                locations=[],
                names=[],
                priority=0,
                is_ready=False,
                published_at=datetime.fromisoformat(a["published"]),
                created_at=datetime.now(UTC),
            )
            session.add(item)
            article_items.append(item)
        await session.commit()

    return article_items


async def build_translation_lookup() -> NewsCategoryService:
    async for session in get_async_session():
        service = NewsCategoryService()
        await service.on_load(session=session)
        return service


async def update_items(
    article_items: list[NewsItem],
    catogory_service: NewsCategoryService,
) -> tuple[list[NewsItem], int]:
    service = LLMSummarize()
    logger.info("Start updatings news")
    redis_connector = RedisConnector(stream_name="news", stop_event=asyncio.Event())
    await redis_connector.start_push()

    result_data: list[NewsItem] = []
    total_tokens = 0
    for a in article_items:
        result, tokens = await service.get(text=a.content, lang=a.lang)
        if not result:
            continue
        total_tokens += tokens
        a.summary = result.summary

        a.category = catogory_service.resolve_category(
            text=result.category, lang=a.lang
        )
        a.subcategories = catogory_service.resolve_subcategories(
            category_id=a.category, texts=result.subcategories, lang=a.lang
        )
        a.priority = result.importance
        a.companies = result.companies
        a.locations = result.locations
        a.names = result.names
        a.is_ready = True

        result_data.append(a)
        await redis_connector.xadd(data={"item": a.model_dump_json()})

    await redis_connector.stop()
    return result_data, total_tokens


async def save_items(article_items: list[NewsItem]):
    async for session in get_async_session():
        for a in article_items:
            await session.merge(a)
        await session.commit()


async def handle_message(articles: list[dict]) -> bool:
    try:
        logger.info(f"Recived new {len(articles)} articles")
        article_items = await create_items(articles=articles)
        logger.info(f"Created new {len(article_items)} articles")
        catogory_service = await build_translation_lookup()
        article_items, total_tokens = await update_items(
            article_items=article_items,
            catogory_service=catogory_service,
        )
        if len(article_items) > 0:
            await save_items(article_items=article_items)
        logger.info(
            f"Updated new {len(article_items)} articles, spent: {total_tokens} tokens"
        )
        return True
    except Exception as e:
        logger.error(f"Feaid to proccess articles: {str(e)}", exc_info=True)
        return False


async def run() -> RedisConnector:
    stop_event = asyncio.Event()
    redis_connector = RedisConnector("raw_news", stop_event)

    await redis_connector.start_read(handle_message)

    return redis_connector
