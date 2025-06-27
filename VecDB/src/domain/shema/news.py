from datetime import datetime
from pydantic import Field
from src.domain.shema.base import BaseModel

class NewsItemCreate(BaseModel):
    id: int = Field(description="news id")
    summary: str = Field(description="Краткий текст новости")
    lang: str = Field(description="Язык новости, напр. 'ru' или 'en'")
    published_at: datetime = Field(description="Дата/время публикации новости")


class SearchRequest(BaseModel):
    summary: str = Field(description="Текст для поиска похожих новостей")
    top_k: int = Field(gt=0, description="Количество возвращаемых похожих новостей")
    lang: str | None = Field(None, description="(опционально) фильтрация по языку")
    date_from: datetime | None = Field(
        default=None,
        description="(опционально) только новости, опубликованные не ранее этой даты"
    )


class SearchResponse(BaseModel):
    data: list[str] = Field(description="Список найденных похожих текстов новостей")
