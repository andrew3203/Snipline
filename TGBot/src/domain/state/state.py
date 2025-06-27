
import asyncio
import json
import logging
from redis.asyncio import Redis, ConnectionPool
from src.utils.cache import AsyncLRUCache
from src.utils.file import read_all_json_from_dir
from src.utils.singelon import SingletonMeta
from src.config import settings

from .model import StateModel
from .scenario import FlowDefinition, Node

logger = logging.getLogger(__name__)


class State(metaclass=SingletonMeta):

    def __init__(self) -> None:
        self.init_key = "start"
        self.data = AsyncLRUCache[StateModel](
            max_age=60 * 60,
            maxsize=1000,
            model_class=StateModel,
        )
        self.scenario: dict[str, FlowDefinition] = {}
        pool = ConnectionPool.from_url(
            url=settings.REDIS_URL,
            max_connections=5,
            socket_timeout=30,
            db=0,
            encoding="utf-8",
            socket_connect_timeout=20,
            health_check_interval=30,
            retry_on_timeout=True,
            decode_responses=True,
        )
        self.redis = Redis(connection_pool=pool)
        self.store_key = "users_store"
    
    async def start(self):
        await self._load_scenario()
        await self._load()
        self._save_task = asyncio.create_task(self._auto_save_loop())

    async def _auto_save_loop(self):
        while True:
            await asyncio.sleep(60)
            try:
                await self.save()
                logger.info("Saved")
            except Exception as e:
                logger.info(f"Auto-save failed: {e}")

    async def _load_scenario(self):
        items = await read_all_json_from_dir("src/flows")
        for name, content in items.items():
            self.scenario[name] = FlowDefinition.model_validate(content)
    
    async def get(self, user_id: int) -> StateModel:
        state = await self.data.get(user_id)
        if not state:
            raise Exception("There is no state for current user")
        return state
    
    async def get_or_create(self, user_id: int, lang: str) -> StateModel:
        state = await self.data.get(user_id)
        if not state:
            state = StateModel(user_id=user_id, lang=lang)
            await self.data.set(user_id, state)
            return state
        return state
    
    async def set(self, user_id: int, state: StateModel) -> None:
        await self.data.set(user_id, state)
    
    async def get_node(self, user_id: int) -> Node:
        state = await self.get(user_id)
        if not self.scenario:
            await self._load_scenario()

        scenario = self.scenario[state.flow_key]
        state.node_key = state.node_key or scenario.start_node
        return scenario.nodes[state.node_key]
    
    async def save(self):
        data = await self.data.dumps()
        await self.redis.mset(data)

        keys = await self.data.dumps_keys()
        await self.redis.set(self.store_key, keys)
    
    async def _load(self):
        if len(self.data) == 0:
            keys_raw = await self.redis.get(self.store_key)
            if not keys_raw:
                return

            keys = json.loads(keys_raw)
            result = await self.redis.mget(keys)
            data = {k: v for k, v in zip(keys, result)}
            await self.data.mset(data)


    