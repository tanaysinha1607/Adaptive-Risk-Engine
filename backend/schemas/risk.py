from __future__ import annotations

from pydantic import BaseModel, Field


class RiskScoreOut(BaseModel):
    # Keep `score` for backward compatibility; `risk_score` is the new canonical field.
    risk_score: float = Field(ge=0, le=100)
    anomaly_score: float = Field(ge=0, le=1)
    score: float = Field(ge=0, le=100)
    explanation: dict
    action: str | None = None

