'use client'

import { useEffect, useState } from 'react'
import { ArrowLeft, TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react'
import Link from 'next/link'
import ScoreBadge from './ScoreBadge'

interface SectorStock {
  symbol: string
  bullish_score: number
  confidence: number
  recommendation: string
  current_price: number
  change_percent: number
  signals: Record<string, string>
}

interface SectorData {
  sector: string
  total_stocks: number
  analyzed: number
  statistics: {
    average_score: number
    average_confidence: number
    bullish_count: number
    bearish_count: number
    neutral_count: number
  }
  top_performer: SectorStock | null
  stocks: SectorStock[]
}

interface SectorStocksProps {
  sector: string | null
  onBack: () => void
}

const SECTOR_NAMES: Record<string, string> = {
  'Tech': 'Technology',
  'Finance': 'Finance',
  'Healthcare': 'Healthcare',
  'Energy': 'Energy',
  'Consumer': 'Consumer',
  'Industrial': 'Industrial',
  'CommServices': 'Communication Services',
  'RealEstate': 'Real Estate',
  'Materials': 'Materials',
  'Utilities': 'Utilities',
  'AI': 'AI / Machine Learning',
  'Photonics': 'Photonics / Optics',
}

export default function SectorStocks({ sector, onBack }: SectorStocksProps) {
  const [data, setData] = useState<SectorData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sector) return

    async function fetchSectorData() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`https://chartwise-ai.onrender.com/api/predictions/sectors/${sector}`)
        if (response.ok) {
          const result = await response.json()
          setData(result)
        } else {
          setError('Failed to load sector data')
        }
      } catch (err) {
        setError('Error fetching sector data')
      } finally {
        setLoading(false)
      }
    }

    fetchSectorData()
  }, [sector])

  if (!sector) return null

  if (loading) {
    return (
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-1/3"></div>
          <div className="h-4 bg-slate-700 rounded w-1/2"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-slate-700 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Sectors
        </button>
        <div className="text-center py-8">
          <p className="text-danger-400">{error || 'No data available'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Sectors
          </button>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-primary-400" />
            {SECTOR_NAMES[sector] || sector}
          </h2>
          <p className="text-slate-400 text-sm">
            {data.analyzed} of {data.total_stocks} stocks analyzed
          </p>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900/50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-white">{data.statistics.average_score}%</p>
          <p className="text-xs text-slate-500">Avg Score</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-success-400">{data.statistics.bullish_count}</p>
          <p className="text-xs text-slate-500">Bullish</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">{data.statistics.neutral_count}</p>
          <p className="text-xs text-slate-500">Neutral</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-danger-400">{data.statistics.bearish_count}</p>
          <p className="text-xs text-slate-500">Bearish</p>
        </div>
      </div>

      {/* Stocks List */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Stocks in Sector
        </h3>
        {data.stocks.map((stock, index) => (
          <Link
            key={stock.symbol}
            href={`/stock/${stock.symbol}`}
            className="block bg-slate-900/30 hover:bg-slate-900/50 border border-slate-700 rounded-lg p-4 transition-all hover:scale-[1.02]"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-slate-500 font-mono w-6">#{index + 1}</span>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-lg font-bold text-white">{stock.symbol}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      stock.bullish_score >= 60 ? 'bg-success-500/20 text-success-300' :
                      stock.bullish_score <= 40 ? 'bg-danger-500/20 text-danger-300' :
                      'bg-yellow-500/20 text-yellow-300'
                    }`}>
                      {stock.recommendation}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-400">
                    <span>${stock.current_price.toFixed(2)}</span>
                    <span className={stock.change_percent >= 0 ? 'text-success-400' : 'text-danger-400'}>
                      {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <ScoreBadge score={stock.bullish_score} confidence={stock.confidence} />
                
                <div className="text-right hidden sm:block">
                  <div className="flex items-center gap-1 text-xs text-slate-500">
                    {stock.bullish_score >= 60 ? (
                      <TrendingUp className="w-3 h-3 text-success-400" />
                    ) : stock.bullish_score <= 40 ? (
                      <TrendingDown className="w-3 h-3 text-danger-400" />
                    ) : (
                      <Activity className="w-3 h-3 text-yellow-400" />
                    )}
                    <span>{Object.keys(stock.signals).length} signals</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Key Signals */}
            {Object.entries(stock.signals).slice(0, 3).map(([key, value]) => (
              <div key={key} className="mt-2 flex flex-wrap gap-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  value.includes('bullish') ? 'bg-success-500/20 text-success-300' :
                  value.includes('bearish') ? 'bg-danger-500/20 text-danger-300' :
                  'bg-slate-700 text-slate-300'
                }`}>
                  {key}: {value}
                </span>
              </div>
            ))}
          </Link>
        ))}
      </div>
    </div>
  )
}
