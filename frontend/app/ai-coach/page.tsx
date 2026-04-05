'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, TrendingUp, TrendingDown, AlertTriangle, 
  Lightbulb, Target, Shield, ArrowRight, Sparkles,
  BarChart3, Activity, Zap
} from 'lucide-react'
import Link from 'next/link'

interface AIInsight {
  type: string
  asset: string
  message: string
  confidence: number
  action: string
  timeframe: string
  reasoning: string[]
  risk_level: string
  price: number
  probabilities: {
    up: number
    down: number
    sideways: number
  }
}

interface SectorAnalysis {
  sector: string
  outlook: string
  confidence: number
  ai_score: number
  top_picks: {symbol: string, score: number}[]
  insight: string
  catalysts: string[]
  risks: string[]
}

interface AIPrediction {
  symbol: string
  prediction: string
  direction: string
  confidence: number
  probability_up: number
  probability_down: number
  strength: string
  price: number
}

export default function AICoachPage() {
  const [insights, setInsights] = useState<AIInsight[]>([])
  const [sectors, setSectors] = useState<SectorAnalysis[]>([])
  const [predictions, setPredictions] = useState<AIPrediction[]>([])
  const [marketSummary, setMarketSummary] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'insights' | 'predictions' | 'sectors'>('insights')

  useEffect(() => {
    fetchAIData()
  }, [])

  const fetchAIData = async () => {
    setLoading(true)
    try {
      // Fetch insights
      const insightsRes = await fetch('https://chartwise-ai.onrender.com/api/ai-coach/insights?limit=15')
      if (insightsRes.ok) {
        const insightsData = await insightsRes.json()
        setInsights(insightsData.insights)
      }

      // Fetch predictions
      const predictionsRes = await fetch('https://chartwise-ai.onrender.com/api/ai-coach/predictions?limit=20')
      if (predictionsRes.ok) {
        const predictionsData = await predictionsRes.json()
        setPredictions(predictionsData.predictions)
      }

      // Fetch sectors
      const sectorsRes = await fetch('https://chartwise-ai.onrender.com/api/ai-coach/sectors')
      if (sectorsRes.ok) {
        const sectorsData = await sectorsRes.json()
        setSectors(sectorsData.sectors)
      }

      // Fetch market summary
      const summaryRes = await fetch('https://chartwise-ai.onrender.com/api/ai-coach/market-summary')
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json()
        setMarketSummary(summaryData.summary)
      }
    } catch (error) {
      console.error('Error fetching AI data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'buy': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30'
      case 'sell': return 'text-rose-400 bg-rose-400/10 border-rose-400/30'
      case 'hold': return 'text-amber-400 bg-amber-400/10 border-amber-400/30'
      default: return 'text-slate-400 bg-slate-400/10 border-slate-400/30'
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-emerald-400'
      case 'medium': return 'text-amber-400'
      case 'high': return 'text-rose-400'
      default: return 'text-slate-400'
    }
  }

  const getOutlookColor = (outlook: string) => {
    switch (outlook) {
      case 'bullish': return 'text-emerald-400 bg-emerald-400/10'
      case 'bearish': return 'text-rose-400 bg-rose-400/10'
      case 'neutral': return 'text-amber-400 bg-amber-400/10'
      default: return 'text-slate-400 bg-slate-400/10'
    }
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900/50 via-purple-900/50 to-pink-900/50 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">AI Coach</h1>
              <p className="text-slate-400">Advanced AI-powered trading insights & predictions</p>
            </div>
          </div>
          
          {marketSummary && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-900/50 backdrop-blur-sm rounded-xl p-4 border border-indigo-500/30"
            >
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-indigo-400 mt-0.5 flex-shrink-0" />
                <p className="text-slate-200">{marketSummary}</p>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-800 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1">
            {[
              { id: 'insights', label: 'AI Insights', icon: Lightbulb },
              { id: 'predictions', label: 'Predictions', icon: Target },
              { id: 'sectors', label: 'Sector AI', icon: BarChart3 }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'text-indigo-400 border-indigo-400 bg-indigo-500/10'
                    : 'text-slate-400 border-transparent hover:text-slate-200'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-slate-400">AI analyzing market data...</span>
            </div>
          </div>
        ) : (
          <>
            {/* AI Insights Tab */}
            {activeTab === 'insights' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {insights.map((insight, idx) => (
                    <motion.div
                      key={insight.asset}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="bg-slate-900 rounded-xl p-5 border border-slate-800 hover:border-indigo-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <Link href={`/stock/${insight.asset}`} className="text-xl font-bold text-white hover:text-indigo-400 transition-colors">
                            {insight.asset}
                          </Link>
                          <p className="text-slate-500 text-sm">${insight.price?.toFixed(2) || '--'}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getActionColor(insight.action)}`}>
                          {insight.action.toUpperCase()}
                        </span>
                      </div>

                      <p className="text-slate-300 text-sm mb-4">{insight.message}</p>

                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-500">Confidence</span>
                          <span className={`font-medium ${
                            insight.confidence >= 70 ? 'text-emerald-400' :
                            insight.confidence >= 50 ? 'text-amber-400' : 'text-rose-400'
                          }`}>
                            {insight.confidence.toFixed(0)}%
                          </span>
                        </div>

                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-500">Risk Level</span>
                          <span className={`font-medium ${getRiskColor(insight.risk_level)}`}>
                            {insight.risk_level.charAt(0).toUpperCase() + insight.risk_level.slice(1)}
                          </span>
                        </div>

                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-500">Timeframe</span>
                          <span className="text-slate-300">{insight.timeframe}</span>
                        </div>

                        {insight.probabilities && (
                          <div className="pt-3 border-t border-slate-800">
                            <div className="flex gap-2 text-xs">
                              <span className="text-emerald-400">↑ {insight.probabilities.up.toFixed(0)}%</span>
                              <span className="text-rose-400">↓ {insight.probabilities.down.toFixed(0)}%</span>
                              <span className="text-slate-400">→ {insight.probabilities.sideways.toFixed(0)}%</span>
                            </div>
                          </div>
                        )}
                      </div>

                      {insight.reasoning && insight.reasoning.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-slate-800">
                          <p className="text-xs text-slate-500 mb-2">Key Factors:</p>
                          <ul className="space-y-1">
                            {insight.reasoning.slice(0, 3).map((reason, i) => (
                              <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                                <span className="text-indigo-400 mt-0.5">•</span>
                                {reason}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>

                {insights.length === 0 && (
                  <div className="text-center py-20">
                    <Brain className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400">No insights available. Try refreshing.</p>
                  </div>
                )}
              </div>
            )}

            {/* Predictions Tab */}
            {activeTab === 'predictions' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {predictions.map((pred, idx) => (
                    <motion.div
                      key={pred.symbol}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.03 }}
                      className={`bg-slate-900 rounded-xl p-5 border-2 ${
                        pred.direction === 'up' ? 'border-emerald-500/30' :
                        pred.direction === 'down' ? 'border-rose-500/30' :
                        'border-amber-500/30'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <Link href={`/stock/${pred.symbol}`} className="text-lg font-bold text-white hover:text-indigo-400">
                          {pred.symbol}
                        </Link>
                        <span className={`text-2xl ${
                          pred.direction === 'up' ? 'text-emerald-400' :
                          pred.direction === 'down' ? 'text-rose-400' :
                          'text-amber-400'
                        }`}>
                          {pred.prediction}
                        </span>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-500">Strength</span>
                          <span className={`font-medium ${
                            pred.strength === 'Strong' ? 'text-emerald-400' : 'text-amber-400'
                          }`}>
                            {pred.strength}
                          </span>
                        </div>

                        <div className="flex justify-between text-sm">
                          <span className="text-slate-500">Confidence</span>
                          <span className="text-slate-300">{pred.confidence.toFixed(0)}%</span>
                        </div>

                        <div className="flex justify-between text-xs text-slate-500">
                          <span>Bullish: {pred.probability_up.toFixed(0)}%</span>
                          <span>Bearish: {pred.probability_down.toFixed(0)}%</span>
                        </div>

                        <div className="w-full bg-slate-800 rounded-full h-2 mt-3">
                          <div 
                            className={`h-2 rounded-full ${
                              pred.direction === 'up' ? 'bg-emerald-500' :
                              pred.direction === 'down' ? 'bg-rose-500' :
                              'bg-amber-500'
                            }`}
                            style={{ width: `${pred.confidence}%` }}
                          />
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {predictions.length === 0 && (
                  <div className="text-center py-20">
                    <Target className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400">No predictions available.</p>
                  </div>
                )}
              </div>
            )}

            {/* Sectors Tab */}
            {activeTab === 'sectors' && (
              <div className="space-y-4">
                {sectors.map((sector, idx) => (
                  <motion.div
                    key={sector.sector}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="bg-slate-900 rounded-xl p-6 border border-slate-800"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <h3 className="text-xl font-bold text-white">{sector.sector}</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getOutlookColor(sector.outlook)}`}>
                          {sector.outlook.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-slate-500">AI Score</p>
                        <p className={`text-2xl font-bold ${
                          sector.ai_score >= 60 ? 'text-emerald-400' :
                          sector.ai_score >= 40 ? 'text-amber-400' : 'text-rose-400'
                        }`}>
                          {sector.ai_score.toFixed(0)}
                        </p>
                      </div>
                    </div>

                    <p className="text-slate-300 mb-4">{sector.insight}</p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-slate-500 mb-2 flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-emerald-400" />
                          Top Picks
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {sector.top_picks.map((pick) => (
                            <Link
                              key={pick.symbol}
                              href={`/stock/${pick.symbol}`}
                              className="px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-lg text-sm hover:bg-emerald-500/20 transition-colors"
                            >
                              {pick.symbol}
                            </Link>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-sm text-slate-500 mb-2 flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-rose-400" />
                          Catalysts
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {sector.catalysts.map((cat, i) => (
                            <span key={i} className="px-2 py-1 bg-slate-800 text-slate-300 rounded text-xs">
                              {cat}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-slate-500">
                        Confidence: <span className="text-slate-300">{sector.confidence.toFixed(0)}%</span>
                      </span>
                      <span className="text-slate-600">|</span>
                      <span className="text-slate-500">
                        Stocks Analyzed: <span className="text-slate-300">{sector.stocks_analyzed}</span>
                      </span>
                    </div>
                  </motion.div>
                ))}

                {sectors.length === 0 && (
                  <div className="text-center py-20">
                    <BarChart3 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400">No sector analysis available.</p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
