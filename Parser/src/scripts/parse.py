import logging

from src.parser.model import NewsResultItem
from src.parser.parse_news import parse_news
from src.parser.rss import load_links
from src.parser.load_newsv2 import load_html

logger = logging.getLogger(__name__)


def parse_articles(**kwargs) -> list[NewsResultItem]:
    logger.info("Start proccess")
    news_links = load_links()
    logger.info(f"Found new {len(news_links)} articles")

    news_html = load_html(news=news_links)
    logger.info(f"Loaded new {len(news_html)} articles")

    result = parse_news(news=news_html, **kwargs)
    logger.info(f"Parsed new {len(result)} articles")
    return result

