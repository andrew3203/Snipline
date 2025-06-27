from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DEBUG: bool = Field(description="Debug", default=False)

    POSTGRES_USER: str = Field(description="")
    POSTGRES_PASSWORD: str = Field(description="")
    POSTGRES_HOST: str = Field(description="")
    POSTGRES_PORT: str = Field(description="")
    POSTGRES_DB: str = Field(description="")

    REDIS_URL: str = Field(description="")

    LLM_URL: str = Field(description="")
    LLM_API_KEY: str = Field(description="")

    YOOKASSA_SHOP_ID: str = Field(description="")
    YOOKASSA_SECRET: str = Field(description="")
    YOOKASSA_RETURN_URL: str = Field(description="")

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def logging_path(self) -> str:
        return "logging.ini" if self.DEBUG else "logging_production.ini"


settings = Settings()
