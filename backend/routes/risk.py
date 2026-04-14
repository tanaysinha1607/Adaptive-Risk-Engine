from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.risk_log import RiskLog
from backend.schemas.risk import RiskScoreOut
from backend.services.actions_engine import decide_action
from backend.services.risk_engine import compute_current_risk
from backend.services.stream_manager import stream_manager

router = APIRouter()


@router.get("", response_model=RiskScoreOut)
async def current_risk(db: Session = Depends(get_db)) -> RiskScoreOut:
    result = compute_current_risk(db)
    decision = decide_action(float(result.risk_score))

    risk_log = RiskLog(
        risk_score=float(result.risk_score),
        explanation=result.explanation,
        action=decision.action,
    )
    db.add(risk_log)
    db.commit()

    await stream_manager.broadcast(
        "risk",
        {
            "risk_score": float(result.risk_score),
            "anomaly_score": float(result.anomaly_score),
            "explanation": result.explanation,
            "action": decision.action,
            "score": float(result.risk_score),
        },
    )
    return RiskScoreOut(
        risk_score=float(result.risk_score),
        anomaly_score=float(result.anomaly_score),
        score=float(result.risk_score),
        explanation=result.explanation,
        action=decision.action,
    )

