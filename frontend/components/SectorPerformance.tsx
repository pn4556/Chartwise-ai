'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, PieChart } from 'lucide-react'

interface SectorData {
  name: string
  avgScore: number
  topStock: string
  stockCount: number
  trend: 'up' | 'down' | 'neutral'
}

export default function SectorPerformance() {
  const [sectors, setSectors] = useState<SectorData[]>([
    { name: 'Technology', avgScore: 72, topStock: 'NVDA', stockCount: 28, trend: 'up' },
    { name: 'Healthcare', avgScore: 58, topStock: 'LLY', stockCount: 18, trend: 'neutral' },
    { name: 'Finance', avgScore: 64, topStock: 'JPM', stockCount: 18, trend: 'up' },
    { name: 'Energy', avgScore: 45, topStock: 'XOM', stockCount: 10, trend: 'down' },
    { name: 'Consumer', avgScore: 61, topStock: 'AMZN', stockCount: 18, trend: 'up' },
    { name: 'Industrial', avgScore: 52, topStock: 'CAT', stockCount: 10, trend: 'neutral' },
    { name: 'Comm Services', avgScore: 59, topStock: 'META', stockCount: 10, trend: 'up' },
    { name: 'Real Estate', avgScore: 48, topStock: 'PLD', stockCount: 10, trend: 'down' },
    { name: 'Materials', avgScore: 50, topStock: 'LIN', stockCount: 10, trend: 'neutral' },
    { name: 'Utilities', avgScore: 44, topStock: 'NEE', stockCount: 10, trend: 'down' },
    { name: 'AI / ML', avgScore: 68, topStock: 'PLTR', stockCount: 20, trend: 'up' },
    { name: 'Photonics', avgScore: 46, topStock: 'COHR', stockCount: 18, trend: 'neutral' },
  ])

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <PieChart className="w-5 h-5 text-primary-400" />
          Sector Performance
        </h2>
      </div>

      <div className="space-y-4">
        {sectors.map((sector) => (
          <div key={sector.name} className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-white font-medium">{sector.name}</span>
                <span className={`text-sm ${sector.avgScore >= 60 ? 'text-success-400' : sector.avgScore >= 40 ? 'text-yellow-400' : 'text-danger-400'}`}>
                  {sector.avgScore}% avg
                </span>
              </div>
              
              {/* Progress bar */}
              <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    sector.avgScore >= 60 ? 'bg-success-400' : 
                    sector.avgScore >= 40 ? 'bg-yellow-400' : 'bg-danger-400'
                  }`}
                  style={{ width: `${sector.avgScore}%` }}
                />
              </div>
              
              <div className="flex items-center justify-between mt-1 text-xs text-slate-500">
                <span>Top: {sector.topStock}</span>
                <div className="flex items-center gap-1">
                  {sector.trend === 'up' ? (
                    <TrendingUp className="w-3 h-3 text-success-400" />
                  ) : sector.trend === 'down' ? (
                    <TrendingDown className="w-3 h-3 text-danger-400" />
                  ) : null}
                  <span>{sector.stockCount} stocks</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-slate-700">
        <div className="text-center">
          <p className="text-2xl font-bold text-success-400">5</p>
          <p className="text-xs text-slate-500">Bullish Sectors</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-yellow-400">4</p>
          <p className="text-xs text-slate-500">Neutral</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-danger-400">4</p>
          <p className="text-xs text-slate-500">Bearish</p>
        </div>
      </div>
    </div>
  )
}
