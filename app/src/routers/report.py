from datetime import datetime, UTC, timedelta
from fastapi import Depends, HTTPException, Query, APIRouter
from src.application.llm.report import LLMReport
from src.db import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from src.models.filters import UserFilter
from src.repository.news import apply_filter

router = APIRouter()


@router.get("/news-count", response_model=int)
async def get_filtered_news_count(
    user_id: int = Query(..., description="User ID"),
    filter_id: int = Query(..., description="Filter ID"),
    date_from: datetime | None = Query(description="Start date", default=None),
    session: AsyncSession = Depends(get_async_session),
):
    date_from = date_from or datetime.now(UTC) - timedelta(hours=12)

    filter_obj = await session.get(UserFilter, filter_id)
    if not filter_obj or filter_obj.user_id != user_id:
        raise HTTPException(status_code=404, detail="Filter not found")
    query = await apply_filter(filter_obj.filters, date_from)
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.exec(count_query)
    return count_result.one()


@router.get("/report", response_model=str)
async def get_filtered_news_report(
    user_id: int = Query(..., description="User ID"),
    filter_id: int = Query(..., description="Filter ID"),
    date_from: datetime | None = Query(description="Start date", default=None),
    answer_lang: str = Query(..., description="Answer language"),
    session: AsyncSession = Depends(get_async_session),
):
    date_from = date_from or datetime.now(UTC) - timedelta(hours=12)

    filter_obj = await session.get(UserFilter, filter_id)
    if not filter_obj or filter_obj.user_id != user_id:
        raise HTTPException(status_code=404, detail="Filter not found")

    query = await apply_filter(filter_obj.filters, date_from)
    result = await session.exec(query)
    news_items = result.all()

    llm = LLMReport()
    return await llm.get_report(data=news_items, answer_lang=answer_lang)


@router.get("/question", response_model=str)
async def get_filtered_news_report_question(
    user_id: int = Query(..., description="User ID"),
    question: str = Query(description="Question"),
    filter_id: int = Query(..., description="Filter ID"),
    date_from: datetime | None = Query(description="Start date", default=None),
    answer_lang: str = Query(..., description="Answer language"),
    session: AsyncSession = Depends(get_async_session),
):
    date_from = date_from or datetime.now(UTC) - timedelta(hours=12)

    filter_obj = await session.get(UserFilter, filter_id)
    if not filter_obj or filter_obj.user_id != user_id:
        raise HTTPException(status_code=404, detail="Filter not found")

    query = await apply_filter(filter_obj.filters, date_from)
    result = await session.exec(query)
    news_items = result.all()

    llm = LLMReport()
    return await llm.get_report_with_payload(
        data=news_items, answer_lang=answer_lang, question=question
    )
