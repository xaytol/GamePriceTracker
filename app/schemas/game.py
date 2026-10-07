from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GameCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Название игры")
    external_id: str = Field(..., description="ID игры во внешнем магазине")
    current_price: Decimal = Field(..., ge=0, description="Текущая цена")
    image_url: str | None = Field(None, description="URL обложки игры")


class GameUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    current_price: Decimal | None = Field(None, ge=0)
    image_url: str | None = None


class GameResponse(BaseModel):
    id: int
    title: str
    external_id: str
    current_price: Decimal
    image_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
