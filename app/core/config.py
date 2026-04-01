from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "LiteHotel HMS"
    secret_key: str = "change-me-super-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "sqlite:///./hotel.db"


settings = Settings()
