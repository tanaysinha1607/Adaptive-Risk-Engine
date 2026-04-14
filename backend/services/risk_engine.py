from __future__ import annotations

import math
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ai.risk_model import detect_anomaly
from backend.models.trade import Trade


@dataclass(frozen=True)
class RiskResult:
    risk_score: float
    anomaly_score: float
    anomaly_flag: bool
    explanation: dict


def compute_current_risk(db: Session, lookback_trades: int = 500) -> RiskResult:
    """
    Simple, deterministic risk score (0-100) based on:
    - total exposure (sum(amount * leverage))
    - average leverage
    - volatility proxy (recent trade size variance)
    """
    recent = (
        db.execute(
            select(Trade.amount, Trade.leverage, Trade.asset, Trade.timestamp)
            .order_by(Trade.timestamp.desc())
            .limit(lookback_trades)
        )
        .all()
    )

    if not recent:
        return RiskResult(
            risk_score=0.0,
            anomaly_score=0.0,
            anomaly_flag=False,
            explanation={"reason": "no_trades"},
        )

    exposures = [float(a) * float(l) for (a, l, _asset, _ts) in recent]
    total_exposure = sum(exposures)
    avg_leverage = sum(float(l) for (_a, l, _asset, _ts) in recent) / len(recent)

    mean_amt = sum(float(a) for (a, _l, _asset, _ts) in recent) / len(recent)
    var_amt = sum((float(a) - mean_amt) ** 2 for (a, _l, _asset, _ts) in recent) / len(recent)
    stdev_amt = math.sqrt(var_amt)

    # Normalize into 0..100 with soft caps to keep it stable.
    exposure_component = min(60.0, 60.0 * (math.log10(total_exposure + 1.0) / 6.0))  # ~1e6 hits cap
    leverage_component = min(25.0, 25.0 * (avg_leverage / 100.0))
    vol_component = min(15.0, 15.0 * (math.log10(stdev_amt + 1.0) / 4.0))  # stdev ~1e4 hits cap

    base_risk = max(0.0, min(100.0, exposure_component + leverage_component + vol_component))

    anomaly_input = [
        {"amount": float(a), "leverage": float(l), "timestamp": ts}
        for (a, l, _asset, ts) in recent
    ]
    anomaly = detect_anomaly(anomaly_input)
    final_risk = max(0.0, min(100.0, base_risk * 0.7 + float(anomaly.anomaly_score) * 30.0))

    explanation = {
        "lookback_trades": len(recent),
        "total_exposure": total_exposure,
        "avg_leverage": avg_leverage,
        "amount_stdev": stdev_amt,
        "base_risk": base_risk,
        "anomaly": {
            "score": anomaly.anomaly_score,
            "flag": anomaly.anomaly_flag,
            "model": anomaly.model,
            "reasons": anomaly.reasons,
        },
        "components": {
            "exposure": exposure_component,
            "leverage": leverage_component,
            "volatility": vol_component,
        },
        "signals": anomaly.reasons,
    }
    return RiskResult(
        risk_score=final_risk,
        anomaly_score=float(anomaly.anomaly_score),
        anomaly_flag=bool(anomaly.anomaly_flag),
        explanation=explanation,
    )

