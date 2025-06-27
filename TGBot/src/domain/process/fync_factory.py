import logging
import importlib
import inspect
from typing import Any, Awaitable, Callable

from src.domain.state.model import StateModel
from src.repo.http.app_http import AppHttpRepo
from src.utils.singelon import SingletonMeta

logger = logging.getLogger(__name__)

class FuncFactory(metaclass=SingletonMeta):
    def __init__(self):
        self.repo = self.__get_func_repo()
        self.api = AppHttpRepo()
    
    def __get_func_repo(self) -> dict[str, Callable[[StateModel, AppHttpRepo, Any], Awaitable[Any | None]]]:
        pkg_name = "src.domain.process.func_repo"
        pkg = importlib.import_module(pkg_name)

        func_names = getattr(pkg, "__all__", [])

        repo: dict[str, Callable[[StateModel, Any], Awaitable[str | None]]] = {}
        for name in func_names:
            obj = getattr(pkg, name, None)
            if obj and inspect.iscoroutinefunction(obj):
                repo[name] = obj
            else:
                logger.warning(f"Ignored {name=}, not found or not async function in {pkg_name}")
        return repo
    
    async def run(self, func_key: str, state: StateModel, **kwargs) -> Any:
        func = self.repo.get(func_key)
        if func:
            return await func(state=state, api=self.api, **kwargs)
        logger.warning(f"Function with {func_key=} not found")
        return None
 

