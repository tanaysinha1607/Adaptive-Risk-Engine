import { getApiBaseUrl } from './env'

export async function fetchRisk() {
  const res = await fetch(`${getApiBaseUrl()}/risk`)
  if (!res.ok) throw new Error(`risk_failed_${res.status}`)
  const data = (await res.json()) as {
    risk_score?: number
    anomaly_score?: number
    score?: number
    explanation: Record<string, unknown>
    action?: string | null
  }
  return {
    risk_score: data.risk_score ?? data.score ?? 0,
    anomaly_score: data.anomaly_score ?? 0,
    explanation: data.explanation,
    action: data.action ?? null,
  }
}

export async function fetchMetrics() {
  const res = await fetch(`${getApiBaseUrl()}/metrics`)
  if (!res.ok) throw new Error(`metrics_failed_${res.status}`)
  return (await res.json()) as {
    trades: { count: number; last_timestamp: string | null }
    risk_logs: { count: number; last_timestamp: string | null }
  }
}

