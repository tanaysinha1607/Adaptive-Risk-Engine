from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class AnomalyResult:
    anomaly_score: float  # 0..1
    anomaly_flag: bool
    reasons: list[str]
    model: str


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _safe_z(value: float, mean: float, stdev: float) -> float:
    if stdev <= 1e-9:
        return 0.0
    return (value - mean) / stdev


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _stdev(xs: list[float]) -> float:
    if not xs:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def _sigmoid(x: float) -> float:
    # stable-ish sigmoid for moderate x
    return 1.0 / (1.0 + math.exp(-x))


def detect_anomaly(recent_trades: list[dict]) -> AnomalyResult:
    """
    Input: list of recent trades (newest-first or oldest-first OK) with keys:
      - amount: float
      - leverage: float
      - timestamp: datetime

    Output:
      - anomaly_score in [0,1]
      - anomaly_flag boolean
      - reasons list
    """
    if len(recent_trades) < 10:
        return AnomalyResult(anomaly_score=0.0, anomaly_flag=False, reasons=[], model="insufficient_data")

    # Normalize ordering oldest -> newest for frequency features
    trades = sorted(recent_trades, key=lambda t: t["timestamp"])
    amounts = [float(t["amount"]) for t in trades]
    leverages = [float(t["leverage"]) for t in trades]
    times: list[dt.datetime] = [t["timestamp"] for t in trades]

    # Trade frequency as trades/second based on inter-arrival times
    rates: list[float] = []
    for i in range(1, len(times)):
        delta = (times[i] - times[i - 1]).total_seconds()
        if delta <= 0:
            continue
        rates.append(1.0 / delta)

    last_amount = amounts[-1]
    last_lev = leverages[-1]
    last_rate = rates[-1] if rates else 0.0

    # Try sklearn IsolationForest first
    try:
        from sklearn.ensemble import IsolationForest  # type: ignore

        X = []
        rate_fill = _mean(rates) if rates else 0.0
        for i in range(len(trades)):
            r = rate_fill
            if i > 0 and i - 1 < len(rates):
                r = rates[i - 1]
            X.append([amounts[i], leverages[i], r])

        iso = IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=42,
        )
        iso.fit(X)

        # decision_function: higher = more normal. score_samples: higher = more normal.
        raw = float(iso.score_samples([X[-1]])[0])
        # Map to 0..1 anomaly (invert). Raw values are unbounded-ish; squash.
        anomaly_score = _clamp01(1.0 - _sigmoid(raw))
        anomaly_flag = anomaly_score >= 0.7

        reasons: list[str] = []
        if last_lev >= 60:
            reasons.append("High leverage detected")
        if last_rate > (_mean(rates) + 2 * _stdev(rates)):
            reasons.append("Unusual trading spike")
        if anomaly_flag:
            reasons.append("Anomalous behavior detected")

        return AnomalyResult(
            anomaly_score=anomaly_score,
            anomaly_flag=anomaly_flag,
            reasons=reasons,
            model="isolation_forest",
        )
    except Exception:
        # fallback below
        pass

    # Statistical fallback: z-scores on last trade vs window
    amt_mu, amt_sd = _mean(amounts[:-1]), _stdev(amounts[:-1])
    lev_mu, lev_sd = _mean(leverages[:-1]), _stdev(leverages[:-1])
    rate_mu, rate_sd = _mean(rates[:-1]) if len(rates) > 1 else _mean(rates), _stdev(rates[:-1]) if len(rates) > 1 else _stdev(rates)

    z_amt = abs(_safe_z(last_amount, amt_mu, amt_sd))
    z_lev = abs(_safe_z(last_lev, lev_mu, lev_sd))
    z_rate = abs(_safe_z(last_rate, rate_mu, rate_sd))

    z_max = max(z_amt, z_lev, z_rate)
    # Map z to 0..1 (z~3 => ~0.7, z~5 => ~0.9)
    anomaly_score = _clamp01(_sigmoid((z_max - 2.5) * 1.1))
    anomaly_flag = z_max >= 3.0

    reasons: list[str] = []
    if z_lev >= 2.5 or last_lev >= 60:
        reasons.append("High leverage detected")
    if z_rate >= 2.5:
        reasons.append("Unusual trading spike")
    if anomaly_flag:
        reasons.append("Anomalous behavior detected")

    return AnomalyResult(
        anomaly_score=anomaly_score,
        anomaly_flag=anomaly_flag,
        reasons=reasons,
        model="zscore",
    )

