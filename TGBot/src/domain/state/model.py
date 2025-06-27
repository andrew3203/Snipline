from pydantic import BaseModel, Field

from src.repo.http.models import FullUserResponse


class StateModel(BaseModel):
    info: dict = Field(description="Additional info", default={})
    user_id: int = Field(description="User id")
    flow_key: str = Field(description="Current scenario key", default="start")
    node_key: str | None = Field(description="Current step key", default=None)
    lang: str = Field(description="language_code")
    user_info: FullUserResponse | None = Field(default=None)
