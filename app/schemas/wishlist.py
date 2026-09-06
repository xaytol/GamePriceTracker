from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class WishlistCreate(BaseModel):
    game_id: int = Field(..., description="ID игры для добавления в вишлист")
    target_price: Decimal = Field(..., gt=0, description="Целевая цена)")


class WishlistUpdate(BaseModel):
    target_price: Decimal = Field(..., gt=0, description="Новая целевая цена")


class WishlistResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    target_price: Decimal
    is_notified: bool
    created_at: datetime

    class Config:
        from_attributes = True