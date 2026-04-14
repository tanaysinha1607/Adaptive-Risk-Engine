from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionDecision:
    action: str | None
    details: dict


def decide_action(risk_score: float) -> ActionDecision:
    """
    Policy:
    - risk > 85: block trades (simulated by rejecting ingestion)
    - risk > 70: reduce leverage
    """
    if risk_score > 85:
        return ActionDecision(action="block_trades", details={"threshold": 85})
    if risk_score > 70:
        return ActionDecision(action="reduce_leverage", details={"threshold": 70})
    return ActionDecision(action=None, details={})

