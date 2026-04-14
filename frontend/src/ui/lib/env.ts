export function getApiBaseUrl() {
  return (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://127.0.0.1:8000'
}

export function getWsUrl() {
  const api = getApiBaseUrl()
  const u = new URL(api)
  u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'
  u.pathname = '/stream'
  u.search = ''
  u.hash = ''
  return u.toString()
}

