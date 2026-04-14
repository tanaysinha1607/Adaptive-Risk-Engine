from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.risk_log import RiskLog
from backend.models.trade import Trade


def get_metrics(db: Session) -> dict:
    trade_count = db.scalar(select(func.count()).select_from(Trade)) or 0
    last_trade_ts = db.scalar(select(func.max(Trade.timestamp)))
    risklog_count = db.scalar(select(func.count()).select_from(RiskLog)) or 0
    last_risk_ts = db.scalar(select(func.max(RiskLog.created_at)))

    return {
        "trades": {"count": int(trade_count), "last_timestamp": last_trade_ts},
        "risk_logs": {"count": int(risklog_count), "last_timestamp": last_risk_ts},
    }

