from pydantic import BaseModel
from datetime import datetime


class NewsItemUpdate(BaseModel):
    summary: str


class NewsItemCreate(BaseModel):
    title: str
    content: str
    summary: str
    lang: str
    source_url: str
    category: str
    subcategories: list[str]
    companies: list[str]
    locations: list[str]
    names: list[str]
    priority: int = 0
    is_ready: bool
    published_at: datetime
    created_at: datetime
