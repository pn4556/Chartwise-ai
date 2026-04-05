/**
 * WebSocket client for real-time updates
 */

import { useEffect, useRef, useState, useCallback } from 'react'

const WS_URL = 'wss://chartwise-ai.onrender.com/ws'

export interface WebSocketMessage {
  type: string
  symbol?: string
  data?: any
  timestamp?: string
  [key: string]: any
}

interface UseWebSocketOptions {
  onMessage?: (data: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const subscriptionsRef = useRef<Set<string>>(new Set())
  const isManualDisconnectRef = useRef(false)

  const connect = useCallback(() => {
    try {
      // Don't connect if max attempts reached
      const maxAttempts = options.maxReconnectAttempts || 10
      if (reconnectAttempts >= maxAttempts) {
        console.warn(`Max reconnection attempts (${maxAttempts}) reached`)
        return
      }

      const ws = new WebSocket(WS_URL)
      
      ws.onopen = () => {
        console.log('🔌 WebSocket connected')
        setIsConnected(true)
        setReconnectAttempts(0)
        isManualDisconnectRef.current = false
        
        // Resubscribe to previous symbols after reconnection
        subscriptionsRef.current.forEach(symbol => {
          ws.send(JSON.stringify({ action: 'subscribe', symbol }))
        })
        
        options.onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          options.onMessage?.(data)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected', event.code, event.reason)
        setIsConnected(false)
        options.onDisconnect?.()
        
        // Auto reconnect if not manually disconnected and not a normal close
        if (!isManualDisconnectRef.current && options.autoReconnect !== false) {
          const interval = options.reconnectInterval || 5000
          setReconnectAttempts(prev => prev + 1)
          reconnectTimeoutRef.current = setTimeout(connect, interval)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      wsRef.current = ws
    } catch (err) {
      console.error('Failed to connect WebSocket:', err)
    }
  }, [options, reconnectAttempts])

  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    wsRef.current?.close()
  }, [])

  const send = useCallback((message: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, message queued:', message)
    }
  }, [])

  const subscribe = useCallback((symbol: string) => {
    const upperSymbol = symbol.toUpperCase()
    subscriptionsRef.current.add(upperSymbol)
    send({ action: 'subscribe', symbol: upperSymbol })
  }, [send])

  const subscribeMultiple = useCallback((symbols: string[]) => {
    const upperSymbols = symbols.map(s => s.toUpperCase())
    upperSymbols.forEach(s => subscriptionsRef.current.add(s))
    send({ action: 'subscribe_multiple', symbols: upperSymbols })
  }, [send])

  const unsubscribe = useCallback((symbol: string) => {
    const upperSymbol = symbol.toUpperCase()
    subscriptionsRef.current.delete(upperSymbol)
    send({ action: 'unsubscribe', symbol: upperSymbol })
  }, [send])

  const unsubscribeAll = useCallback(() => {
    subscriptionsRef.current.clear()
    send({ action: 'unsubscribe_all' })
  }, [send])

  const ping = useCallback(() => {
    send({ action: 'ping' })
  }, [send])

  const getSubscriptions = useCallback(() => {
    send({ action: 'get_subscriptions' })
  }, [send])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    reconnectAttempts,
    subscriptions: Array.from(subscriptionsRef.current),
    send,
    subscribe,
    subscribeMultiple,
    unsubscribe,
    unsubscribeAll,
    ping,
    getSubscriptions,
    connect,
    disconnect
  }
}

// Hook for subscribing to specific symbol updates
export function useSymbolUpdates(symbol: string | null) {
  const [predictionData, setPredictionData] = useState<any>(null)
  const [priceData, setPriceData] = useState<any>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  
  const { subscribe, unsubscribe, isConnected, lastMessage } = useWebSocket({
    onMessage: (message) => {
      if (message.symbol === symbol) {
        setLastUpdate(new Date())
        if (message.type === 'prediction_update') {
          setPredictionData(message.data)
        } else if (message.type === 'price_update') {
          setPriceData(message.data)
        }
      }
    }
  })

  useEffect(() => {
    if (isConnected && symbol) {
      subscribe(symbol)
      return () => {
        if (symbol) unsubscribe(symbol)
      }
    }
  }, [isConnected, symbol, subscribe, unsubscribe])

  return { 
    predictionData, 
    priceData, 
    lastMessage,
    lastUpdate,
    isConnected 
  }
}

// Hook for watching multiple symbols (useful for watchlist)
export function useWatchlistUpdates(symbols: string[]) {
  const [updates, setUpdates] = useState<Record<string, any>>({})
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  
  const { subscribeMultiple, unsubscribeAll, isConnected, lastMessage } = useWebSocket({
    onMessage: (message) => {
      if (message.symbol && symbols.includes(message.symbol)) {
        setLastUpdate(new Date())
        setUpdates(prev => ({
          ...prev,
          [message.symbol!]: message.data || message
        }))
      }
    }
  })

  useEffect(() => {
    if (isConnected && symbols.length > 0) {
      subscribeMultiple(symbols)
      return () => unsubscribeAll()
    }
  }, [isConnected, symbols.join(','), subscribeMultiple, unsubscribeAll])

  return { updates, lastUpdate, lastMessage, isConnected }
}

// Hook for portfolio updates (for paper trading)
export function usePortfolioUpdates() {
  const [portfolioData, setPortfolioData] = useState<any>(null)
  const [predictionsRefreshed, setPredictionsRefreshed] = useState(false)
  
  const { isConnected, lastMessage } = useWebSocket({
    onMessage: (message) => {
      if (message.type === 'portfolio_update') {
        setPortfolioData(message.data)
      } else if (message.type === 'predictions_refreshed') {
        setPredictionsRefreshed(true)
        // Reset after a short delay
        setTimeout(() => setPredictionsRefreshed(false), 5000)
      }
    }
  })

  return { portfolioData, predictionsRefreshed, isConnected, lastMessage }
}
