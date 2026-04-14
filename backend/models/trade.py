from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.session import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    asset: Mapped[str] = mapped_column(String(32), index=True)
    type: Mapped[str] = mapped_column(String(8))  # buy/sell
    amount: Mapped[float] = mapped_column(Float)
    leverage: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc), index=True
    )

    __table_args__ = (
        Index("ix_trades_user_ts", "user_id", "timestamp"),
        Index("ix_trades_asset_ts", "asset", "timestamp"),
    )

