import asyncio
from src.repo.stream.redis import RedisConnector
from .report import ReportService

async def start():
    redis_connector = RedisConnector(stream_name="notifications", stop_event=asyncio.Event())
    service = ReportService()
    await redis_connector.start_read(handle=service.handle)