from datetime import datetime
from typing import NamedTuple
from newspaper import Article


class NewsItem(NamedTuple):
    link: str
    published: datetime
    lang: str

class NewsHtmlItem(NamedTuple):
    link: str
    published: datetime
    lang: str
    html: str | None
    success: bool

class NewsResultItem(NamedTuple):
    link: str
    published: datetime
    lang: str
    html: str | None
    success: bool
    article: Article | None