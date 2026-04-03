'use client'

import { useEffect, useState } from 'react'
import { fetchTopPicks } from '@/lib/api'
import { formatPrice, getRecommendationColor } from '@/lib/utils'
import ScoreBadge from './ScoreBadge'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'
import Link from 'next/link'

interface TopPick {
  rank: number
  symbol: string
  asset_type: string
  bullish_score: number
  confidence: number
  recommendation: string
  current_price: number
  key_signals: string[]
}

export default function TopPicksList() {
  const [picks, setPicks] = useState<TopPick[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadPicks() {
      try {
        const data = await fetchTopPicks(10)
        setPicks(data)
      } catch (err) {
        setError('Failed to load top picks')
      } finally {
        setLoading(false)
      }
    }

    loadPicks()
    const interval = setInterval(loadPicks, 60000) // Refresh every minute
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 bg-slate-800 rounded-lg" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-danger-400 text-center py-8">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {picks.map((pick) => (
        <Link
          key={pick.symbol}
          href={`/stock/${pick.symbol}`}
          className="block bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl p-4 transition-all hover:scale-[1.02]"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-2xl font-bold text-slate-500 w-8">
                #{pick.rank}
              </span>
              
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-bold text-white">{pick.symbol}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded ${pick.asset_type === 'crypto' ? 'bg-purple-500/20 text-purple-300' : 'bg-blue-500/20 text-blue-300'}`}>
                    {pick.asset_type}
                  </span>
                </div>
                <p className="text-slate-400 text-sm">
                  {formatPrice(pick.current_price || 0)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <ScoreBadge score={pick.bullish_score} confidence={pick.confidence} />
              
              <div className="text-right">
                <p className={`font-semibold ${getRecommendationColor(pick.recommendation)}`}>
                  {pick.recommendation}
                </p>
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  {pick.bullish_score >= 60 ? (
                    <TrendingUp className="w-3 h-3 text-success-400" />
                  ) : pick.bullish_score <= 40 ? (
                    <TrendingDown className="w-3 h-3 text-danger-400" />
                  ) : (
                    <Activity className="w-3 h-3 text-yellow-400" />
                  )}
                  <span>{pick.key_signals.length} signals</span>
                </div>
              </div>
            </div>
          </div>

          {pick.key_signals.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {pick.key_signals.slice(0, 3).map((signal, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-1 bg-slate-700/50 text-slate-300 rounded"
                >
                  {signal}
                </span>
              ))}
            </div>
          )}
        </Link>
      ))}
    </div>
  )
}
