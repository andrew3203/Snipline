from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from newspaper import Article

from src.parser.model import NewsHtmlItem, NewsResultItem
from src.utils.chunkify import chunkify
from src.utils.redis import RedisConnector
from src.utils.utils import clean_news


logger = logging.getLogger(__name__)


def get_article(news: list[NewsHtmlItem]) -> list[NewsResultItem]:
    result = []
    for item in news:
        if item.html is None:
            continue
            # result.append(NewsResultItem(*item, article=None))

        article = Article(item.link, language=item.lang)
        try:
            article.download(input_html=item.html)
            article.parse()

            if not article.is_parsed:
                raise Exception(f"{item.link} was not parsed")
            article.text = clean_news(article.text)
            if len(article.text.replace(" ", "")) < 50:
                raise Exception(f"{item.link} is empty")
            result.append(NewsResultItem(*item, article=article))
        except Exception as e:
            logger.error(f"Parse error: {e}")
            # result.append(NewsResultItem(*item, article=None))
    return result



def parse_news(news: list[NewsHtmlItem], **kwargs) -> list[NewsResultItem]:
    num_workers = 5
    connector: RedisConnector = kwargs["connector"]
    if len(news) < num_workers * 2:
        res = get_article(news=news)
        connector.xadd(res)
        return res

    chunks = chunkify(news, num_workers)        
    all_results = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_chunk = {executor.submit(get_article, chunk): chunk for chunk in chunks}
        for future in as_completed(future_to_chunk):
            result = future.result()
            all_results.extend(result)
            connector.xadd(result)
    return all_results
    