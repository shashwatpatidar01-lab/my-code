from datetime import datetime
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Message(BaseModel):
    message: str


class Timestamped(BaseModel):
    created_at: datetime
