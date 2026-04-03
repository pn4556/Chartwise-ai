'use client'

import Header from '@/components/Header'
import TopPicksList from '@/components/TopPicksList'
import MarketOverview from '@/components/MarketOverview'
import SectorPerformance from '@/components/SectorPerformance'
import FilterBar from '@/components/FilterBar'
import { Sparkles, TrendingUp, Shield } from 'lucide-react'

export default function Home() {
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
              <span>Top 10 Daily Picks</span>
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          {/* Sector Performance */}
          <div className="lg:col-span-1">
            <SectorPerformance />
          </div>

          {/* Top Picks with Filters */}
          <div className="lg:col-span-2">
            <FilterBar onFilterChange={(filters) => console.log('Filters:', filters)} />
            
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Top 10 Strongest Setups</h2>
              <span className="text-sm text-slate-500">Updates every 15 minutes</span>
            </div>
            <TopPicksList />
          </div>
        </div>
      </main>
    </div>
  )
}
