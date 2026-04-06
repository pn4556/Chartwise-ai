'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Bell, Check, X, TrendingUp, TrendingDown, AlertTriangle, 
  Target, Zap, BarChart3, Filter, RefreshCw, Sparkles,
  CandlestickChart, Activity, Volume2
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
  category: string
  triggered_by: string[]
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pattern' | 'indicator' | 'price' | 'unacknowledged'>('all')
  const [scanning, setScanning] = useState(false)
  const [stats, setStats] = useState<{
    total: number
    unacknowledged: number
    by_type: Record<string, number>
    by_severity: Record<string, number>
  }>({
    total: 0,
    unacknowledged: 0,
    by_type: {},
    by_severity: {}
  })

  useEffect(() => {
    fetchAlerts()
    fetchStats()
  }, [filter])

  const fetchAlerts = async () => {
    setLoading(true)
    try {
      let url = 'https://chartwise-ai.onrender.com/api/alerts/'
      
      if (filter === 'unacknowledged') {
        url = 'https://chartwise-ai.onrender.com/api/alerts/unacknowledged'
      } else if (filter !== 'all') {
        url = `https://chartwise-ai.onrender.com/api/alerts/?alert_type=${filter}`
      }
      
      const res = await fetch(url)
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

  const fetchStats = async () => {
    try {
      const res = await fetch('https://chartwise-ai.onrender.com/api/alerts/stats')
      if (res.ok) {
        const data = await res.json()
        setStats(data.statistics)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const acknowledgeAlert = async (alertId: string) => {
    try {
      const res = await fetch(`https://chartwise-ai.onrender.com/api/alerts/${alertId}/acknowledge`, {
        method: 'POST'
      })
      if (res.ok) {
        setAlerts(alerts.map(a => a.id === alertId ? { ...a, acknowledged: true } : a))
        fetchStats()
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error)
    }
  }

  const scanForAlerts = async () => {
    setScanning(true)
    try {
      const res = await fetch('https://chartwise-ai.onrender.com/api/alerts/scan')
      if (res.ok) {
        await fetchAlerts()
        await fetchStats()
      }
    } catch (error) {
      console.error('Error scanning:', error)
    } finally {
      setScanning(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-rose-500 bg-rose-500/10 border-rose-500/30'
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/30'
      case 'medium': return 'text-amber-500 bg-amber-500/10 border-amber-500/30'
      default: return 'text-blue-500 bg-blue-500/10 border-blue-500/30'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'pattern': return <CandlestickChart className="w-4 h-4" />
      case 'indicator': return <Activity className="w-4 h-4" />
      case 'breakout': return <Zap className="w-4 h-4" />
      case 'volume': return <Volume2 className="w-4 h-4" />
      case 'reversal': return <TrendingUp className="w-4 h-4" />
      default: return <Bell className="w-4 h-4" />
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

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'unacknowledged') return !a.acknowledged
    if (filter === 'all') return true
    return a.type === filter
  })

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900/50 via-purple-900/50 to-pink-900/50 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center">
                <Bell className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Alerts & Signals</h1>
                <p className="text-slate-400">Pattern detection and trading signals</p>
              </div>
            </div>
            
            <button
              onClick={scanForAlerts}
              disabled={scanning}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 text-white rounded-lg font-medium transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
              {scanning ? 'Scanning...' : 'Scan Now'}
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
              <p className="text-slate-500 text-sm">Total Alerts</p>
              <p className="text-2xl font-bold text-white">{stats.total}</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
              <p className="text-slate-500 text-sm">New Alerts</p>
              <p className="text-2xl font-bold text-rose-400">{stats.unacknowledged}</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
              <p className="text-slate-500 text-sm">Patterns</p>
              <p className="text-2xl font-bold text-purple-400">{stats.by_type?.pattern || 0}</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
              <p className="text-slate-500 text-sm">High Priority</p>
              <p className="text-2xl font-bold text-orange-400">{stats.by_severity?.high || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="border-b border-slate-800 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex flex-wrap items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500 mr-2" />
            {[
              { id: 'all', label: 'All Alerts', count: stats.total },
              { id: 'pattern', label: 'Patterns', count: stats.by_type?.pattern || 0 },
              { id: 'indicator', label: 'Indicators', count: stats.by_type?.indicator || 0 },
              { id: 'unacknowledged', label: 'New', count: stats.unacknowledged }
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === f.id
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                {f.label}
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  filter === f.id ? 'bg-indigo-500' : 'bg-slate-700'
                }`}>
                  {f.count}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-slate-400">Loading alerts...</span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <AnimatePresence>
              {filteredAlerts.map((alert, idx) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`bg-slate-900 rounded-xl p-5 border-l-4 ${
                    alert.acknowledged ? 'border-slate-700 opacity-60' : 
                    alert.severity === 'critical' ? 'border-rose-500' :
                    alert.severity === 'high' ? 'border-orange-500' :
                    alert.severity === 'medium' ? 'border-amber-500' : 'border-blue-500'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Link 
                          href={`/stock/${alert.symbol}`}
                          className="text-lg font-bold text-white hover:text-indigo-400 transition-colors"
                        >
                          {alert.symbol}
                        </Link>
                        
                        <span className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium ${getTypeColor(alert.type)}`}>
                          {getTypeIcon(alert.type)}
                          {alert.type.replace('_', ' ').toUpperCase()}
                        </span>
                        
                        <span className={`px-2 py-1 rounded-lg text-xs font-medium border ${getSeverityColor(alert.severity)}`}>
                          {alert.severity.toUpperCase()}
                        </span>

                        {alert.pattern_name && (
                          <span className="px-2 py-1 bg-purple-500/10 text-purple-400 rounded-lg text-xs">
                            {alert.pattern_name.replace('_', ' ').toUpperCase()}
                          </span>
                        )}
                      </div>

                      <h3 className="text-white font-semibold mb-1">{alert.title}</h3>
                      <p className="text-slate-400 text-sm mb-3">{alert.message}</p>

                      <div className="flex flex-wrap items-center gap-4 text-sm">
                        {alert.price_at_trigger && (
                          <span className="text-slate-500">
                            Price: <span className="text-slate-300">${alert.price_at_trigger.toFixed(2)}</span>
                          </span>
                        )}
                        
                        {alert.target_price && (
                          <span className="text-emerald-400">
                            Target: ${alert.target_price.toFixed(2)}
                          </span>
                        )}
                        
                        {alert.stop_loss && (
                          <span className="text-rose-400">
                            Stop: ${alert.stop_loss.toFixed(2)}
                          </span>
                        )}

                        {alert.triggered_by && alert.triggered_by.length > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-slate-500">Signals:</span>
                            <div className="flex gap-1">
                              {alert.triggered_by.slice(0, 3).map((signal, i) => (
                                <span key={i} className="px-2 py-0.5 bg-slate-800 text-slate-400 rounded text-xs">
                                  {signal.replace('_', ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        <span className="text-slate-600">
                          {new Date(alert.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {!alert.acknowledged && (
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg text-sm transition-colors ml-4"
                      >
                        <Check className="w-4 h-4" />
                        Acknowledge
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {filteredAlerts.length === 0 && (
              <div className="text-center py-20">
                <Bell className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                <p className="text-slate-400 text-lg mb-2">No alerts found</p>
                <p className="text-slate-600 text-sm">Scan for new patterns and signals</p>
                <button
                  onClick={scanForAlerts}
                  className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors"
                >
                  Scan Now
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
