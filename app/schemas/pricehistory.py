from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class PriceHistoryResponse(BaseModel):
    id: int
    game_id: int
    price: Decimal
    recorded_at: datetime

    class Config:
        from_attributes = True