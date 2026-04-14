import type { TradeEvent } from '../lib/types'

type Props = {
  trades: TradeEvent[]
}

export function TradeFeed({ trades }: Props) {
  return (
    <div className="card">
      <div className="cardHeader">
        <div>
          <div className="kicker">Live trade feed</div>
          <div className="h2">Trades</div>
        </div>
        <div className="muted">{trades.length} shown</div>
      </div>

      <div className="table">
        <div className="thead">
          <div>Time</div>
          <div>User</div>
          <div>Asset</div>
          <div>Side</div>
          <div className="right">Amount</div>
          <div className="right">Lev</div>
        </div>
        {trades.map((t) => (
          <div className="trow" key={t.id}>
            <div className="mono">{new Date(t.timestamp).toLocaleTimeString()}</div>
            <div className="mono">{t.user_id}</div>
            <div className="mono">{t.asset}</div>
            <div className={t.type === 'buy' ? 'pos' : 'neg'}>{t.type.toUpperCase()}</div>
            <div className="right mono">{t.amount.toLocaleString()}</div>
            <div className="right mono">{t.leverage.toFixed(0)}x</div>
          </div>
        ))}
      </div>
    </div>
  )
}

