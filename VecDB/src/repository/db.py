from datetime import datetime
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest

from config.settings import settings
from src.domain.exceptions import APIException
from src.domain.utils.singleton import SingletonMeta


class AsyncQdrantService(metaclass=SingletonMeta):
    """
    Обёртка для работы с AsyncQdrantClient:
    - создаёт/проверяет коллекцию
    - умеет добавлять точку (новость)
    - умеет искать ближайшие по вектору объекты с фильтрацией
    """
    def __init__(self):
        self.client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

    async def ensure_collection(self) -> None:
        """
        Проверяет наличие коллекции, при отсутствии — создаёт её.
        """
        try:
            existing = await self.client.get_collections()
        except Exception as exc:
            raise APIException(msg=f"Ошибка при получении списка коллекций: {exc}")

        names = [c.name for c in (existing.collections or [])]
        if settings.COLLECTION_NAME not in names:
            try:
                await self.client.recreate_collection(
                    collection_name=settings.COLLECTION_NAME,
                    vectors_config=rest.VectorParams(size=settings.EMBEDDING_DIM, distance=rest.Distance.COSINE),
                )
            except Exception as exc:
                raise APIException(msg=f"Ошибка при создании коллекции: {exc}")

    async def add_news_item(
        self,
        id: int,
        summary: str,
        lang: str,
        published_at: datetime,
        vector: list[float]
    ) -> None:
        """
        Сохраняет в Qdrant новый документ-новость.
        Возвращает сгенерированный UUID.
        """
        payload = {
            "summary": summary,
            "lang": lang,
            "published_at": published_at.timestamp()
        }
        point = rest.PointStruct(id=id, vector=vector, payload=payload)
        try:
            await self.client.upsert(collection_name=settings.COLLECTION_NAME, points=[point])
        except Exception as exc:
            raise APIException(msg=f"Ошибка при вставке в Qdrant: {exc}")

    async def search_similar(
        self,
        query_vector: list[float],
        top_k: int,
        score_threshold: float | None = None,
        lang: str | None = None,
        date_from: datetime | None = None
    ) -> list[str]:
        """
        Ищет top_k самых похожих документов по вектору.
        Опционально фильтрует по языку (lang) и дате (published_at >= date_from).
        Возвращает список полей "summary".
        """
        must_filters = []
        if lang:
            must_filters.append(
                rest.FieldCondition(
                    key="lang",
                    match=rest.MatchValue(value=lang)
                )
            )
        if date_from:
            must_filters.append(
                rest.FieldCondition(
                    key="published_at",
                    range=rest.Range(gte=date_from.timestamp())
                )
            )
        filter_obj = rest.Filter(must=must_filters) if must_filters else None

        try:
            hits = await self.client.search(
                collection_name=settings.COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                query_filter=filter_obj
            )
        except Exception as exc:
            raise APIException(msg=f"Ошибка при поиске в Qdrant: {exc}")

        results = []
        for hit in hits:
            payload = hit.payload or {}
            results.append(payload.get("summary", ""))
        return results

