type Props = {
  score: number
  action?: string | null
}

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n))
}

function colorFor(score: number) {
  if (score >= 85) return 'var(--danger)'
  if (score >= 70) return 'var(--warn)'
  return 'var(--ok)'
}

export function RiskIndicator({ score, action }: Props) {
  const pct = clamp(score, 0, 100)
  const color = colorFor(pct)
  const label = pct >= 85 ? 'High' : pct >= 70 ? 'Elevated' : 'Normal'

  return (
    <div className="card">
      <div className="cardHeader">
        <div>
          <div className="kicker">Risk score</div>
          <div className="h2">
            {pct.toFixed(2)} <span className="muted">/ 100</span>
          </div>
        </div>
        <div className="pill" style={{ borderColor: color, color }}>
          {label}
        </div>
      </div>

      <div className="bar" aria-label="risk">
        <div className="barFill" style={{ width: `${pct}%`, background: color }} />
      </div>

      <div className="row">
        <div className="muted">Policy</div>
        <div className="mono">{action ?? 'none'}</div>
      </div>
    </div>
  )
}

