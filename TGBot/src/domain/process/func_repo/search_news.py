import logging
from src.domain.state.model import StateModel
from src.repo.http.app_http import AppHttpRepo


logger = logging.getLogger(__name__)


async def search_news_by_query(
    state: StateModel,
    api: AppHttpRepo,
    **kwargs
) -> str | None:
    state.info["search_results"] = await api.get_news_rag_question(
        user_id=state.user_id,
        question=state.info["user_query"],
        answer_lang=state.lang
    )


