import logging
from src.domain.state.model import StateModel
from src.repo.http.app_http import AppHttpRepo
from src.utils.exceptions import CoreException


logger = logging.getLogger(__name__)


async def gift(
    state: StateModel,
    api: AppHttpRepo,
    **kwargs
) -> str | None:
    await api.create_subscription(
        user_id=state.user_id,
        plan_id=7,
        payment_id=None,
        promo_offer_id=None,
    )
    state.user_info = await api.get_user(user_id=state.user_id)