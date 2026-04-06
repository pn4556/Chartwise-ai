'use client'

import { useState } from 'react'
import { Filter, SlidersHorizontal, X } from 'lucide-react'

export interface FilterOptions {
  assetType: 'all' | 'stocks' | 'crypto' | 'commodity'
  minScore: number
  maxScore: number
  minConfidence: number
  recommendations: string[]
  sector: string
}

interface FilterBarProps {
  onFilterChange: (filters: FilterOptions) => void
}

const RECOMMENDATIONS = [
  { value: 'Strong Buy', label: 'Strong Buy', color: 'bg-green-500' },
  { value: 'Buy', label: 'Buy', color: 'bg-green-400' },
  { value: 'Hold', label: 'Hold', color: 'bg-yellow-500' },
  { value: 'Sell', label: 'Sell', color: 'bg-red-400' },
  { value: 'Strong Sell', label: 'Strong Sell', color: 'bg-red-500' },
]

const SECTORS = [
  { value: 'all', label: 'All Sectors' },
  { value: 'Tech', label: 'Technology' },
  { value: 'Finance', label: 'Finance' },
  { value: 'Healthcare', label: 'Healthcare' },
  { value: 'Energy', label: 'Energy' },
  { value: 'Consumer', label: 'Consumer' },
]

export default function FilterBar({ onFilterChange }: FilterBarProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [filters, setFilters] = useState<FilterOptions>({
    assetType: 'all',
    minScore: 0,
    maxScore: 100,
    minConfidence: 0,
    recommendations: [],
    sector: 'all'
  })

  // Helper to get asset type display label
  const getAssetTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'all': 'All',
      'stocks': 'Stocks Only',
      'crypto': 'Crypto Only',
      'commodity': 'Commodities Only'
    }
    return labels[type] || type
  }

  const handleChange = <K extends keyof FilterOptions>(key: K, value: FilterOptions[K]) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  const toggleRecommendation = (rec: string) => {
    const newRecs = filters.recommendations.includes(rec)
      ? filters.recommendations.filter(r => r !== rec)
      : [...filters.recommendations, rec]
    handleChange('recommendations', newRecs)
  }

  const clearFilters = () => {
    const defaultFilters: FilterOptions = {
      assetType: 'all',
      minScore: 0,
      maxScore: 100,
      minConfidence: 0,
      recommendations: [],
      sector: 'all'
    }
    setFilters(defaultFilters)
    onFilterChange(defaultFilters)
  }

  const hasActiveFilters = () => {
    return (
      filters.assetType !== 'all' ||
      filters.minScore > 0 ||
      filters.maxScore < 100 ||
      filters.minConfidence > 0 ||
      filters.recommendations.length > 0 ||
      filters.sector !== 'all'
    )
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl mb-6">
      {/* Header */}
      <div 
        className="flex items-center justify-between px-6 py-4 cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-5 h-5 text-primary-400" />
          <span className="font-semibold text-white">Filters</span>
          {hasActiveFilters() && (
            <span className="px-2 py-0.5 bg-primary-500/20 text-primary-400 text-xs rounded-full">
              Active
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {hasActiveFilters() && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                clearFilters()
              }}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              Clear all
            </button>
          )}
          {isOpen ? <X className="w-5 h-5 text-slate-400" /> : <Filter className="w-5 h-5 text-slate-400" />}
        </div>
      </div>

      {/* Filter Options */}
      {isOpen && (
        <div className="px-6 pb-6 border-t border-slate-700 pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Asset Type */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Asset Type</label>
              <div className="flex flex-wrap gap-2">
                {[
                  { value: 'all', label: 'All' },
                  { value: 'stocks', label: 'Stocks Only' },
                  { value: 'crypto', label: 'Crypto Only' },
                  { value: 'commodity', label: 'Commodities Only' },
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleChange('assetType', option.value as 'all' | 'stocks' | 'crypto' | 'commodity')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      filters.assetType === option.value
                        ? 'bg-primary-500 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sector Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Sector (Stocks)</label>
              <select
                value={filters.sector}
                onChange={(e) => handleChange('sector', e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              >
                {SECTORS.map((sector) => (
                  <option key={sector.value} value={sector.value}>
                    {sector.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Confidence Level */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Min Confidence: <span className="text-primary-400">{filters.minConfidence}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.minConfidence}
                onChange={(e) => handleChange('minConfidence', parseInt(e.target.value))}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
            </div>

            {/* Bullish Score Range */}
            <div className="md:col-span-2 lg:col-span-2">
              <label className="block text-sm font-medium text-slate-300 mb-3">
                Bullish Score Range: <span className="text-primary-400">{filters.minScore}% - {filters.maxScore}%</span>
              </label>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Min</span>
                    <span>{filters.minScore}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={filters.minScore}
                    onChange={(e) => {
                      const value = parseInt(e.target.value)
                      if (value <= filters.maxScore) {
                        handleChange('minScore', value)
                      }
                    }}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
                  />
                </div>
                <div className="text-slate-500">-</div>
                <div className="flex-1">
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Max</span>
                    <span>{filters.maxScore}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={filters.maxScore}
                    onChange={(e) => {
                      const value = parseInt(e.target.value)
                      if (value >= filters.minScore) {
                        handleChange('maxScore', value)
                      }
                    }}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
                  />
                </div>
              </div>
            </div>

            {/* Recommendation Filter */}
            <div className="md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium text-slate-300 mb-2">Recommendations</label>
              <div className="flex flex-wrap gap-2">
                {RECOMMENDATIONS.map((rec) => {
                  const isSelected = filters.recommendations.includes(rec.value)
                  return (
                    <button
                      key={rec.value}
                      onClick={() => toggleRecommendation(rec.value)}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all border ${
                        isSelected
                          ? `${rec.color} text-white border-transparent`
                          : 'bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600'
                      }`}
                    >
                      <span className="flex items-center gap-1.5">
                        {isSelected && <span className="w-1.5 h-1.5 bg-white rounded-full" />}
                        {rec.label}
                      </span>
                    </button>
                  )
                })}
                {filters.recommendations.length > 0 && (
                  <button
                    onClick={() => handleChange('recommendations', [])}
                    className="px-3 py-1.5 rounded-full text-sm text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

          </div>

          {/* Active Filters Summary */}
          {hasActiveFilters() && (
            <div className="mt-4 pt-4 border-t border-slate-700">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-slate-400">Active:</span>
                {filters.assetType !== 'all' && (
                  <span className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded-md">
                    {getAssetTypeLabel(filters.assetType)}
                  </span>
                )}
                {(filters.minScore > 0 || filters.maxScore < 100) && (
                  <span className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded-md">
                    Score: {filters.minScore}-{filters.maxScore}%
                  </span>
                )}
                {filters.minConfidence > 0 && (
                  <span className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded-md">
                    Confidence: {filters.minConfidence}%
                  </span>
                )}
                {filters.recommendations.length > 0 && (
                  <span className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded-md">
                    {filters.recommendations.length} recommendation{filters.recommendations.length > 1 ? 's' : ''}
                  </span>
                )}
                {filters.sector !== 'all' && (
                  <span className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded-md">
                    Sector: {filters.sector}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
