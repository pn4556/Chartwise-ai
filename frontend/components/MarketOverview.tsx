'use client'

import { useEffect, useState } from 'react'
import { fetchMarketOverview } from '@/lib/api'
import { TrendingUp, TrendingDown, Minus, BarChart3 } from 'lucide-react'

interface MarketData {
  bullish_count: number
  bearish_count: number
  neutral_count: number
  average_score: number
  top_performer: string
  most_bearish: string
  last_updated: string
}

export default function MarketOverview() {
  const [data, setData] = useState<MarketData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const overview = await fetchMarketOverview()
        setData(overview)
      } catch (err) {
        console.error('Failed to load market overview')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  if (loading || !data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-pulse">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-24 bg-slate-800 rounded-xl" />
        ))}
      </div>
    )
  }

  const total = data.bullish_count + data.bearish_count + data.neutral_count
  const bullishPercent = total > 0 ? (data.bullish_count / total) * 100 : 0

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-400 text-sm">Market Sentiment</span>
          <BarChart3 className="w-4 h-4 text-slate-500" />
        </div>
        <div className="flex items-end gap-2">
          <span className={`text-2xl font-bold ${bullishPercent >= 50 ? 'text-success-400' : 'text-danger-400'}`}>
            {bullishPercent.toFixed(0)}%
          </span>
          <span className="text-slate-500 text-sm mb-1">bullish</span>
        </div>
        <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-success-500 to-success-400"
            style={{ width: `${bullishPercent}%` }}
          />
        </div>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-400 text-sm">Bullish Assets</span>
          <TrendingUp className="w-4 h-4 text-success-400" />
        </div>
        <div className="text-2xl font-bold text-success-400">
          {data.bullish_count}
        </div>
        <p className="text-xs text-slate-500 mt-1">Score ≥ 60%</p>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-400 text-sm">Bearish Assets</span>
          <TrendingDown className="w-4 h-4 text-danger-400" />
        </div>
        <div className="text-2xl font-bold text-danger-400">
          {data.bearish_count}
        </div>
        <p className="text-xs text-slate-500 mt-1">Score ≤ 40%</p>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-400 text-sm">Avg Score</span>
          <Minus className="w-4 h-4 text-yellow-400" />
        </div>
        <div className={`text-2xl font-bold ${data.average_score >= 50 ? 'text-success-400' : 'text-danger-400'}`}>
          {data.average_score.toFixed(1)}%
        </div>
        <p className="text-xs text-slate-500 mt-1">Across all assets</p>
      </div>
    </div>
  )
}
