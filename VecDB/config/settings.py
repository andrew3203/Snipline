from typing import Any
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    LOG_LEVEL: str = Field(default="INFO")
    APP_VERSION: str = Field(default="1.0")
    DEBUG: bool = Field(default=True)

    CORS_ORIGINS: str = Field(description="origins")
    CORS_ORIGINS_REGEX: str | None = Field(description="redex", default=None)
    CORS_HEADERS: str = Field(description="headers")

    QDRANT_HOST: str = Field(description="Qdrant host")
    COLLECTION_NAME: str = Field(description="Qdrant collection name")
    QDRANT_PORT: int = Field(description="Qdrant port", default=6333)
    EMBEDDING_DIM: int = Field(description="Embendings dim", default=512)

    EMBEDDING_SERVICE_URL: str = Field(description="Embendins service")
    EMBEDDING_MODEL: str = Field(description="Embending model name")

    @property
    def cors_origins_list(self) -> list[str]:
        return [i.strip() for i in self.CORS_ORIGINS.split(",")]

    @property
    def cors_origins_regex_list(self) -> list[str] | None:
        return [i.strip() for i in self.CORS_ORIGINS_REGEX.split(",")] if self.CORS_ORIGINS_REGEX else None

    @property
    def cors_headers_list(self) -> list[str]:
        return [i.strip() for i in self.CORS_HEADERS.split(",")]

    @property
    def logging_path(self) -> str:
        return "logging.ini" if self.DEBUG else "logging_production.ini"

    # model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

app_configs: dict[str, Any] = {
    "title": "Vec DB API",
    "version": settings.APP_VERSION,
    "debug": settings.DEBUG,
}