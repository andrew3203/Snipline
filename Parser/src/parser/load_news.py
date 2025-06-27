import logging
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed
from src.parser.model import NewsItem, NewsHtmlItem
from src.utils.chunkify import chunkify


logger = logging.getLogger(__name__)


def run_batch(news: list[NewsItem]) -> list[NewsHtmlItem]:
    from src.parser.driver import process_news_batch
    try:
        return process_news_batch(news)
    except Exception as e:
        logger.error(f"⚠️ Process error: {e}", exc_info=True)
        return []


def load_html(news: list[NewsItem]) -> list[NewsHtmlItem]:
    min_chunk, max_chunk = 3, 20
    max_workers = min(3, cpu_count())
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
    timeout = len(chunks[0]) * 10

    results = []
    logger.info(f"Start {max_workers} parsging proccess by {num_chunks} chunks")
    for i in range(0, len(chunks), max_workers):
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_batch, chunk) for chunk in chunks[i:i + max_workers]]
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=timeout) 
                    results.extend(result)
                except TimeoutError:
                    logger.error("Timeout for proccess")
                    i -= 1
    return results