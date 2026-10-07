from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceHistoryResponse(BaseModel):
    id: int
    game_id: int
    price: Decimal
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
