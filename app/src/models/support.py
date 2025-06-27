from sqlmodel import Field, SQLModel
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class Support(SQLModel, metadata=metadata, table=True):
    __tablename__ = "support"

    id: int = Field(primary_key=True, description="Unique ID of the user")
    user_id: int = Field(
        foreign_key="user.id", index=True, description="User who asked the question"
    )
    question: str = Field(description="User's question")
    answer: str | None = Field(description="Answer provided by", default=None)
    created_at: datetime = Field(
        description="Created at",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    answered_at: datetime | None = Field(
        description="Answered at",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
    )
