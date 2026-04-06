'use client'

import { useState } from 'react'
import Header from '@/components/Header'
import TopPicksList from '@/components/TopPicksList'
import MarketOverview from '@/components/MarketOverview'
import SectorPerformance from '@/components/SectorPerformance'
import SectorStocks from '@/components/SectorStocks'
import FilterBar, { type FilterOptions } from '@/components/FilterBar'
import ActiveAlerts from '@/components/ActiveAlerts'
import { Sparkles, TrendingUp, Shield, Bell } from 'lucide-react'

export default function Home() {
  const [filters, setFilters] = useState<FilterOptions>({
    assetType: 'all',
    minScore: 0,
    maxScore: 100,
    minConfidence: 0,
    recommendations: [],
    sector: 'all'
  })
  
  const [selectedSector, setSelectedSector] = useState<string | null>(null)

  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters)
  }
  
  const handleSectorClick = (sector: string) => {
    setSelectedSector(sector === selectedSector ? null : sector)
  }
  
  const handleBackToSectors = () => {
    setSelectedSector(null)
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            Let <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">AI</span> find your next trade
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Smart trading ideas powered by algorithmic analysis. 
            No opinions, just data-driven insights.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4 mt-8">
            <div className="flex items-center gap-2 text-slate-300">
              <Sparkles className="w-5 h-5 text-primary-400" />
              <span>AI-Powered Analysis</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <TrendingUp className="w-5 h-5 text-success-400" />
              <span>Top 20 Daily Picks</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <Shield className="w-5 h-5 text-purple-400" />
              <span>Paper Trading</span>
            </div>
          </div>
        </div>

        {/* Market Overview */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Market Overview</h2>
          <MarketOverview />
        </section>

        {/* Active Alerts */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Bell className="w-6 h-6 text-rose-400" />
              <h2 className="text-2xl font-bold text-white">Active Alerts & Signals</h2>
            </div>
          </div>
          <ActiveAlerts />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          {/* Sector Performance - Left Column */}
          <div className="lg:col-span-1">
            {!selectedSector ? (
              <SectorPerformance 
                onSectorClick={handleSectorClick}
                selectedSector={selectedSector}
              />
            ) : (
              <SectorStocks 
                sector={selectedSector}
                onBack={handleBackToSectors}
              />
            )}
          </div>

          {/* Top Picks with Filters - Right Columns */}
          <div className="lg:col-span-2">
            <FilterBar onFilterChange={handleFilterChange} />
            
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Top 20 Strongest Setups</h2>
              <span className="text-sm text-slate-500">Updates every 15 minutes</span>
            </div>
            <TopPicksList filters={filters} />
          </div>
        </div>
      </main>
    </div>
  )
}
