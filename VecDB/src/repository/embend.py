from config.settings import settings
from src.repository.http import HttpSource


async def fetch_embedding(text: str) -> list[float]:
    """
    Запрашивает у внешнего сервиса (Ollama) вектор по переданному тексту.
    Ожидается JSON-ответ вида: {"vector": [0.12, -0.03, ...]}
    """
    repo = HttpSource()
    data = await repo.post(
        headers={},
        url=settings.EMBEDDING_SERVICE_URL,
        data={"model": settings.EMBEDDING_MODEL, "prompt": text},
        timeout=30,

    )
    return data["embedding"]