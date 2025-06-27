from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, UTC
import logging
import time
import feedparser

from src.parser.http_parser import NewsScraper
from src.parser.model import NewsItem
from src.utils.chunkify import chunkify
from src.utils.urls import update_urls, get_urls
from src.utils.utils import parse_datetime_with_timezone

logger = logging.getLogger(__name__)

ru_proxies = [
    "5.8.87.51:8000:KaWEaF:rjbQSW",
    "5.8.81.131:8000:KaWEaF:rjbQSW",
    "5.8.81.39:8000:KaWEaF:rjbQSW",
    "5.8.86.77:8000:KaWEaF:rjbQSW",
    "5.8.84.209:8000:KaWEaF:rjbQSW",
]
global_proxies = [
    "196.19.243.129:8000:E4ZZ5B:YtGjTK",
    "196.18.227.232:8000:E4ZZ5B:YtGjTK",
    "196.17.223.211:8000:E4ZZ5B:YtGjTK",
    "196.19.243.11:8000:E4ZZ5B:YtGjTK",
    "196.19.243.79:8000:E4ZZ5B:YtGjTK",
]
scaper = NewsScraper(
    ru_proxies=ru_proxies,
    global_proxies=global_proxies
)


def get_rss(rss_link: str, **kwargs) -> feedparser.FeedParserDict:
    rss = feedparser.parse(rss_link, **kwargs)
    if rss.get("entries"):
        return rss

    time.sleep(2)
    xml = scaper.get_html(url=rss_link, timeout=20)
    if xml:
        rss = feedparser.parse(xml, **kwargs)
        if rss.get("entries"):
            return rss
    return defaultdict(list)

def get_liks(
    rss_link: str,
    date_from: datetime,
    lang: str,
    **kwargs
) -> tuple[list[NewsItem], datetime]:
    rss = get_rss(rss_link=rss_link, **kwargs)
    data: list[NewsItem] = []
    last_date = date_from
    for i in rss["entries"]:
        if i["link"] and i["published"]:
            published = parse_datetime_with_timezone(i["published"])
            if published > date_from:
                data.append(NewsItem(link=i["link"], published=published, lang=lang))
            last_date = max(last_date, published)
    return data, last_date

def prepare_news_links(rss_urls: list[dict]) -> list[NewsItem]:
    news_links: list[NewsItem] = []
    for item in rss_urls:
        if item["setting"] != "http":
            continue
        if item.get("last_date"):
            date_from = datetime.fromisoformat(item["last_date"])
        else:
            date_from = datetime.now(UTC).replace(hour=0, microsecond=0, second=0, minute=0)

        links, last_date = get_liks(rss_link=item["rss"], lang=item["lang"], date_from=date_from)
        news_links.extend(links)
        item["last_date"] = last_date.isoformat()
    return news_links

def filter_news(news: list[NewsItem]) -> list[NewsItem]:
    stash = set()
    result: list[NewsItem] = []
    for n in news:
        if n.link not in stash:
            stash.add(n.link)
            result.append(n)
    return result


def load_links() -> list[NewsItem]:
    rss_urls = get_urls()
    news_links: list[NewsItem] = []
    num_workers = 5
    chunks = chunkify(rss_urls, num_workers)        
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_chunk = {executor.submit(prepare_news_links, chunk): chunk for chunk in chunks}
        for future in as_completed(future_to_chunk):
            result = future.result()
            news_links.extend(result)
            
    update_urls(rss_urls)
    return filter_news(news_links)

