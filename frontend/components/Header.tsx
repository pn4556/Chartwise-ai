'use client'

import { Zap, Menu, X, User, LogOut, Brain } from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'
import { useAuth } from '@/lib/auth'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">
              Chartwise<span className="text-primary-400">AI</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-6">
            <Link href="/" className="text-slate-300 hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/ai-coach" className="text-slate-300 hover:text-indigo-400 transition-colors flex items-center gap-1">
              <Brain className="w-4 h-4" />
              AI Coach
            </Link>
            <Link href="/watchlist" className="text-slate-300 hover:text-white transition-colors">
              Watchlist
            </Link>
            <Link href="/paper-trading" className="text-slate-300 hover:text-white transition-colors">
              Paper Trading
            </Link>
          </nav>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <div className="hidden md:flex items-center gap-2 text-slate-300">
                  <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4" />
                  </div>
                  <span className="text-sm">{user?.name}</span>
                </div>
                <button
                  onClick={logout}
                  className="p-2 text-slate-400 hover:text-white transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="hidden md:block px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium transition-colors"
              >
                Sign In
              </Link>
            )}
            
            <button
              className="md:hidden p-2 text-slate-400"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-800">
            <nav className="flex flex-col gap-4">
              <Link href="/" className="text-slate-300 hover:text-white transition-colors">
                Dashboard
              </Link>
              <Link href="/ai-coach" className="text-slate-300 hover:text-indigo-400 transition-colors flex items-center gap-2">
                <Brain className="w-4 h-4" />
                AI Coach
              </Link>
              <Link href="/watchlist" className="text-slate-300 hover:text-white transition-colors">
                Watchlist
              </Link>
              <Link href="/paper-trading" className="text-slate-300 hover:text-white transition-colors">
                Paper Trading
              </Link>
              {!isAuthenticated && (
                <Link href="/login" className="text-primary-400 font-medium">
                  Sign In
                </Link>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
