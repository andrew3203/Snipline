import asyncio
import signal
import logging
import logging.config

from config.settings import settings
from src.application.scripts import news, scheduler

logging.config.fileConfig(settings.logging_path, disable_existing_loggers=False)

logger = logging.getLogger(__name__)


async def main():
    news_model = await news.run()
    scheduler_model = await scheduler.run()

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    logger.info("Stop signal recived, shutdown…")

    try:
        await news_model.stop()
        await scheduler_model.shutdown(wait=True)
        logger.info("End of service")
    except Exception as e:
        logger.exception("Stop error: %s", e)


if __name__ == "__main__":
    asyncio.run(main())
