import logging
from src.domain.state.model import StateModel
from src.repo.http.app_http import AppHttpRepo
from src.utils.exceptions import CoreException


logger = logging.getLogger(__name__)


async def start(
    state: StateModel,
    api: AppHttpRepo,
    command_args: str | None,
    lang: str,
    first_name: str,
    username: str,
    **kwargs
) -> str | None:
    try:
        state.user_info = await api.get_user(user_id=state.user_id)
    except CoreException:
        try:
            await api.create_user(
                id=state.user_id,
                lang=lang,
                username=username,
                name=first_name,
                is_active=True,
                rise_error=False
            )
            logger.info(f"Created new user user_id={state.user_id}")
        except CoreException:
            logger.error(f"Failed to create new user user_id={state.user_id}", exc_info=True)
    
    if command_args and isinstance(command_args, str):
        referrer_id: int | None = None
        source: str | None = None
        if command_args.startswith("u") and command_args[1:].isdigit():
            referrer_id = int(command_args[1:])
        elif command_args.startswith("s"):
            source = command_args[1:]
        try:
            await api.create_referral(
                referrer_id=referrer_id,
                referred_id=state.user_id,
                source=source,
            )
            state.user_info = await api.get_user(user_id=state.user_id)
            logger.info(f"Referall for user_id={state.user_id} created {referrer_id=} {source=}")
        except CoreException:
            logger.error(f"Failed to create refferal user_id={state.user_id}", exc_info=True)

async def chech_user(
    state: StateModel,
    api: AppHttpRepo,
    **kwargs
) -> str | None:
    if state.user_info:
        return "second_eneter"
