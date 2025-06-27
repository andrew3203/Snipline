from sqlmodel import Field, SQLModel
from src.models.config import metadata


class NewsCategory(SQLModel, metadata=metadata, table=True):
    __tablename__ = "news_category"

    id: int = Field(
        primary_key=True, index=True, description="Unique ID of the catogory"
    )
    parent_id: int | None = Field(
        description="Parrent id of category", nullable=True, default=None
    )
