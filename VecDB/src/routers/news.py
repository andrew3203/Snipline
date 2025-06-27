from fastapi import APIRouter

from src.domain.shema.news import SearchRequest, NewsItemCreate, SearchResponse
from src.repository.db import AsyncQdrantService
from src.repository.embend import fetch_embedding

router = APIRouter()


@router.post("", response_model=dict)
async def add_news(
    item: NewsItemCreate,
):
    """
    1. Получаем embedding для переданного summary.
    2. Сохраняем новость в Qdrant через AsyncQdrantService.
    3. Возвращаем сгенерированный ID.
    """
    vector = await fetch_embedding(item.summary)
    await AsyncQdrantService().add_news_item(
        id=item.id,
        summary=item.summary,
        lang=item.lang,
        published_at=item.published_at,
        vector=vector
    )
    return {"status": "ok"}


@router.post("/search", response_model=SearchResponse)
async def search_news(data: SearchRequest):
    """
    1. Получаем embedding для текста из запроса.
    2. Передаём все параметры в AsyncQdrantService.search_similar.
    3. Возвращаем список найденных summary.
    """
    query_vector = await fetch_embedding(data.summary)
    found = await AsyncQdrantService().search_similar(
        query_vector=query_vector,
        top_k=data.top_k,
        lang=data.lang,
        date_from=data.date_from
    )
    return SearchResponse(data=found)
