import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from backend.core.config import settings
from backend.db.session import init_db
from backend.routes.health import router as health_router
from backend.routes.metrics import router as metrics_router
from backend.routes.risk import router as risk_router
from backend.routes.stream import router as stream_router
from backend.routes.trade import router as trade_router
from backend.services.simulator import trade_simulator

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Adaptive Risk Engine", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # We don't use cookies/auth headers that require credentials.
        # Keeping this False allows wildcard origins to work in browsers.
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(trade_router, prefix="/trade", tags=["trade"])
    app.include_router(risk_router, prefix="/risk", tags=["risk"])
    app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
    app.include_router(stream_router, tags=["stream"])

    @app.on_event("startup")
    async def _startup() -> None:
        db_ready = False
        for attempt in range(1, 6):
            try:
                init_db()
                db_ready = True
                break
            except OperationalError as e:
                logger.warning("DB init failed (attempt %s/5): %s", attempt, e)
                await asyncio.sleep(min(8.0, 0.8 * attempt))

        if not db_ready:
            logger.error("DB init failed after retries; API will start without DB")
            return

        if settings.enable_simulator:
            trade_simulator.start()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await trade_simulator.stop()

    return app


app = create_app()
