import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.parser.http_parser import NewsScraper
from src.parser.model import NewsItem, NewsHtmlItem
from src.utils.chunkify import chunkify


logger = logging.getLogger(__name__)

global_proxies = [
    "5.8.87.51:8000:KaWEaF:rjbQSW",
    "5.8.81.131:8000:KaWEaF:rjbQSW",
    "5.8.81.39:8000:KaWEaF:rjbQSW",
    "5.8.86.77:8000:KaWEaF:rjbQSW",
    "5.8.84.209:8000:KaWEaF:rjbQSW",
]
ru_proxies = [
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

def run_batch(news: list[NewsItem]) -> list[NewsHtmlItem]:
    try:
        return scaper.process_news_batch(news)
    except Exception as e:
        logger.error(f"⚠️ Process error: {e}", exc_info=True)
        return []


def load_html(news: list[NewsItem]) -> list[NewsHtmlItem]:
    min_chunk, max_chunk = 3, 20
    max_workers = 10
    total = len(news)

    if total < min_chunk * max_workers:
        return run_batch(news)
    
    ideal_chunk_size = total / max_workers
    num_chunks = (
        int(ideal_chunk_size)
        if min_chunk <= ideal_chunk_size <= max_chunk
        else
        min(total // min_chunk, -(-total // max_chunk))
    )
    chunks = chunkify(news, num_chunks)

    results = []
    logger.info(f"Start {max_workers} parsging proccess by {num_chunks} chunks")
    for i in range(0, len(chunks), max_workers):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_batch, chunk) for chunk in chunks[i:i + max_workers]]
            for future in as_completed(futures):
                result = future.result() 
                results.extend(result)
           
    return results