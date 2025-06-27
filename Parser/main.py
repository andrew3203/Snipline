import logging
import logging.config
from src.scripts.loop import main_loop

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    sleep_time = 600
    main_loop(sleep_time=sleep_time)