from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str | None = None
    calil_appkey: str | None = None
    default_city: str = "宮崎市"
    ndl_api_base: str = "https://iss.ndl.go.jp/api/opensearch"
    cinii_base: str = "https://ci.nii.ac.jp/books/opensearch/search"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="", extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()
