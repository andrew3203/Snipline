from sqlmodel import Field, SQLModel, Column, TEXT
from sqlalchemy.dialects import postgresql
from src.models.config import metadata


class Dictionary(SQLModel, metadata=metadata, table=True):
    __tablename__ = "dictionary"

    id: str = Field(
        primary_key=True, index=True, description="Row id : {id}_{table_name}"
    )
    data: dict = Field(
        sa_column=Column(postgresql.JSONB(astext_type=TEXT()), nullable=False),
        description="Data",
    )

    @property
    def table_name(self) -> str:
        return self.id.split("_")[-1]

    @property
    def row_id(self) -> int:
        return int(self.id.split("_")[0])
