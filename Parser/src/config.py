import os


class Settings:
    REDIS_URL: str = os.environ.get("REDIS_URL")
    SLEEP_TIME: int = int(os.environ.get("SLEEP_TIME", 600))


settings = Settings()