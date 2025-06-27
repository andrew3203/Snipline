from sqlmodel import Field, SQLModel
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class User(SQLModel, metadata=metadata, table=True):
    __tablename__ = "user"

    id: int = Field(primary_key=True, index=True, description="Unique ID of the user")
    username: str | None = Field(default=None, description="Telegram username")
    name: str | None = Field(default=None, description="Telegram name")
    lang: str = Field(description="User's language")
    location: str | None = Field(description="User's location", default=None)
    tz: str | None = Field(description="User's timezone", default=None)
    is_active: bool = Field(description="Is active", default=True)
    current_plan_id: int | None = Field(
        default=None,
        foreign_key="subscription_plan.id",
        description="Current active plan ID",
    )
    created_at: datetime = Field(
        description="User registration date",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    active_at: datetime | None = Field(
        description="User last active date",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
    )
