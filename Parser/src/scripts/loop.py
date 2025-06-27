import logging
import signal
import threading

from src.scripts.parse import parse_articles
from src.utils.redis import RedisConnector

logger = logging.getLogger(__name__)

stop_event = threading.Event()

def handle_signal(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    stop_event.set()

signal.signal(signal.SIGINT, handle_signal)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_signal)  # Docker stop


def main_loop(sleep_time: float):
    connector = RedisConnector("raw_news", stop_event)
    connector.start()
    while not stop_event.is_set():
        try:
             parse_articles(connector=connector)
        except Exception as e:
            logger.error(f"Error during parsing: {e}", exc_info=True)

        if stop_event.wait(sleep_time):
            connector.stop()
            break 
    logger.info("Shutdown complete.")

