import logging
import requests
import random
import time
import threading
from urllib.parse import urlparse
from fake_useragent import UserAgent
from datetime import datetime, timedelta, UTC

from src.parser.model import NewsHtmlItem, NewsItem

logger = logging.getLogger(__name__)

def human_delay(min_s=1.0, max_s=5.0):
    time.sleep(random.uniform(min_s, max_s))


class NewsScraper:
    def __init__(
        self,
        ru_proxies: list[str] | None = None,
        global_proxies: list[str] | None = None,
        profiles: list[dict[str, str]] | None = None,
        max_retries: int = 1,
        retry_delay: int = 2,
        session_ttl: int = 600
    ) -> None:
        self.ru_proxies_raw: list[str] = ru_proxies or []
        self.global_proxies_raw: list[str] = global_proxies or []
        self.profiles: list[dict[str, str]] = profiles or []
        self.ua: UserAgent = UserAgent()
        self.max_retries: int = max_retries
        self.retry_delay: int = retry_delay
        self.session_ttl: timedelta = timedelta(seconds=session_ttl)

        self.ru_proxies: list[dict[str, str]] = self._prepare_proxies(self.ru_proxies_raw)
        self.global_proxies: list[dict[str, str]] = self._prepare_proxies(self.global_proxies_raw)

        self.sessions: dict[str, tuple[requests.Session, datetime]] = {}
        self.lock: threading.Lock = threading.Lock()

    def _prepare_proxies(self, proxy_list: list[str]) -> list[dict[str, str]]:
        proxies: list[dict[str, str]] = []
        for proxy in proxy_list:
            try:
                ip, port, user, pwd = proxy.strip().split(":")
                proxies.append({
                    "http": f"http://{user}:{pwd}@{ip}:{port}",
                    "https": f"http://{user}:{pwd}@{ip}:{port}"
                })
            except ValueError:
                logger.warning(f"Invalid proxy format: {proxy}")
        return proxies

    def _random_headers(self) -> dict[str, str]:
        return random.choice(self.profiles) if self.profiles else {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,ru-RU;q=0.9",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com/",
        }

    def _get_proxy_list(self, host: str) -> list[dict[str, str]]:
        return self.ru_proxies if host.endswith(".ru") else self.global_proxies

    def _get_session(self, host: str) -> requests.Session:
        now = datetime.now(UTC)

        with self.lock:
            session_data = self.sessions.get(host)
            if session_data:
                session, created = session_data
                if now - created < self.session_ttl:
                    return session

            # Создание новой сессии
            session = requests.Session()
            session.headers.update(self._random_headers())

            proxies = self._get_proxy_list(host)
            if proxies:
                session.proxies.update(random.choice(proxies))

            self.sessions[host] = (session, now)

        return session

    def get_html(self, url: str, timeout: int = 10) -> str:
        host: str = urlparse(url).netloc

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Loading: {url} ...")
                session = self._get_session(host)
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.error(f"[{attempt}] Error: {e}")
                time.sleep(self.retry_delay)
        try:
            logger.info(f"Loading without proxy: {url}")
            response = requests.get(url, headers=self._random_headers(), timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e2:
            logger.error(f"Final attempt without proxy failed: {e2}")

        return None

    def process_news_batch(self, items: list[NewsItem], delay: int = 30) -> list[NewsHtmlItem]:
        results: list[NewsHtmlItem] = []
        for n in items:
            html = self.get_html(url=n.link, timeout=delay)
            human_delay()
            if html:
                results.append((NewsHtmlItem(*n, html=html, success=True)))

        return results