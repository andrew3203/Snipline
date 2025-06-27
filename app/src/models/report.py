from sqlmodel import Field, SQLModel, Column, TEXT
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class NewsReport(SQLModel, metadata=metadata, table=True):
    __tablename__ = "news_report"

    id: int = Field(primary_key=True, index=True, description="Report ID")
    content: str = Field(description="Report text")
    lang: str = Field(description="Lang", index=True)
    news_ids: list[int] = Field(
        sa_column=Column(postgresql.JSONB(astext_type=TEXT()), nullable=False),
        description="News ids",
    )
    filter_id: int = Field(
        foreign_key="user_filter.id", index=True, description="Filter group ID"
    )
    user_id: int = Field(foreign_key="user.id", index=True, description="User ID")
    reaction: int = Field(
        description="Reaction: 0 - no, 1 - like, -1 - dislike", default=0
    )
    delivered_at: datetime | None = Field(
        description="Delivery timestamp",
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
    )


class AIReport(SQLModel, metadata=metadata, table=True):
    __tablename__ = "ai_report"

    id: int = Field(primary_key=True, index=True, description="Unique ID")
    user_id: int = Field(
        foreign_key="user.id", index=True, description="User who asked the question"
    )
    report_id: int | None = Field(
        foreign_key="news_report.id",
        nullable=True,
        description="Related news report",
        default=None,
    )
    question: str = Field(description="User's question")
    answer: str | None = Field(description="Answer provided by AI", default=None)
    reaction: int = Field(
        description="Reaction: 0 - no, 1 - like, -1 - dislike", default=0
    )
    created_at: datetime = Field(
        description="Time when question was asked",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    delivered_at: datetime | None = Field(
        description="Delivery timestamp",
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
    )
