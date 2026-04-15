from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.trade import TradeCreate, TradeOut
from backend.services.trade_service import create_trade

router = APIRouter()


@router.post("", response_model=TradeOut)
async def ingest_trade(payload: TradeCreate, db: Session = Depends(get_db)) -> TradeOut:
    return await create_trade(db, payload)

