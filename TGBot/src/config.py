import os


class Settings:
    REDIS_URL: str = os.environ.get("REDIS_URL",)
    SLEEP_TIME: int = int(os.environ.get("SLEEP_TIME", 600))
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN")

    SEND_PERIOD: int =  os.environ.get("SEND_PERIOD", 60)
    MAX_CALLS: int =  os.environ.get("MAX_CALLS", 180)


settings = Settings()