from typing_extensions import Literal
import logging

from src.domain.process.message import MessageSender
from src.domain.state.state import State
from src.utils.singelon import SingletonMeta

logger = logging.getLogger(__name__)


class ReportService(metaclass=SingletonMeta):
    def __init__(self):
        self.state = State()
        self.sender = MessageSender()

    async def handle(self, data: dict):
        f: Literal["raw", "node"] = data.pop("mode", "raw")
        match f:
            case "raw":
                await self.handle_raw(data=data)
            case "node":
                 await self.handle_node(data=data)
            case _:
                logger.warning("Faild to recive message from stream")

    async def handle_raw(self, data: dict):
        await self.sender.send_raw(
            user_id=data["user_id"],
            text=data["content"],
            edit=True,
        )
    
    async def handle_node(self, data: dict):
        user_id: int | None = data.pop("user_id", None)
        if not user_id:
            logger.error("faild to recive user id from stream message")
            return
        flow_key: str | None = data.pop("flow_key", None)
        if not flow_key:
            logger.error("faild to recive flow_key from stream message")
            return
        if flow_key not in self.state.scenario:
            logger.error(f"Incorrect {flow_key=} in stream message")
            return

        state = await self.state.get(user_id=user_id)

        state.info.update(data)
        state.node_key = self.state.scenario[flow_key].start_node
        await self.state.set(user_id, state)

        node = await self.state.get_node(user_id=user_id)

        await self.sender.send(
            state=state,
            node=node,
        )