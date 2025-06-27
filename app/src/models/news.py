from sqlmodel import Field, SQLModel, Column, TEXT
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class NewsItem(SQLModel, metadata=metadata, table=True):
    __tablename__ = "news_item"
    __table_args__ = (
        sa.Index("ix_news_item_subcategories", "subcategories", postgresql_using="gin"),
        sa.Index("ix_news_item_companies", "companies", postgresql_using="gin"),
        sa.Index("ix_news_item_locations", "locations", postgresql_using="gin"),
    )

    id: int | None = Field(
        primary_key=True, index=True, description="Unique ID of the news item"
    )
    title: str = Field(description="News title")
    content: str = Field(description="News content")
    summary: str = Field(description="News summary")
    lang: str = Field(description="Lang")
    source_url: str = Field(description="URL to the source")
    category: int | None = Field(description="Category", default=None)
    subcategories: list[int | str | None] = Field(
        sa_column=Column(
            postgresql.JSONB(astext_type=TEXT()),
            nullable=False,
            index=True,
        ),
        description="List of subcategories",
    )
    companies: list[str | None] = Field(
        sa_column=Column(
            postgresql.JSONB(astext_type=TEXT()),
            nullable=False,
            index=True,
        ),
        description="List of related companies",
    )
    locations: list[str | None] = Field(
        sa_column=Column(
            postgresql.JSONB(astext_type=TEXT()),
            nullable=False,
            index=True,
        ),
        description="List of related locations",
    )
    names: list[str | None] = Field(
        sa_column=Column(postgresql.JSONB(astext_type=TEXT()), nullable=False),
        description="List of related names",
    )
    priority: int = Field(description="News priority 0, 1, 2, 3", default=0)
    is_ready: bool = Field(description="Is ready for listing")
    published_at: datetime = Field(
        description="Publication date",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, index=True),
    )
    created_at: datetime = Field(
        description="Publication date",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
