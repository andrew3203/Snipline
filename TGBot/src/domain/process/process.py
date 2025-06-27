import logging
from typing import Any
from src.domain.process.i18n import Localization
from src.domain.process.message import MessageSender
from src.domain.state.model import StateModel
from src.domain.state.scenario import MessageNode, ConditionNode, FunctionNode, SubflowNode, EndNode, InputNode
from src.domain.state.state import State
from aiogram.types import Message, CallbackQuery

from src.utils.conditions import compile_expr
from src.utils.singelon import SingletonMeta

from .fync_factory import FuncFactory

logger = logging.getLogger(__name__)


class UserFlow(metaclass=SingletonMeta):

    def __init__(self):
        self.state = State()
        self.i18n = Localization()
        self.func_factory = FuncFactory()
        self.sender = MessageSender()
        self.factory = {
            "message": self.process_message,
            "input": self.process_input,
            "function": self.process_function,
            "condition": self.process_condition,
            "subflow": self.process_subflow,
            "end": self.process_end,
        }
        

    async def start(self):
        self.sender.start()
        await self.state.start()

    async def run_scenario(
        self,
        user_id: int,
        flow_key: str,
        lang: str,
        command_args: str | None,
        entry: str = None,
        **kwargs,
    ):
        state = await self.state.get_or_create(user_id=user_id, lang=lang)
        state.flow_key = flow_key
        state.node_key = entry or self.state.scenario[flow_key].start_node
        logger.info(f"Run scenario with {flow_key=} and node_key={state.node_key}")
        await self.state.set(user_id, state)
        await self.func_factory.run(
            func_key=flow_key,
            state=state,
            command_args=command_args,
            lang=lang,
            **kwargs,
        )

    async def handle_message(self, update: Message):
        state = await self.state.get(user_id=update.from_user.id)
        node = await self.state.get_node(user_id=update.from_user.id)
        await self.factory[node.type](state=state, node=node, text=update.text)
        await self.chech_is_subflow(user_id=state.user_id)
    
    async def handle_callback(self, update: CallbackQuery):
        state = await self.state.get(user_id=update.from_user.id)
        keys = update.data.split("__")
        state.node_key, text = keys[0], keys[-1]
        node = await self.state.get_node(user_id=update.from_user.id)
        await self.factory[node.type](state=state, node=node, text=text)
        await update.answer()
        await self.chech_is_subflow(user_id=state.user_id)

    async def process_message(self, state: StateModel, node: MessageNode, **kwargs: Any):
        await self.sender.send(state=state, node=node)
        state.node_key = node.next
        await self.state.set(user_id=state.user_id, state=state)

    async def process_function(self, state: StateModel, node: FunctionNode, **kwargs: Any):
        node_key = await self.func_factory.run(
            state=state,
            func_key=node.name,
            node=node,
            **kwargs,
        )

        state.node_key = node_key or node.next
        await self.state.set(user_id=state.user_id, state=state)

        node = await self.state.get_node(user_id=state.user_id)
        await self.factory[node.type](state=state, node=node, **kwargs)

    async def process_condition(self, state: StateModel, node: ConditionNode, **kwargs: Any):
        next_key = None
        for cond in node.conditions:
            if cond.if_ and compile_expr(cond.if_)(state.info):
                next_key = cond.goto
                break
            if cond.else_:
                next_key = cond.else_
                break

        state.node_key = next_key
        await self.state.set(state.user_id, state)
        node = await self.state.get_node(state.user_id)
        await self.factory[node.type](state=state, node=node)

    async def process_input(self, state: StateModel, node: InputNode, **kwargs: Any):
        state.info[node.save_to] = kwargs["text"]
        state.node_key = node.next
        await self.state.set(user_id=state.user_id, state=state)
        node = await self.state.get_node(user_id=state.user_id)
        await self.factory[node.type](state=state, node=node, **kwargs)

    async def process_subflow(self, state: StateModel, node: SubflowNode, **kwargs: Any):
        state.flow_key = node.flow
        state.node_key = node.entry
        await self.state.set(user_id=state.user_id, state=state)
        node = await self.state.get_node(user_id=state.user_id)
        await self.factory[node.type](state=state, node=node, **kwargs)
    
    async def process_end(self, state: StateModel, node: EndNode, **kwargs: Any):
        state.flow_key = "start"
        state.node_key = None
        await self.state.set(user_id=state.user_id, state=state)
    
    async def chech_is_subflow(self, user_id: int):
        state = await self.state.get(user_id=user_id)
        node = await self.state.get_node(user_id=state.user_id)
        if node.type == "subflow":
            await self.process_subflow(state=state, node=node)