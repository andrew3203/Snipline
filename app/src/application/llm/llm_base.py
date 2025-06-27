import asyncio
import logging

from aiohttp import ClientResponseError
from src.utls.file import read_all_from_dir
from src.utls.singelon import SingletonMeta
from src.repository.llm import GenAIAgentClient, ChatCompletionRequest, Message

logger = logging.getLogger(__name__)


class LLMBase(metaclass=SingletonMeta):
    def __init__(self, path: str):
        self.promts: dict | None = None
        self.agent = GenAIAgentClient()
        self.path = path

    async def load_promts(self):
        self.promts = await read_all_from_dir(self.path, "txt")
        return self.promts

    def _prepare_payload(
        self,
        text: str,
        lang: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 3000,
        max_completion_tokens: int = 500,
    ) -> ChatCompletionRequest:
        system = self.promts.get(lang)
        if not system:
            system = self.promts["en"]
        return ChatCompletionRequest(
            messages=[
                Message(role="system", content=system),
                Message(role="user", content=text),
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
        )

    async def get(
        self, text: str, lang: str, try_number: int = 0, **kwagrs
    ) -> tuple[str | None, int]:
        if not self.promts:
            await self.load_promts()

        if try_number > 1:
            return None, 0

        payload = self._prepare_payload(text=text, lang=lang, **kwagrs)
        try:
            response = await self.agent.chat_completion(payload=payload)
            total_tokens = response.get("usage", {}).get("total_tokens", 0)
            return response["choices"][0]["message"]["content"], total_tokens
        except KeyError as e:
            logger.error(f"LLMSummarize parse response error: {str(e)}")
        except ClientResponseError as e:
            logger.error(f"HTTP LLMSummarize response error: {str(e)}")
            await asyncio.sleep(5)
            try:
                await self.agent.health_check()
                return await self.get(text=text, lang=lang, try_number=try_number + 1)
            except ClientResponseError as e:
                logger.error(f"HTTP LLMSummarize health_check error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexcpected LLMSummarize error: {str(e)}")

        return None, 0
