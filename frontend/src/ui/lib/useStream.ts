import { useEffect, useMemo, useRef, useState } from 'react'
import { getWsUrl } from './env'
import type { StreamMessage } from './types'

type StreamState = {
  connected: boolean
  lastMessageAt: number | null
}

export function useStream(onMessage: (msg: StreamMessage) => void) {
  const [state, setState] = useState<StreamState>({ connected: false, lastMessageAt: null })
  const wsUrl = useMemo(() => getWsUrl(), [])
  const onMessageRef = useRef(onMessage)

  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  useEffect(() => {
    let ws: WebSocket | null = null
    let stopped = false
    let reconnectTimer: number | null = null

    const connect = () => {
      if (stopped) return
      ws = new WebSocket(wsUrl)

      ws.onopen = () => setState((s) => ({ ...s, connected: true }))
      ws.onclose = () => {
        setState((s) => ({ ...s, connected: false }))
        if (!stopped) {
          reconnectTimer = window.setTimeout(connect, 800)
        }
      }
      ws.onerror = () => {
        // onclose will handle reconnect
      }
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data) as StreamMessage
          onMessageRef.current(msg)
          setState({ connected: true, lastMessageAt: Date.now() })
        } catch {
          // ignore
        }
      }
    }

    connect()

    const pingTimer = window.setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) ws.send('ping')
    }, 15000)

    return () => {
      stopped = true
      window.clearInterval(pingTimer)
      if (reconnectTimer) window.clearTimeout(reconnectTimer)
      ws?.close()
      ws = null
    }
  }, [wsUrl])

  return state
}

