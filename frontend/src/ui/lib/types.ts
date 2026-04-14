export type TradeEvent = {
  id: number
  user_id: string
  asset: string
  type: 'buy' | 'sell'
  amount: number
  leverage: number
  timestamp: string
}

export type RiskEvent = {
  risk_score?: number
  anomaly_score?: number
  score?: number
  explanation: Record<string, unknown>
  action?: string | null
}

export type ActionEvent = {
  action: 'reduce_leverage' | 'block_trades'
  risk_score: number
  details: Record<string, unknown>
}

export type StreamMessage =
  | { event: 'trade'; data: TradeEvent }
  | { event: 'risk'; data: RiskEvent }
  | { event: 'action'; data: ActionEvent }
