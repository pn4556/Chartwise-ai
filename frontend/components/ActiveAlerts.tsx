'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Bell, TrendingUp, TrendingDown, AlertTriangle, 
  Zap, CandlestickChart, Activity, Volume2, ArrowRight
} from 'lucide-react'
import Link from 'next/link'

interface Alert {
  id: string
  symbol: string
  type: string
  severity: string
  title: string
  message: string
  timestamp: string
  pattern_name?: string
  price_at_trigger?: number
  target_price?: number
  stop_loss?: number
  acknowledged: boolean
  triggered_by: string[]
}

export default function ActiveAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAlerts()
    // Refresh every 60 seconds
    const interval = setInterval(fetchAlerts, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchAlerts = async () => {
    try {
      const res = await fetch('https://chartwise-ai.onrender.com/api/alerts/unacknowledged?limit=6')
      if (res.ok) {
        const data = await res.json()
        setAlerts(data.alerts || [])
      }
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-rose-500'
      case 'high': return 'bg-orange-500'
      case 'medium': return 'bg-amber-500'
      default: return 'bg-blue-500'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'pattern': return <CandlestickChart className="w-3 h-3" />
      case 'indicator': return <Activity className="w-3 h-3" />
      case 'breakout': return <Zap className="w-3 h-3" />
      case 'volume': return <Volume2 className="w-3 h-3" />
      case 'reversal': return <TrendingUp className="w-3 h-3" />
      default: return <Bell className="w-3 h-3" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'pattern': return 'text-purple-400 bg-purple-400/10'
      case 'indicator': return 'text-blue-400 bg-blue-400/10'
      case 'breakout': return 'text-emerald-400 bg-emerald-400/10'
      case 'volume': return 'text-cyan-400 bg-cyan-400/10'
      case 'reversal': return 'text-rose-400 bg-rose-400/10'
      default: return 'text-slate-400 bg-slate-400/10'
    }
  }

  if (loading) {
    return (
      <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  if (alerts.length === 0) {
    return (
      <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
        <div className="text-center py-8">
          <Bell className="w-12 h-12 text-slate-700 mx-auto mb-3" />
          <p className="text-slate-500">No active alerts</p>
          <p className="text-slate-600 text-sm mt-1">Pattern alerts will appear here when detected</p>
          <Link 
            href="/alerts"
            className="inline-flex items-center gap-2 mt-4 text-indigo-400 hover:text-indigo-300 text-sm"
          >
            View All Alerts <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {alerts.map((alert, idx) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="relative bg-slate-800/50 rounded-lg p-4 border-l-4 border-slate-700 hover:border-indigo-500 transition-colors group"
          >
            {/* Severity indicator */}
            <div className={`absolute top-0 right-0 w-2 h-2 rounded-full m-2 ${getSeverityColor(alert.severity)}`} />
            
            <div className="flex items-start justify-between mb-2">
              <Link 
                href={`/stock/${alert.symbol}`}
                className="text-lg font-bold text-white hover:text-indigo-400 transition-colors"
              >
                {alert.symbol}
              </Link>
              <span className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${getTypeColor(alert.type)}`}>
                {getTypeIcon(alert.type)}
              </span>
            </div>

            <h3 className="text-sm font-semibold text-slate-200 mb-1 line-clamp-1">{alert.title}</h3>
            <p className="text-xs text-slate-400 line-clamp-2 mb-3">{alert.message}</p>

            {alert.pattern_name && (
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded text-xs">
                  {alert.pattern_name.replace('_', ' ').toUpperCase()}
                </span>
              </div>
            )}

            <div className="flex items-center justify-between text-xs">
              {alert.price_at_trigger && (
                <span className="text-slate-500">
                  @ ${alert.price_at_trigger.toFixed(2)}
                </span>
              )}
              
              <span className="text-slate-600">
                {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>

            {(alert.target_price || alert.stop_loss) && (
              <div className="flex items-center gap-3 mt-2 pt-2 border-t border-slate-700 text-xs">
                {alert.target_price && (
                  <span className="text-emerald-400">
                    T: ${alert.target_price.toFixed(2)}
                  </span>
                )}
                {alert.stop_loss && (
                  <span className="text-rose-400">
                    S: ${alert.stop_loss.toFixed(2)}
                  </span>
                )}
              </div>
            )}
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-800 flex justify-center">
        <Link 
          href="/alerts"
          className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 text-sm font-medium"
        >
          View All Alerts & Scan for More
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  )
}
