from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from config.settings import settings
import aiohttp


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "developer"]
    content: str


class KBFilter(BaseModel):
    index: str
    path: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.01)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    max_completion_tokens: Optional[int] = Field(default=None, ge=1)
    stream: Optional[bool] = False
    k: Optional[int] = Field(default=None, ge=0)
    retrieval_method: Optional[
        Literal["rewrite", "step_back", "sub_queries", "none"]
    ] = None
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[Union[str, List[str]]] = None
    instruction_override: Optional[str] = None
    include_functions_info: Optional[bool] = False
    include_retrieval_info: Optional[bool] = False
    include_guardrails_info: Optional[bool] = False
    provide_citations: Optional[bool] = False
    kb_filters: Optional[List[KBFilter]] = None
    filter_kb_content_by_query_metadata: Optional[bool] = False


class GenAIAgentClient:
    def __init__(self):
        self.base_url = settings.LLM_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        }

    async def health_check(self) -> dict:
        url = f"{self.base_url}/health"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def chat_completion(self, payload: ChatCompletionRequest) -> dict:
        url = f"{self.base_url}/api/v1/chat/completions"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                url, json=payload.model_dump(exclude_none=True)
            ) as response:
                response.raise_for_status()
                return await response.json()
