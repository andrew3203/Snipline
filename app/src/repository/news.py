from datetime import datetime
from fastapi import APIRouter
from src.models import NewsItem
from sqlmodel import select, col, and_, func, cast, TEXT
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


def contains(field, values: list[str]):
    return func.jsonb_exists_any(field, cast(values, ARRAY(TEXT)))


async def filter_news_items(
    session: AsyncSession,
    date_from: datetime,
    category: str | None = None,
    priority: int | None = None,
    source: str | None = None,
    subcategories: str | None = None,
    companies: str | None = None,
    locations: str | None = None,
    names: str | None = None,
    lang: str | None = None,
    limit: int | None = None,
) -> list[NewsItem]:
    query = select(NewsItem).where(
        and_(
            col(NewsItem.is_ready).is_(True),
            NewsItem.published_at >= date_from,
        )
    )
    if category:
        query = query.where(NewsItem.category == category)
    if priority:
        query = query.where(NewsItem.priority == priority)
    if lang:
        query = query.where(NewsItem.lang == lang)
    if source:
        query = query.where(col(NewsItem.source_url).ilike(f"%{source}%"))
    if subcategories:
        query = query.where(contains(NewsItem.subcategories, subcategories.split(",")))
    if companies:
        query = query.where(contains(NewsItem.companies, companies.split(",")))
    if locations:
        query = query.where(contains(NewsItem.locations, locations.split(",")))
    if names:
        query = query.where(contains(NewsItem.names, names.split(",")))
    if limit:
        query = query.limit(limit)

    query = await session.exec(query)
    return query.all()


async def apply_filter(filter_data: dict, date_from: datetime):
    query = select(NewsItem).where(
        and_(NewsItem.published_at >= date_from, col(NewsItem.is_ready).is_(True))
    )

    if category := filter_data.get("category"):
        query = query.where(NewsItem.category == category)
    if subcats := filter_data.get("subcategories"):
        query = query.where(contains(NewsItem.subcategories, subcats))
    if comps := filter_data.get("companies"):
        query = query.where(contains(NewsItem.companies, comps))
    if locs := filter_data.get("locations"):
        query = query.where(contains(NewsItem.locations, locs))
    if names := filter_data.get("names"):
        query = query.where(contains(NewsItem.names, names))
    if prios := filter_data.get("priority"):
        query = query.where(col(NewsItem.priority).in_(prios))

    return query
