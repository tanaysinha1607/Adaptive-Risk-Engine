from __future__ import annotations

import asyncio
import datetime as dt
import logging
import random
from contextlib import suppress

from backend.db.session import SessionLocal
from backend.schemas.trade import TradeCreate
from backend.services.trade_service import create_trade

logger = logging.getLogger(__name__)


class TradeSimulator:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._running = False
        self._spike_until: float = 0.0
        self._next_spike_at: float = 0.0

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._running = True
        loop = asyncio.get_running_loop()
        now = loop.time()
        self._next_spike_at = now + random.uniform(20.0, 30.0)
        self._task = loop.create_task(self._run(), name="trade-simulator")

    async def stop(self) -> None:
        self._running = False
        if self._task is None:
            return
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def _run(self) -> None:
        while self._running:
            mode = self._update_market_mode()
            msg = "Volatility spike triggered!" if mode == "spike" else "Normal trading..."
            logger.info(msg)
            print(msg, flush=True)

            db = SessionLocal()
            try:
                payload = self._generate_trade(mode)
                await create_trade(db, payload)
            except Exception:
                logger.exception("Trade simulator failed to create trade")
            finally:
                db.close()

            await asyncio.sleep(random.uniform(0.5, 1.0))

    def _update_market_mode(self) -> str:
        now = asyncio.get_running_loop().time()
        if now >= self._next_spike_at and now >= self._spike_until:
            self._spike_until = now + random.uniform(5.0, 8.0)
            self._next_spike_at = self._spike_until + random.uniform(20.0, 30.0)
            return "spike"
        if now < self._spike_until:
            return "spike"
        return "normal"

    def _generate_trade(self, mode: str) -> TradeCreate:
        asset = random.choice(["BTC", "ETH", "EURUSD"])
        trade_type = random.choice(["buy", "sell"])
        user_id = str(random.randint(1000, 9999))

        if mode == "spike":
            if asset == "BTC":
                amount = round(random.uniform(5000, 25000), 2)
            elif asset == "ETH":
                amount = round(random.uniform(2500, 12000), 2)
            else:
                amount = round(random.uniform(100000, 500000), 2)
            leverage = random.randint(60, 100)
        else:
            if asset == "BTC":
                amount = round(random.uniform(100, 4000), 2)
            elif asset == "ETH":
                amount = round(random.uniform(50, 2500), 2)
            else:
                amount = round(random.uniform(1000, 50000), 2)
            leverage = random.randint(1, 40)

        return TradeCreate(
            user_id=user_id,
            asset=asset,
            type=trade_type,
            amount=amount,
            leverage=leverage,
            timestamp=dt.datetime.now(dt.timezone.utc),
        )


trade_simulator = TradeSimulator()
