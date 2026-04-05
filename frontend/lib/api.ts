const API_BASE = 'https://chartwise-ai.onrender.com'

// Helper to get auth token
function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('chartwise_token')
  }
  return null
}

// Helper to create headers with auth
function getHeaders(includeAuth: boolean = true): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  }
  
  if (includeAuth) {
    const token = getAuthToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }
  
  return headers
}

// Handle API errors
async function handleResponse(response: Response) {
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('chartwise_token')
      window.location.href = '/login'
      throw new Error('Session expired. Please login again.')
    }
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }))
    throw new Error(error.detail || 'Request failed')
  }
  return response.json()
}

// Public endpoints (no auth required)
export async function fetchTopPicks(limit = 10) {
  const res = await fetch(`${API_BASE}/api/predictions/top-picks?limit=${limit}`)
  if (!res.ok) throw new Error('Failed to fetch top picks')
  return res.json()
}

export async function fetchStockPrediction(symbol: string) {
  const res = await fetch(`${API_BASE}/api/stocks/${symbol}/prediction`)
  if (!res.ok) throw new Error('Failed to fetch prediction')
  return res.json()
}

export async function fetchStockHistory(symbol: string, period = '1y') {
  const res = await fetch(`${API_BASE}/api/stocks/${symbol}/history?period=${period}`)
  if (!res.ok) throw new Error('Failed to fetch history')
  return res.json()
}

export async function fetchMarketOverview() {
  const res = await fetch(`${API_BASE}/api/predictions/market-overview`)
  if (!res.ok) throw new Error('Failed to fetch market overview')
  return res.json()
}

export async function fetchPopularStocks() {
  const res = await fetch(`${API_BASE}/api/stocks`)
  if (!res.ok) throw new Error('Failed to fetch stocks')
  return res.json()
}

// Protected endpoints (auth required)
export async function fetchPortfolio() {
  const res = await fetch(`${API_BASE}/api/paper-trading/portfolio`, {
    headers: getHeaders()
  })
  return handleResponse(res)
}

export async function fetchTrades(status: string = 'all') {
  const res = await fetch(`${API_BASE}/api/paper-trading/trades?status=${status}`, {
    headers: getHeaders()
  })
  return handleResponse(res)
}

export async function createTrade(
  symbol: string, 
  assetType: string, 
  direction: 'long' | 'short', 
  quantity: number,
  thesis?: string
) {
  const res = await fetch(`${API_BASE}/api/paper-trading/trade`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ 
      symbol, 
      asset_type: assetType, 
      direction, 
      quantity,
      thesis 
    }),
  })
  return handleResponse(res)
}

export async function exitTrade(
  tradeId: number, 
  exitPrice?: number, 
  exitReason?: string, 
  lessons?: string
) {
  const res = await fetch(`${API_BASE}/api/paper-trading/trade/${tradeId}/exit`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ 
      exit_price: exitPrice, 
      exit_reason: exitReason, 
      lessons 
    }),
  })
  return handleResponse(res)
}

export async function fetchWatchlist() {
  const res = await fetch(`${API_BASE}/api/watchlist`, {
    headers: getHeaders()
  })
  return handleResponse(res)
}

export async function addToWatchlist(symbol: string, assetType: string = 'stock', alertThreshold?: number) {
  const res = await fetch(`${API_BASE}/api/watchlist`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ 
      symbol, 
      asset_type: assetType,
      alert_threshold: alertThreshold 
    }),
  })
  return handleResponse(res)
}

export async function removeFromWatchlist(symbol: string) {
  const res = await fetch(`${API_BASE}/api/watchlist/${symbol}`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  return handleResponse(res)
}

// User profile
export async function updateProfile(name?: string, avatarUrl?: string) {
  const params = new URLSearchParams()
  if (name) params.append('name', name)
  if (avatarUrl) params.append('avatar_url', avatarUrl)
  
  const res = await fetch(`${API_BASE}/api/auth/me?${params.toString()}`, {
    method: 'PUT',
    headers: getHeaders()
  })
  return handleResponse(res)
}

export async function changePassword(currentPassword: string, newPassword: string) {
  const params = new URLSearchParams()
  params.append('current_password', currentPassword)
  params.append('new_password', newPassword)
  
  const res = await fetch(`${API_BASE}/api/auth/change-password?${params.toString()}`, {
    method: 'POST',
    headers: getHeaders()
  })
  return handleResponse(res)
}
