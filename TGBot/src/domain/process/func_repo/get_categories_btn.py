import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.domain.state.model import StateModel
from src.repo.http.app_http import AppHttpRepo


logger = logging.getLogger(__name__)


async def get_categories(
    state: StateModel,
    api: AppHttpRepo,
    **kwargs
):
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)