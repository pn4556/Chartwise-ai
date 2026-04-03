'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Header from '@/components/Header'
import ScoreBadge from '@/components/ScoreBadge'
import { fetchStockPrediction, fetchStockHistory, createTrade, addToWatchlist } from '@/lib/api'
import { formatPrice, formatPercentage, getRecommendationColor } from '@/lib/utils'
import { ArrowLeft, TrendingUp, TrendingDown, Activity, BarChart3, Clock, Star, Plus, X, Loader2, CheckCircle, Wifi, WifiOff } from 'lucide-react'
import Link from 'next/link'
import StockChart from '@/components/StockChart'
import { useSymbolUpdates } from '@/lib/websocket'

interface Prediction {
  symbol: string
  name?: string
  bullish_score: number
  confidence: number
  recommendation: string
  signals: Record<string, string>
  technical_score: number
  trend_score: number
  volume_score: number
  rsi: number
  macd?: number
  macd_signal?: number
}

interface HistoryPoint {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface KeySignal {
  name: string
  value: string
  isBullish: boolean
  isBearish: boolean
}

export default function StockDetail() {
  const params = useParams()
  const symbol = params.symbol as string

  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [history, setHistory] = useState<HistoryPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [livePrice, setLivePrice] = useState<number | null>(null)

  // Modal states
  const [tradeModalOpen, setTradeModalOpen] = useState(false)
  const [tradeType, setTradeType] = useState<'long' | 'short'>('long')
  const [shares, setShares] = useState(1)
  const [creatingTrade, setCreatingTrade] = useState(false)

  const [watchlistModalOpen, setWatchlistModalOpen] = useState(false)
  const [addingToWatchlist, setAddingToWatchlist] = useState(false)
  
  // WebSocket for real-time updates
  const { predictionData, priceData, isConnected, lastUpdate } = useSymbolUpdates(symbol)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        setError(null)
        const [predData, histData] = await Promise.all([
          fetchStockPrediction(symbol),
          fetchStockHistory(symbol, '1y')
        ])
        setPrediction(predData)
        setHistory(histData)
        if (histData.length > 0) {
          setLivePrice(histData[histData.length - 1].close)
        }
      } catch (err) {
        console.error('Failed to load stock data:', err)
        setError('Failed to load stock data. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [symbol])
  
  // Handle real-time prediction updates
  useEffect(() => {
    if (predictionData) {
      setPrediction(prev => ({
        ...prev,
        ...predictionData,
        symbol: symbol
      } as Prediction))
    }
  }, [predictionData, symbol])
  
  // Handle real-time price updates
  useEffect(() => {
    if (priceData) {
      const newPrice = priceData.current_price || priceData.price
      if (newPrice) {
        setLivePrice(newPrice)
      }
    }
  }, [priceData])

  const handleCreateTrade = async (e: React.FormEvent) => {
    e.preventDefault()
    if (shares < 1) return

    try {
      setCreatingTrade(true)
      setError(null)
      await createTrade(symbol.toUpperCase(), 'stock', tradeType, shares)
      setSuccessMessage(`Successfully created ${tradeType} position for ${shares} shares of ${symbol}`)
      setTradeModalOpen(false)
      setShares(1)
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create trade')
    } finally {
      setCreatingTrade(false)
    }
  }

  const handleAddToWatchlist = async () => {
    try {
      setAddingToWatchlist(true)
      setError(null)
      await addToWatchlist(symbol.toUpperCase(), 'stock')
      setSuccessMessage(`${symbol} added to your watchlist`)
      setWatchlistModalOpen(false)
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add to watchlist')
    } finally {
      setAddingToWatchlist(false)
    }
  }

  const openTradeModal = (type: 'long' | 'short') => {
    setTradeType(type)
    setTradeModalOpen(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950">
        <Header />
        <div className="animate-pulse max-w-7xl mx-auto px-4 py-8">
          <div className="h-32 bg-slate-800 rounded-xl mb-6" />
          <div className="h-96 bg-slate-800 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!prediction && !loading) {
    return (
      <div className="min-h-screen bg-slate-950">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8 text-center">
          <p className="text-danger-400">Failed to load stock data</p>
          <Link href="/" className="text-primary-400 hover:underline mt-4 inline-block">
            Go back
          </Link>
        </div>
      </div>
    )
  }

  const currentPrice = livePrice || (history.length > 0 ? history[history.length - 1].close : 0)
  const priceChange = history.length > 1 && currentPrice
    ? currentPrice - history[history.length - 2].close
    : 0
  const priceChangePercent = history.length > 1 && currentPrice
    ? (priceChange / history[history.length - 2].close) * 100
    : 0

  const high24h = history.length > 0 ? Math.max(...history.slice(-30).map(h => h.high)) : 0
  const low24h = history.length > 0 ? Math.min(...history.slice(-30).map(h => h.low)) : 0
  const avgVolume = history.length > 0
    ? history.slice(-30).reduce((acc, h) => acc + h.volume, 0) / 30
    : 0

  // Parse key signals from prediction
  const keySignals: KeySignal[] = prediction
    ? Object.entries(prediction.signals).map(([key, value]) => ({
        name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: value.replace(/_/g, ' '),
        isBullish: value.toLowerCase().includes('bullish'),
        isBearish: value.toLowerCase().includes('bearish')
      }))
    : []

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success/Error Messages */}
        {successMessage && (
          <div className="mb-6 p-4 bg-success-500/20 border border-success-500/50 rounded-lg flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
            <CheckCircle className="w-5 h-5 text-success-400" />
            <span className="text-success-400">{successMessage}</span>
            <button
              onClick={() => setSuccessMessage(null)}
              className="ml-auto text-success-400 hover:text-success-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-danger-500/20 border border-danger-500/50 rounded-lg flex items-center gap-2">
            <span className="text-danger-400">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-danger-400 hover:text-danger-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>

        {/* Stock Header */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-4xl font-bold text-white">{symbol}</h1>
                {prediction?.name && (
                  <span className="text-xl text-slate-400">{prediction.name}</span>
                )}
                {/* WebSocket Status */}
                {isConnected ? (
                  <span className="flex items-center gap-1 px-2 py-1 bg-success-500/20 rounded text-xs text-success-400">
                    <Wifi className="w-3 h-3" />
                    Live
                  </span>
                ) : (
                  <span className="flex items-center gap-1 px-2 py-1 bg-slate-700 rounded text-xs text-slate-500">
                    <WifiOff className="w-3 h-3" />
                    Offline
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 mt-2">
                <span className="text-2xl font-semibold text-white">
                  {formatPrice(currentPrice)}
                </span>
                <span className={`text-lg font-medium ${priceChange >= 0 ? 'text-success-400' : 'text-danger-400'}`}>
                  {priceChange >= 0 ? '+' : ''}{formatPrice(priceChange)}
                  {' '}({formatPercentage(priceChangePercent)})
                </span>
                {priceChange >= 0 ? (
                  <TrendingUp className="w-5 h-5 text-success-400" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-danger-400" />
                )}
                {lastUpdate && (
                  <span className="text-xs text-slate-500 ml-2">
                    Updated {lastUpdate.toLocaleTimeString()}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-center">
                <ScoreBadge score={prediction?.bullish_score || 0} confidence={prediction?.confidence} size="lg" />
                <p className="text-xs text-slate-500 mt-1">Bullish Score</p>
              </div>

              <div className="text-right">
                <p className={`text-2xl font-bold ${getRecommendationColor(prediction?.recommendation || 'Hold')}`}>
                  {prediction?.recommendation}
                </p>
                <p className="text-sm text-slate-500">AI Recommendation</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Chart */}
          <div className="lg:col-span-2 space-y-6">
            {/* Price Chart */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary-400" />
                  Price Chart
                </h2>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <span>Vol: {(avgVolume / 1000000).toFixed(1)}M avg</span>
                </div>
              </div>
              <StockChart data={history} symbol={symbol} />
            </div>

            {/* Price Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-slate-400 text-sm mb-1">Day High</p>
                <p className="text-xl font-semibold text-success-400">{formatPrice(high24h)}</p>
              </div>
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-slate-400 text-sm mb-1">Day Low</p>
                <p className="text-xl font-semibold text-danger-400">{formatPrice(low24h)}</p>
              </div>
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-slate-400 text-sm mb-1">Volume</p>
                <p className="text-xl font-semibold text-white">{(avgVolume / 1000000).toFixed(1)}M</p>
              </div>
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-slate-400 text-sm mb-1">Confidence</p>
                <p className="text-xl font-semibold text-primary-400">{prediction?.confidence}%</p>
              </div>
            </div>

            {/* Price History Table */}
            {history.length > 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-bold text-white mb-4">Recent Price History</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-slate-400 border-b border-slate-700">
                        <th className="text-left py-2">Date</th>
                        <th className="text-right py-2">Open</th>
                        <th className="text-right py-2">High</th>
                        <th className="text-right py-2">Low</th>
                        <th className="text-right py-2">Close</th>
                        <th className="text-right py-2">Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.slice(-5).reverse().map((point, idx) => (
                        <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30">
                          <td className="py-2 text-slate-300">
                            {new Date(point.date).toLocaleDateString()}
                          </td>
                          <td className="text-right py-2 text-slate-300">
                            {formatPrice(point.open)}
                          </td>
                          <td className="text-right py-2 text-success-400">
                            {formatPrice(point.high)}
                          </td>
                          <td className="text-right py-2 text-danger-400">
                            {formatPrice(point.low)}
                          </td>
                          <td className="text-right py-2 text-white font-medium">
                            {formatPrice(point.close)}
                          </td>
                          <td className="text-right py-2 text-slate-400">
                            {(point.volume / 1000000).toFixed(1)}M
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Analysis */}
          <div className="space-y-6">
            {/* AI Prediction Panel */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary-400" />
                AI Analysis
              </h2>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-slate-400">Bullish Score</span>
                  <span className={`font-bold ${(prediction?.bullish_score || 0) >= 50 ? 'text-success-400' : 'text-danger-400'}`}>
                    {prediction?.bullish_score.toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-slate-400">Confidence</span>
                  <span className="font-bold text-primary-400">{prediction?.confidence}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-slate-400">Recommendation</span>
                  <span className={`font-bold ${getRecommendationColor(prediction?.recommendation || 'Hold')}`}>
                    {prediction?.recommendation}
                  </span>
                </div>
              </div>
            </div>

            {/* Technical Indicators */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary-400" />
                Technical Indicators
              </h2>

              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-slate-400">RSI (14)</span>
                  <span className={`font-medium ${(prediction?.rsi || 50) > 70 ? 'text-danger-400' : (prediction?.rsi || 50) < 30 ? 'text-success-400' : 'text-white'}`}>
                    {(prediction?.rsi || 0).toFixed(1)}
                    {(prediction?.rsi || 50) > 70 && ' (Overbought)'}
                    {(prediction?.rsi || 50) < 30 && ' (Oversold)'}
                  </span>
                </div>

                {prediction?.macd !== undefined && (
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <span className="text-slate-400">MACD</span>
                    <span className={`font-medium ${(prediction.macd || 0) > 0 ? 'text-success-400' : 'text-danger-400'}`}>
                      {prediction.macd > 0 ? '+' : ''}{prediction.macd.toFixed(2)}
                    </span>
                  </div>
                )}

                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-slate-400">Technical Score</span>
                  <span className="font-medium text-white">{(prediction?.technical_score || 0).toFixed(1)}%</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-slate-400">Trend Score</span>
                  <span className="font-medium text-white">{(prediction?.trend_score || 0).toFixed(1)}%</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-slate-400">Volume Score</span>
                  <span className="font-medium text-white">{(prediction?.volume_score || 0).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Signal Breakdown */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold text-white mb-4">Key Signals</h2>

              <div className="space-y-2">
                {keySignals.map((signal, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                    <span className="text-slate-400 text-sm">{signal.name}</span>
                    <div className="flex items-center gap-2">
                      {signal.isBullish ? (
                        <TrendingUp className="w-4 h-4 text-success-400" />
                      ) : signal.isBearish ? (
                        <TrendingDown className="w-4 h-4 text-danger-400" />
                      ) : (
                        <Activity className="w-4 h-4 text-yellow-400" />
                      )}
                      <span className={`text-sm font-medium ${
                        signal.isBullish ? 'text-success-400' :
                        signal.isBearish ? 'text-danger-400' : 'text-yellow-400'
                      }`}>
                        {signal.value.charAt(0).toUpperCase() + signal.value.slice(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold text-white mb-4">Actions</h2>

              <div className="space-y-3">
                <button
                  onClick={() => setWatchlistModalOpen(true)}
                  className="w-full py-3 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Star className="w-4 h-4" />
                  Add to Watchlist
                </button>
                <button
                  onClick={() => openTradeModal('long')}
                  className="w-full py-3 bg-success-600/20 hover:bg-success-600/30 text-success-400 border border-success-600/50 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <TrendingUp className="w-4 h-4" />
                  Paper Trade (Long)
                </button>
                <button
                  onClick={() => openTradeModal('short')}
                  className="w-full py-3 bg-danger-600/20 hover:bg-danger-600/30 text-danger-400 border border-danger-600/50 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <TrendingDown className="w-4 h-4" />
                  Paper Trade (Short)
                </button>
              </div>
            </div>

            {/* Last Updated */}
            <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
              <Clock className="w-4 h-4" />
              <span>Last updated: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </main>

      {/* Trade Modal */}
      {tradeModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                {tradeType === 'long' ? (
                  <TrendingUp className="w-5 h-5 text-success-400" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-danger-400" />
                )}
                Paper Trade {tradeType === 'long' ? 'Long' : 'Short'}: {symbol}
              </h3>
              <button
                onClick={() => setTradeModalOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6 p-4 bg-slate-900/50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-slate-400">Current Price</span>
                <span className="text-white font-semibold">{formatPrice(currentPrice)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Total Cost (Est.)</span>
                <span className="text-white font-semibold">{formatPrice(currentPrice * shares)}</span>
              </div>
            </div>

            <form onSubmit={handleCreateTrade} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Number of Shares
                </label>
                <input
                  type="number"
                  min="1"
                  max="10000"
                  value={shares}
                  onChange={(e) => setShares(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  required
                />
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setTradeModalOpen(false)}
                  className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingTrade}
                  className={`flex-1 px-4 py-2 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                    tradeType === 'long'
                      ? 'bg-success-600 hover:bg-success-500'
                      : 'bg-danger-600 hover:bg-danger-500'
                  }`}
                >
                  {creatingTrade ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>Create {tradeType === 'long' ? 'Long' : 'Short'} Position</>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Watchlist Modal */}
      {watchlistModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Star className="w-5 h-5 text-primary-400" />
                Add to Watchlist
              </h3>
              <button
                onClick={() => setWatchlistModalOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6 text-center">
              <div className="w-16 h-16 bg-primary-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="w-8 h-8 text-primary-400" />
              </div>
              <p className="text-white text-lg font-semibold mb-1">{symbol}</p>
              <p className="text-slate-400">Add this stock to your watchlist to track it easily.</p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setWatchlistModalOpen(false)}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddToWatchlist}
                disabled={addingToWatchlist}
                className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              >
                {addingToWatchlist ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Add to Watchlist
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
