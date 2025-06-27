import asyncio
import logging

from pydantic import ValidationError
from src.application.llm.llm_base import LLMBase
from src.utls.file import read_all_from_dir
from .model import LLMResp
import json

logger = logging.getLogger(__name__)


class LLMSummarize(LLMBase):
    def __init__(self):
        super().__init__("src/prompts/summarize")

    async def load_promts(self):
        data = await super().load_promts()
        categories = await read_all_from_dir("src/prompts/category", "json")
        for k, v in categories.items():
            data[k] = data[k] + json.dumps(v, indent=2)
        self.promts = data

    def parse(self, content: str) -> LLMResp:
        content = content.replace("`", "")
        content = content.replace("json", "")
        content = content.replace("\n", "")
        content = content.strip(" ")
        return LLMResp.model_validate_json(content)

    async def get(
        self, text: str, lang: str, try_number: int = 0, **kwagrs
    ) -> tuple[LLMResp | None, int]:
        content: str | None = None
        if try_number > 1:
            return None, 0
        try:
            content, total_tokens = await super().get(
                text=text,
                lang=lang,
                try_number=try_number,
                **kwagrs,
            )
            return self.parse(content), total_tokens
        except ValidationError as e:
            logger.error(
                f"Faild to parse LLMSummarize resp: {content}\n{str(e)}", exc_info=True
            )
        except Exception as e:
            logger.error(f"Unexpected parse error: {str(e)}", exc_info=True)

        await asyncio.sleep(1)
        return await self.get(text=text, lang=lang, try_number=try_number + 1, **kwagrs)
