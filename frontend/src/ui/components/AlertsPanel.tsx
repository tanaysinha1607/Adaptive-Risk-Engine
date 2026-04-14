import type { ActionEvent } from '../lib/types'

type Alert = {
  id: string
  at: number
  kind: 'reduce_leverage' | 'block_trades'
  risk: number
  details: Record<string, unknown>
}

type Props = {
  alerts: Alert[]
}

function titleFor(kind: Alert['kind']) {
  return kind === 'block_trades' ? 'Trades blocked' : 'Leverage reduced'
}

export function AlertsPanel({ alerts }: Props) {
  return (
    <div className="card">
      <div className="cardHeader">
        <div>
          <div className="kicker">Actions engine</div>
          <div className="h2">Alerts</div>
        </div>
        <div className="muted">{alerts.length} recent</div>
      </div>

      <div className="alerts">
        {alerts.length === 0 ? (
          <div className="muted">No alerts yet.</div>
        ) : (
          alerts.map((a) => (
            <div className="alert" key={a.id}>
              <div className="row">
                <div className="pill solid">{titleFor(a.kind)}</div>
                <div className="mono muted">{new Date(a.at).toLocaleTimeString()}</div>
              </div>
              <div className="row">
                <div className="muted">Risk</div>
                <div className="mono">{a.risk.toFixed(2)}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export function toAlert(e: ActionEvent): Alert {
  return {
    id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
    at: Date.now(),
    kind: e.action,
    risk: e.risk_score,
    details: e.details,
  }
}

