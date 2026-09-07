from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal


class GameCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Название игры")
    external_id: str = Field(..., description="ID игры во внешнем магазине")
    current_price: Decimal = Field(..., ge=0, description="Текущая цена")
    image_url: Optional[str] = Field(None, description="URL обложки игры")


class GameUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    current_price: Optional[Decimal] = Field(None, ge=0)
    image_url: Optional[str] = None


class GameResponse(BaseModel):
    id: int
    title: str
    external_id: str
    current_price: Decimal
    image_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)