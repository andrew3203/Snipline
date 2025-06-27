from sqlmodel import Field, SQLModel, Column, TEXT
from sqlalchemy.dialects import postgresql

from src.models.config import metadata


class UserFilter(SQLModel, metadata=metadata, table=True):
    __tablename__ = "user_filter"

    id: int = Field(primary_key=True, index=True, description="Unique ID of the filter")
    user_id: int = Field(foreign_key="user.id", index=True, description="User ID")
    name: str = Field(description="Name of filter group")
    filters: dict = Field(
        sa_column=Column(postgresql.JSONB(astext_type=TEXT()), nullable=False),
        description="Filters",
    )
