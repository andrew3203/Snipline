from fastapi import Depends, Query, Body, APIRouter
from src.models import NewsItem
from src.db import get_async_session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schema.news import NewsItemCreate, NewsItemUpdate

router = APIRouter()


@router.post("", response_model=dict)
async def create_news_item(
    data: NewsItemCreate,
    session: AsyncSession = Depends(get_async_session),
):
    item = NewsItem(**data.model_dump())
    session.add(item)
    await session.commit()
    return item.model_dump()


@router.get("", response_model=list[dict])
async def get_news_items(
    session: AsyncSession = Depends(get_async_session),
    limit: int = Query(description="Limit"),
    offset: int = Query(description="Offset"),
):
    query = await session.exec(select(NewsItem).limit(limit).offset(offset))
    return [i.model_dump() for i in query.all()]


@router.get("/item", response_model=dict)
async def get_news_item(
    session: AsyncSession = Depends(get_async_session),
    id: int = Query(description="id"),
):
    query = await session.exec(select(NewsItem).where(NewsItem.id == id))
    model = query.one()
    return model.model_dump()


@router.put("", response_model=dict)
async def update_news_items(
    session: AsyncSession = Depends(get_async_session),
    id: int = Query(description="id"),
    data: NewsItemUpdate = Body(...),
):
    query = await session.exec(select(NewsItem).where(NewsItem.id == id))
    model = query.one()
    model.summary = data.summary
    session.add(model)
    await session.commit()
    return model.model_dump()
