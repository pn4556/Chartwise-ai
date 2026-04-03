'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import { Wallet, TrendingUp, TrendingDown, DollarSign, Plus, X, Loader2, Wifi, WifiOff } from 'lucide-react'
import { fetchPortfolio, fetchTrades, createTrade, exitTrade } from '@/lib/api'
import { useWatchlistUpdates, usePortfolioUpdates } from '@/lib/websocket'

interface Trade {
  id: string
  symbol: string
  direction: 'long' | 'short'
  entry_price: number
  current_price?: number
  shares: number
  current_pnl: number
  current_pnl_percent: number
  status: string
  entry_date?: string
}

interface Portfolio {
  cash_balance: number
  total_value: number
  open_positions: number
  total_pnl: number
  win_rate: number
}

export default function PaperTrading() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [creatingTrade, setCreatingTrade] = useState(false)
  const [closingTradeId, setClosingTradeId] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // New trade form state
  const [newTrade, setNewTrade] = useState({
    symbol: '',
    type: 'long' as 'long' | 'short',
    shares: 1,
  })
  
  // Get symbols from open trades for WebSocket subscription
  const tradeSymbols = trades.map(t => t.symbol)
  
  // WebSocket hooks for real-time updates
  const { updates: priceUpdates, isConnected: wsConnected, lastUpdate: wsLastUpdate } = useWatchlistUpdates(tradeSymbols)
  const { predictionsRefreshed } = usePortfolioUpdates()

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [portfolioData, tradesData] = await Promise.all([
        fetchPortfolio(),
        fetchTrades(),
      ])
      setPortfolio(portfolioData)
      setTrades(tradesData.filter((t: Trade) => t.status === 'open'))
      setLastRefresh(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])
  
  // Refresh when predictions are updated via WebSocket
  useEffect(() => {
    if (predictionsRefreshed) {
      console.log('Predictions refreshed via WebSocket, reloading data...')
      loadData()
    }
  }, [predictionsRefreshed])
  
  // Update trades with real-time price updates
  useEffect(() => {
    if (Object.keys(priceUpdates).length > 0) {
      setTrades(prevTrades => 
        prevTrades.map(trade => {
          const update = priceUpdates[trade.symbol]
          if (update && update.current_price) {
            const currentPrice = update.current_price
            const priceDiff = trade.direction === 'long' 
              ? currentPrice - trade.entry_price 
              : trade.entry_price - currentPrice
            const currentPnl = priceDiff * trade.shares
            const currentPnlPercent = (priceDiff / trade.entry_price) * 100
            
            return {
              ...trade,
              current_price: currentPrice,
              current_pnl: currentPnl,
              current_pnl_percent: currentPnlPercent
            }
          }
          return trade
        })
      )
    }
  }, [priceUpdates])

  const handleCreateTrade = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTrade.symbol || newTrade.shares < 1) return

    try {
      setCreatingTrade(true)
      await createTrade(newTrade.symbol.toUpperCase(), 'stock', newTrade.type, newTrade.shares)
      setIsModalOpen(false)
      setNewTrade({ symbol: '', type: 'long', shares: 1 })
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create trade')
    } finally {
      setCreatingTrade(false)
    }
  }

  const handleCloseTrade = async (tradeId: string) => {
    try {
      setClosingTradeId(tradeId)
      await exitTrade(parseInt(tradeId))
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to close trade')
    } finally {
      setClosingTradeId(null)
    }
  }

  const activeTrades = trades.filter(t => t.status === 'open')

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Wallet className="w-8 h-8 text-primary-400" />
              Paper Trading
            </h1>
            <p className="text-slate-400 mt-1">Practice trading with virtual money</p>
          </div>
          <div className="flex items-center gap-4">
            {/* WebSocket Status */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg">
              {wsConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-success-400" />
                  <span className="text-sm text-success-400">Live Updates</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-slate-500" />
                  <span className="text-sm text-slate-500">Offline</span>
                </>
              )}
            </div>
            {/* Last Update Time */}
            <div className="text-xs text-slate-500">
              Last refresh: {lastRefresh.toLocaleTimeString()}
              {wsLastUpdate && (
                <span className="ml-2 text-success-400">
                  (Live: {wsLastUpdate.toLocaleTimeString()})
                </span>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-danger-500/20 border border-danger-500/50 rounded-lg text-danger-400">
            {error}
            <button 
              onClick={() => setError(null)}
              className="ml-2 text-sm underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Portfolio Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Available Cash</p>
            <p className="text-2xl font-bold text-white">
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                `$${portfolio?.cash_balance.toLocaleString() || '0'}`
              )}
            </p>
          </div>
          
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Total Value</p>
            <p className="text-2xl font-bold text-white">
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                `$${portfolio?.total_value.toLocaleString() || '0'}`
              )}
            </p>
          </div>
          
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Open Positions</p>
            <p className="text-2xl font-bold text-white">
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                portfolio?.open_positions || 0
              )}
            </p>
          </div>
          
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Total P&L</p>
            <p className={`text-2xl font-bold ${
              (portfolio?.total_pnl || 0) >= 0 ? 'text-success-400' : 'text-danger-400'
            }`}>
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  {(portfolio?.total_pnl || 0) >= 0 ? '+' : ''}
                  ${portfolio?.total_pnl.toFixed(2) || '0.00'}
                </>
              )}
            </p>
          </div>
        </div>

        {/* Active Trades */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Active Positions</h2>
            <button 
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Trade
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <Loader2 className="w-12 h-12 text-slate-600 mx-auto mb-4 animate-spin" />
              <p className="text-slate-400">Loading positions...</p>
            </div>
          ) : activeTrades.length === 0 ? (
            <div className="text-center py-12">
              <DollarSign className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No active positions</p>
              <p className="text-slate-500 text-sm mt-1">Start trading to see your positions here</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700 text-left">
                  <th className="px-6 py-3 text-slate-400 font-medium">Symbol</th>
                  <th className="px-6 py-3 text-slate-400 font-medium">Type</th>
                  <th className="px-6 py-3 text-slate-400 font-medium">Entry</th>
                  <th className="px-6 py-3 text-slate-400 font-medium">Current</th>
                  <th className="px-6 py-3 text-slate-400 font-medium">Shares</th>
                  <th className="px-6 py-3 text-slate-400 font-medium">P&L</th>
                  <th className="px-6 py-3 text-slate-400 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {activeTrades.map((trade) => (
                  <tr key={trade.id} className="border-b border-slate-700/50 hover:bg-slate-800/50">
                    <td className="px-6 py-4">
                      <span className="font-semibold text-white">{trade.symbol}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        trade.direction === 'long' 
                          ? 'bg-success-500/20 text-success-400' 
                          : 'bg-danger-500/20 text-danger-400'
                      }`}>
                        {trade.direction === 'long' ? (
                          <span className="flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" /> LONG
                          </span>
                        ) : (
                          <span className="flex items-center gap-1">
                            <TrendingDown className="w-3 h-3" /> SHORT
                          </span>
                        )}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      ${trade.entry_price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-white">
                      ${trade.current_price?.toFixed(2) || trade.entry_price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      {trade.shares}
                    </td>
                    <td className="px-6 py-4">
                      <div className={trade.current_pnl >= 0 ? 'text-success-400' : 'text-danger-400'}>
                        <span className="font-semibold">
                          {trade.current_pnl >= 0 ? '+' : ''}${trade.current_pnl.toFixed(2)}
                        </span>
                        <span className="text-sm ml-1">
                          ({trade.current_pnl_percent >= 0 ? '+' : ''}{trade.current_pnl_percent.toFixed(2)}%)
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button 
                        onClick={() => handleCloseTrade(trade.id)}
                        disabled={closingTradeId === trade.id}
                        className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                      >
                        {closingTradeId === trade.id ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            Closing...
                          </>
                        ) : (
                          'Close'
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Trading Tips */}
        <div className="mt-8 bg-gradient-to-r from-primary-900/20 to-purple-900/20 border border-primary-800/30 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-2">💡 Paper Trading Tips</h3>
          <ul className="text-slate-400 text-sm space-y-1">
            <li>• Start with small positions to test your strategy</li>
            <li>• Use stop-losses to manage risk</li>
            <li>• Keep a trading journal to track what works</li>
            <li>• Don&apos;t risk more than 2% of your portfolio on a single trade</li>
          </ul>
        </div>
      </main>

      {/* New Trade Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">New Trade</h3>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTrade} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">
                  Symbol
                </label>
                <input
                  type="text"
                  value={newTrade.symbol}
                  onChange={(e) => setNewTrade({ ...newTrade, symbol: e.target.value.toUpperCase() })}
                  placeholder="e.g. AAPL"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">
                  Trade Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setNewTrade({ ...newTrade, type: 'long' })}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      newTrade.type === 'long'
                        ? 'bg-success-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    <span className="flex items-center justify-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      Long
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setNewTrade({ ...newTrade, type: 'short' })}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      newTrade.type === 'short'
                        ? 'bg-danger-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    <span className="flex items-center justify-center gap-1">
                      <TrendingDown className="w-4 h-4" />
                      Short
                    </span>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">
                  Number of Shares
                </label>
                <input
                  type="number"
                  min="1"
                  value={newTrade.shares}
                  onChange={(e) => setNewTrade({ ...newTrade, shares: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  required
                />
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingTrade || !newTrade.symbol}
                  className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {creatingTrade ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Trade'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
