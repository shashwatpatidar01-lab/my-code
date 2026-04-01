import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "LiteHotel HMS"
    secret_key: str = os.getenv("SECRET_KEY", "change-me-super-secret-key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = ""


def resolve_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    if os.getenv("VERCEL"):
        return "sqlite:////tmp/hotel.db"

    return f"sqlite:///{Path('hotel.db').resolve()}"


settings = Settings(database_url=resolve_database_url())
