from pydantic import BaseModel, Field


class UserCreateModel(BaseModel):
    id: int = Field(description="Unique ID of the user")
    username: str | None = Field(default=None, description="Telegram username")
    name: str | None = Field(default=None, description="Telegram name")
    lang: str = Field(description="User's language")
    location: str | None = Field(description="User's location", default=None)
    tz: str | None = Field(description="User's timezone", default=None)
    is_active: bool = Field(description="Is active", default=True)
