from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.trade import TradeCreate, TradeOut
from backend.services.trade_service import TradeBlockedError, create_trade

router = APIRouter()


@router.post("", response_model=TradeOut)
async def ingest_trade(payload: TradeCreate, db: Session = Depends(get_db)) -> TradeOut:
    try:
        return await create_trade(db, payload)
    except TradeBlockedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "trade_blocked", "risk_score": e.risk_score},
        ) from e

