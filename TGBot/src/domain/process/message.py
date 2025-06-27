import asyncio
import logging

from jinja2 import Environment, BaseLoader
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.domain.process.fync_factory import FuncFactory
from src.domain.process.i18n import Localization
from src.domain.state.model import StateModel
from src.domain.state.scenario import MessageNode
from src.utils.singelon import SingletonMeta
from src.config import settings

logger = logging.getLogger(__name__)


class MessageSender(metaclass=SingletonMeta):
    
    def __init__(self):
        self.i18n = Localization()
        self.bot = Bot(token=settings.BOT_TOKEN)
        self._queue: asyncio.Queue = asyncio.Queue()
        self.func_factory = FuncFactory()
        self._interval = settings.SEND_PERIOD / settings.MAX_CALLS
        self.last_msg_id: dict[int, int] = {}
        self.env = Environment(loader=BaseLoader(), enable_async=True)
    
    def start(self):
        self._task = asyncio.create_task(self._worker())
    
    async def send(self, state: StateModel, node: MessageNode, queue: bool = True):
        markup = await self._get_keybord(state=state, node=node)
        text = self.i18n.get(lang=state.lang, key=f"{state.flow_key}.{state.node_key}.text")
        data = {**state.info, **state.model_dump(mode="json", exclude={"info"})}
        text = await self.env.from_string(text).render_async(data)
        if queue:
            await self._queue.put( (state.user_id, text, markup, node.edit) )
        else:
            await self._send_or_edit_message(text=text, user_id=state.user_id, edit=node.edit, markup=markup)
    
    async def send_raw(self, user_id: int, text: str, edit: bool = False, queue: bool = True):
        if queue:
            await self._queue.put( (user_id, text, edit, None) )
        else:
            await self._send_or_edit_message(text=text, user_id=user_id, edit=edit)

    async def _worker(self):
        while True:
            user_id, text, markup, edit = await self._queue.get()
            try:
                await self._send_or_edit_message(
                    text=text, user_id=user_id, edit=edit, markup=markup
                )
            except Exception as e:
                logger.exception("Failed to send message", exc_info=e)
            await asyncio.sleep(self._interval)
            self._queue.task_done()

    async def _get_keybord(self, state: StateModel, node: MessageNode) -> InlineKeyboardMarkup | None:
        if not node.btn:
            return None
        
        if node.btn.buttons:
            inline_keyboard: list[list[InlineKeyboardButton]] = []
            i = 0
            for row in node.btn.buttons:
                inline_keyboard.append([])
                for b in row:
                    i += 1
                    text = self.i18n.get(lang=state.lang, key=f"{state.flow_key}.{state.node_key}.button{i}")
                    inline_keyboard[-1].append(
                        InlineKeyboardButton(
                            text=text,
                            callback_data=f"{b.callback}__{text}",
                            url=b.url,
                            pay=b.pay,
                        )
                    )

            return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        
        if node.btn.buttons_gen_func:
            return await self.func_factory.run(func_key=node.btn.buttons_gen_func, state=state, node=node)
        return None
    
    async def _send_or_edit_message(
        self,
        text: str,
        user_id: int,
        edit: bool = False,
        markup: InlineKeyboardMarkup | None = None,
    ):
        last_message_id: int | None = self.last_msg_id.get(user_id) if edit else None

        if last_message_id:
            await self._edit_message(
                text=text,
                user_id=user_id,
                last_message_id=last_message_id,
                markup=markup
            )
        else:
            await self._send_message(
                text=text,
                user_id=user_id,
                markup=markup
            )
        
    async def _send_message(
        self,
        text: str,
        user_id: int,
        markup: InlineKeyboardMarkup | None = None,
    ):
        msg = await self.bot.send_message(
            text=text,
            chat_id=user_id,
            reply_markup=markup
        )
        self.last_msg_id[user_id] = msg.message_id

    async def _edit_message(
        self,
        text: str,
        last_message_id: int,
        user_id: int,
        markup: InlineKeyboardMarkup | None = None,
    ):
        await self.bot.edit_message_text(
            text=text,
            message_id=last_message_id,
            chat_id=user_id,
            reply_markup=markup
        )