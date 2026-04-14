from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    asset: str = Field(min_length=1, max_length=32)
    type: Literal["buy", "sell"]
    amount: float = Field(gt=0)
    leverage: float = Field(gt=0, le=500)
    timestamp: dt.datetime | None = None


class TradeOut(BaseModel):
    id: int
    user_id: str
    asset: str
    type: Literal["buy", "sell"]
    amount: float
    leverage: float
    timestamp: dt.datetime

    class Config:
        from_attributes = True

