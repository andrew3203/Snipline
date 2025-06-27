import asyncio
import logging
import random
import shutil
import tempfile
import time
from uuid import uuid4

from playwright.async_api import async_playwright

from src.parser.model import NewsHtmlItem, NewsItem

logger = logging.getLogger(__name__)


def human_delay(min_s=1.0, max_s=3.0):
    time.sleep(random.uniform(min_s, max_s))


async def init_browser(task_id: str):
    user_data_dir = tempfile.mkdtemp(prefix=f"playwright_profile_{task_id}_")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--lang=en-US,ru-RU,en",
            "--window-size=1920,1080",
        ],
        locale="en-US",
    )
    return playwright, browser, user_data_dir


async def accept_cookies(page, keywords=None, delay: int = 1) -> bool:
    if keywords is None:
        keywords = [
            "i accept", "allow all", "allow", "accept", "agree", "yes", "i agree", "accept all",
            "принять все", "принять", "согласен", "разрешить", "разрешить все"
        ]

    try:
        buttons = await page.query_selector_all('button, [role="button"]')
        for btn in buttons:
            text = (await btn.inner_text()).strip().lower()
            if any(k in text for k in keywords):
                await btn.click()
                await asyncio.sleep(delay)
                return True
    except Exception:
        pass
    return False


async def get_html_with_page(page, url: str, delay: int = 5) -> tuple[str, bool]:
    try:
        logger.info(f"Loading {url} ...")
        await page.goto(url, timeout=60000)
        await accept_cookies(page)
        await asyncio.sleep(random.uniform(1, 3))
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await page.wait_for_load_state("load", timeout=delay * 1000)
        html = await page.content()
        return html, True
    except Exception as e:
        logger.error(f"Error loading page {url}: {str(e)}", exc_info=True)
        return str(e), False


async def process_news_batch(items: list[NewsItem], delay: int = 5) -> list[NewsHtmlItem]:
    task_id = str(uuid4())
    playwright, browser, profile_dir = await init_browser(task_id)
    page = await browser.new_page()
    results = []
    try:
        for item in items:
            html, success = await get_html_with_page(page, item.link, delay=delay)
            results.append(
                NewsHtmlItem(
                    *item,
                    html=html if success else None,
                    success=success,
                )
            )
    finally:
        await browser.close()
        await playwright.stop()
        shutil.rmtree(profile_dir)
    return results
