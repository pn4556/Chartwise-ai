'use client'

import { useAuth } from '@/lib/auth'
import Header from '@/components/Header'
import { User, Mail, TrendingUp, Award, Calendar, Wallet } from 'lucide-react'

export default function Profile() {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Please Sign In</h1>
          <p className="text-slate-400">You need to be logged in to view your profile.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">My Profile</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* User Info Card */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                <User className="w-10 h-10 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">{user?.name}</h2>
                <div className="flex items-center gap-2 text-slate-400 text-sm">
                  <Mail className="w-4 h-4" />
                  {user?.email}
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">Member Since</span>
                <span className="text-white flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-500" />
                  Jan 2024
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">Account Type</span>
                <span className="px-2 py-1 bg-primary-500/20 text-primary-400 text-xs rounded-full">
                  Free
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-slate-400">Status</span>
                <span className="flex items-center gap-1 text-success-400 text-sm">
                  <div className="w-2 h-2 bg-success-400 rounded-full" />
                  Active
                </span>
              </div>
            </div>
          </div>

          {/* Trading Stats */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center">
                <Wallet className="w-8 h-8 text-primary-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">${user?.portfolio_value?.toLocaleString()}</p>
                <p className="text-sm text-slate-500">Portfolio Value</p>
              </div>
              
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center">
                <TrendingUp className="w-8 h-8 text-success-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">{user?.win_rate}%</p>
                <p className="text-sm text-slate-500">Win Rate</p>
              </div>
              
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center">
                <Award className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">{user?.trades_count}</p>
                <p className="text-sm text-slate-500">Total Trades</p>
              </div>
              
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center">
                <TrendingUp className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-success-400">+$450</p>
                <p className="text-sm text-slate-500">This Month</p>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">Recent Activity</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-slate-700/50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-success-500/20 rounded-lg flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-success-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Opened Long Position</p>
                      <p className="text-sm text-slate-500">AAPL - 10 shares @ $175.43</p>
                    </div>
                  </div>
                  <span className="text-sm text-slate-500">2 hours ago</span>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-slate-700/50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-danger-500/20 rounded-lg flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-danger-400 rotate-180" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Closed Short Position</p>
                      <p className="text-sm text-slate-500">TSLA - 5 shares @ $245.67 (+$21.65)</p>
                    </div>
                  </div>
                  <span className="text-sm text-slate-500">Yesterday</span>
                </div>

                <div className="flex items-center justify-between py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center">
                      <Award className="w-5 h-5 text-primary-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Achievement Unlocked</p>
                      <p className="text-sm text-slate-500">First Week of Trading</p>
                    </div>
                  </div>
                  <span className="text-sm text-slate-500">3 days ago</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
