from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from backend.models.risk_log import RiskLog
from backend.models.trade import Trade
from backend.schemas.trade import TradeCreate
from backend.services.actions_engine import decide_action
from backend.services.risk_engine import compute_current_risk
from backend.services.stream_manager import stream_manager


async def create_trade(db: Session, payload: TradeCreate) -> Trade:
    ts = payload.timestamp
    if ts is None:
        ts = dt.datetime.now(dt.timezone.utc)
    elif ts.tzinfo is None:
        ts = ts.replace(tzinfo=dt.timezone.utc)

    risk = compute_current_risk(db)
    decision = decide_action(float(risk.risk_score))

    leverage = float(payload.leverage)
    action_details: dict | None = None
    blocked = False

    if decision.action == "block_trades":
        # Simulate trade blocking as a policy decision, but still persist/broadcast
        # the trade so the live dashboard continues to update in high-risk regimes.
        blocked = True
        db.add(
            RiskLog(
                risk_score=float(risk.risk_score),
                explanation={**risk.explanation, "action": decision.details},
                action="block_trades",
            )
        )
        db.commit()

        await stream_manager.broadcast(
            "action",
            {"action": "block_trades", "risk_score": float(risk.risk_score), "details": decision.details},
        )

    if decision.action == "reduce_leverage":
        new_leverage = max(1.0, min(leverage, 20.0))
        if new_leverage != leverage:
            action_details = {
                **decision.details,
                "old_leverage": leverage,
                "new_leverage": new_leverage,
            }
            leverage = new_leverage

            db.add(
                RiskLog(
                    risk_score=float(risk.risk_score),
                    explanation={**risk.explanation, "action": action_details},
                    action="reduce_leverage",
                )
            )
            db.commit()

            await stream_manager.broadcast(
                "action",
                {
                    "action": "reduce_leverage",
                    "risk_score": float(risk.risk_score),
                    "details": action_details,
                },
            )

    trade = Trade(
        user_id=payload.user_id,
        asset=payload.asset,
        type=payload.type,
        amount=float(payload.amount),
        leverage=float(leverage),
        timestamp=ts,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    await stream_manager.broadcast(
        "trade",
        {
            "id": trade.id,
            "user_id": trade.user_id,
            "asset": trade.asset,
            "type": trade.type,
            "amount": trade.amount,
            "leverage": trade.leverage,
            "timestamp": trade.timestamp.isoformat(),
            "blocked": blocked,
        },
    )
    return trade
