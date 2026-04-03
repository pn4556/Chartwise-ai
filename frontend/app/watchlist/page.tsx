'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import { Search, Plus, Trash2, Star, Loader2, Wifi, WifiOff } from 'lucide-react'
import Link from 'next/link'
import { fetchWatchlist, addToWatchlist, removeFromWatchlist } from '@/lib/api'
import { useWatchlistUpdates } from '@/lib/websocket'

interface WatchlistItem {
  id: number
  symbol: string
  asset_type: string
  current_price: number
  bullish_score: number
  recommendation: string
  added_date: string
}

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newSymbol, setNewSymbol] = useState('')
  const [adding, setAdding] = useState(false)
  const [removingSymbol, setRemovingSymbol] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())
  
  // Get symbols for WebSocket subscription
  const symbols = watchlist.map(item => item.symbol)
  
  // WebSocket for real-time updates
  const { updates: priceUpdates, isConnected: wsConnected, lastUpdate: wsLastUpdate } = useWatchlistUpdates(symbols)

  useEffect(() => {
    loadWatchlist()
  }, [])
  
  // Apply real-time price updates to watchlist
  useEffect(() => {
    if (Object.keys(priceUpdates).length > 0) {
      setWatchlist(prevWatchlist => 
        prevWatchlist.map(item => {
          const update = priceUpdates[item.symbol]
          if (update) {
            return {
              ...item,
              current_price: update.current_price || item.current_price,
              bullish_score: update.bullish_score || item.bullish_score,
              recommendation: update.recommendation || item.recommendation
            }
          }
          return item
        })
      )
    }
  }, [priceUpdates])

  const loadWatchlist = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchWatchlist()
      setWatchlist(data)
      setLastRefresh(new Date())
    } catch (err) {
      setError('Failed to load watchlist. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const addStock = async () => {
    if (!newSymbol) return
    const symbol = newSymbol.toUpperCase()
    if (watchlist.find(s => s.symbol === symbol)) {
      setNewSymbol('')
      return
    }

    try {
      setAdding(true)
      await addToWatchlist(symbol)
      await loadWatchlist()
      setNewSymbol('')
    } catch (err) {
      setError('Failed to add stock. Please try again.')
      console.error(err)
    } finally {
      setAdding(false)
    }
  }

  const removeStock = async (symbol: string) => {
    try {
      setRemovingSymbol(symbol)
      await removeFromWatchlist(symbol)
      setWatchlist(watchlist.filter(s => s.symbol !== symbol))
    } catch (err) {
      setError('Failed to remove stock. Please try again.')
      console.error(err)
    } finally {
      setRemovingSymbol(null)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 60) return 'bg-success-400'
    if (score >= 40) return 'bg-yellow-400'
    return 'bg-danger-400'
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Star className="w-8 h-8 text-yellow-400" />
              My Watchlist
            </h1>
            <p className="text-slate-400 mt-1">Track your favorite stocks and cryptocurrencies</p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* WebSocket Status */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg">
              {wsConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-success-400" />
                  <span className="text-sm text-success-400">Live</span>
                  {wsLastUpdate && (
                    <span className="text-xs text-slate-500 ml-1">
                      {wsLastUpdate.toLocaleTimeString()}
                    </span>
                  )}
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-slate-500" />
                  <span className="text-sm text-slate-500">Offline</span>
                </>
              )}
            </div>
            
            <div className="text-xs text-slate-500">
              Updated: {lastRefresh.toLocaleTimeString()}
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div></div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Add symbol (e.g., AAPL)"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addStock()}
              disabled={adding}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 disabled:opacity-50"
            />
            <button
              onClick={addStock}
              disabled={adding || !newSymbol}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:bg-slate-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2 disabled:cursor-not-allowed"
            >
              {adding ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              Add
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-danger-500/10 border border-danger-500/30 rounded-lg text-danger-400">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
            <p className="text-slate-400">Loading watchlist...</p>
          </div>
        ) : watchlist.length === 0 ? (
          <div className="text-center py-16 bg-slate-800/50 rounded-xl border border-slate-700">
            <Star className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Your watchlist is empty</h3>
            <p className="text-slate-400">Add stocks or crypto to track them here</p>
          </div>
        ) : (
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700 text-left">
                  <th className="px-6 py-4 text-slate-400 font-medium">Symbol</th>
                  <th className="px-6 py-4 text-slate-400 font-medium">Type</th>
                  <th className="px-6 py-4 text-slate-400 font-medium">Price</th>
                  <th className="px-6 py-4 text-slate-400 font-medium">AI Score</th>
                  <th className="px-6 py-4 text-slate-400 font-medium">Recommendation</th>
                  <th className="px-6 py-4 text-slate-400 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {watchlist.map((item) => (
                  <tr key={item.id} className="border-b border-slate-700/50 hover:bg-slate-800/50">
                    <td className="px-6 py-4">
                      <Link href={`/stock/${item.symbol}`} className="block">
                        <span className="text-lg font-semibold text-white">{item.symbol}</span>
                        <p className="text-sm text-slate-500">Added {new Date(item.added_date).toLocaleDateString()}</p>
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-700 text-slate-300 capitalize">
                        {item.asset_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-white">${item.current_price?.toFixed(2) || '—'}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getScoreColor(item.bullish_score)}`}
                            style={{ width: `${item.bullish_score}%` }}
                          />
                        </div>
                        <span className="text-white text-sm">{item.bullish_score}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                        item.recommendation === 'buy' ? 'bg-success-500/20 text-success-400' :
                        item.recommendation === 'sell' ? 'bg-danger-500/20 text-danger-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {item.recommendation}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => removeStock(item.symbol)}
                        disabled={removingSymbol === item.symbol}
                        className="p-2 text-slate-400 hover:text-danger-400 transition-colors disabled:opacity-50"
                      >
                        {removingSymbol === item.symbol ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <Trash2 className="w-5 h-5" />
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}
