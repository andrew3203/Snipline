import logging
import os
import shutil
import tempfile
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
import time
from uuid import uuid4
import random

from src.parser.model import NewsHtmlItem, NewsItem


logger = logging.getLogger(__name__)


def human_delay(min_s=1.0, max_s=3.0):
    time.sleep(random.uniform(min_s, max_s))

def init_driver(task_id: str, driver_path: str) -> uc.Chrome:
    chrome_options = uc.ChromeOptions()
    # chrome_options.headless = True
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--remote-debugging-port=0")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    prefs = {
        "profile.default_content_setting_values.notifications": 1,
        "intl.accept_languages": "en_US,ru_RU,en",
    }
    chrome_options.add_experimental_option("prefs", prefs)

    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-setuid-sandbox")

    # 🔧 Улучшение стабильности и скорости
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")

    # 🛡️ Отключаем "умные" оптимизации
    chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--disable-default-apps")

    # 🧠 Снижение fingerprint-а
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")

    # 🌍 Убираем прокси, если не нужен
    chrome_options.add_argument("--no-proxy-server")

    # 🧪 Иногда помогает с JavaScript-heavy сайтами
    chrome_options.add_argument("--enable-automation")

    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome-profile-{task_id}")
    chrome_options.add_argument("--lang=en-US,ru-RU,en")

    driver = uc.Chrome(
        options=chrome_options,
        version_main=135,
        driver_executable_path=driver_path,
        patcher_force_close=True,

    )
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {},
            };
            window.navigator.permissions.query = (parameters) =>
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : Promise.resolve({ state: 'denied' });
        """
    })

    return driver


def wait_for_page_load(driver: uc.Chrome, delay: int) -> None:
    WebDriverWait(driver, delay).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def accept_cookies(driver, keywords=None, delay: int = 1) -> bool:
    """
    Пытается найти и кликнуть на кнопку принятия cookies.
    :param driver: объект Selenium WebDriver
    :param keywords: список ключевых слов для кнопок (по умолчанию английские и русские варианты)
    :param delay: пауза после клика (в секундах)
    :return: True если клик произошёл, иначе False
    """
    if keywords is None:
        keywords = [
            "i accept",
            "allow all",
            "allow",
            "accept", "agree", "yes", "i agree", "accept all", "принять все", "принять", "согласен", "разрешить", "разрешить все"
        ]

    try:
        candidates = driver.find_elements(By.XPATH, '//button | //*[@role="button"]')
        for elem in candidates:
            try:
                text = elem.text.strip().lower()
                if any(k in text for k in keywords):
                    elem.click()
                    human_delay()
                    return True
            except Exception:
                continue

        inputs = driver.find_elements(By.XPATH, '//input[@type="submit"]')
        for inp in inputs:
            try:
                value = inp.get_attribute("value").lower()
                if any(k in value for k in keywords):
                    inp.click()
                    human_delay()
                    return True
            except Exception:
                continue

    except (ElementClickInterceptedException, NoSuchElementException):
        pass

    return False


def scroll_to_bottom(driver: uc.Chrome):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    human_delay()


def get_html_with_driver(driver: uc.Chrome, url: str, delay: int = 5) -> tuple[str, bool]:
    try:
        logger.info(f"Loading {url} ...")
        driver.get(url)
        accept_cookies(driver)
        human_delay()
        scroll_to_bottom(driver)
        wait_for_page_load(driver=driver, delay=delay)
        html = driver.page_source
        return html, True
    except TimeoutException as e:
        logger.warning(f"Page load timed out for {url}")
        return str(e), False
    except Exception as e:
        logger.error(f"Error loading page {url}: {str(e)}", exc_info=True)
        return str(e), False

def copy_driver() -> str:
    tmp_driver_dir = tempfile.mkdtemp(prefix="chromedriver_")
    driver_copy_path = os.path.join(tmp_driver_dir, "chromedriver")
    shutil.copy("/usr/local/bin/chromedriver", driver_copy_path)
    os.chmod(driver_copy_path, 0o755)
    return driver_copy_path

def process_news_batch(items: list[NewsItem], delay: int = 5) -> list[NewsHtmlItem]:
    task_id = str(uuid4())
    driver_copy_path = copy_driver()
    
    time.sleep(random.uniform(0.5, 1.5))
    driver = init_driver(task_id, driver_path=driver_copy_path)
    results = []
    try:
        for item in items:
            html, success = get_html_with_driver(
                driver=driver,
                url=item.link,
                delay=delay,
            )
            results.append(
                NewsHtmlItem(
                    *item,
                    html=html if success else None,
                    success=success,
                )
            )
    finally:
        driver.quit()
        shutil.rmtree(os.path.dirname(driver_copy_path))
    return results