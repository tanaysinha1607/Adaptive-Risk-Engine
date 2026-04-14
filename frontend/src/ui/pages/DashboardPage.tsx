import { useEffect, useMemo, useState } from 'react'
import { AlertsPanel, toAlert } from '../components/AlertsPanel'
import { RiskIndicator } from '../components/RiskIndicator'
import { TradeFeed } from '../components/TradeFeed'
import { fetchMetrics, fetchRisk } from '../lib/api'
import type { ActionEvent, RiskEvent, StreamMessage, TradeEvent } from '../lib/types'
import { useStream } from '../lib/useStream'

const MAX_TRADES = 60
const MAX_ALERTS = 20

export function DashboardPage() {
  const [trades, setTrades] = useState<TradeEvent[]>([])
  const [alerts, setAlerts] = useState<ReturnType<typeof toAlert>[]>([])
  const [risk, setRisk] = useState<{ score: number; action?: string | null } | null>(null)
  const [metrics, setMetrics] = useState<{ trades: number; risk_logs: number } | null>(null)

  const onStreamMessage = (msg: StreamMessage) => {
    if (msg.event === 'trade') {
      const t = msg.data
      setTrades((prev) => [t, ...prev].slice(0, MAX_TRADES))
    } else if (msg.event === 'risk') {
      const r = msg.data as RiskEvent
      const score = r.risk_score ?? r.score ?? 0
      setRisk({ score, action: r.action })
    } else if (msg.event === 'action') {
      const a = msg.data as ActionEvent
      setAlerts((prev) => [toAlert(a), ...prev].slice(0, MAX_ALERTS))
    }
  }

  const stream = useStream(onStreamMessage)

  useEffect(() => {
    let stopped = false
    const run = async () => {
      try {
        const [r, m] = await Promise.all([fetchRisk(), fetchMetrics()])
        if (stopped) return
        setRisk({ score: r.risk_score, action: r.action })
        setMetrics({ trades: m.trades.count, risk_logs: m.risk_logs.count })
      } catch {
        // ignore
      }
    }
    run()
    const t = window.setInterval(run, 3000)
    return () => {
      stopped = true
      window.clearInterval(t)
    }
  }, [])

  const headerRight = useMemo(() => {
    return (
      <div className="meta">
        <div className="metaItem">
          <div className="muted">WS</div>
          <div className={stream.connected ? 'pos mono' : 'neg mono'}>
            {stream.connected ? 'connected' : 'disconnected'}
          </div>
        </div>
        <div className="metaItem">
          <div className="muted">Trades</div>
          <div className="mono">{metrics?.trades ?? '-'}</div>
        </div>
        <div className="metaItem">
          <div className="muted">Risk logs</div>
          <div className="mono">{metrics?.risk_logs ?? '-'}</div>
        </div>
      </div>
    )
  }, [metrics, stream.connected])

  return (
    <div className="page">
      <header className="header">
        <div>
          <div className="kicker">Adaptive Risk Engine</div>
          <div className="h1">Real-time risk dashboard</div>
        </div>
        {headerRight}
      </header>

      <main className="grid">
        <section className="col">
          <RiskIndicator score={risk?.score ?? 0} action={risk?.action ?? null} />
          <AlertsPanel alerts={alerts} />
        </section>

        <section className="col span2">
          <TradeFeed trades={trades} />
        </section>
      </main>

      <footer className="footer muted">
        API: <span className="mono">{import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'}</span>
      </footer>
    </div>
  )
}

