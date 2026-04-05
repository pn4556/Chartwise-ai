'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

const API_BASE = 'https://chartwise-api.onrender.com'

interface User {
  id: number
  email: string
  name: string
  avatar_url?: string
  portfolio_value: number
  trades_count: number
  win_rate: number
  created_at: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  getToken: () => string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    // Check for stored auth token
    const storedToken = localStorage.getItem('chartwise_token')
    if (storedToken) {
      setToken(storedToken)
      // Fetch user info with the token
      fetchUserInfo(storedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUserInfo = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Token invalid, clear it
        localStorage.removeItem('chartwise_token')
        setToken(null)
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      localStorage.removeItem('chartwise_token')
      setToken(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    const accessToken = data.access_token
    
    // Store token
    localStorage.setItem('chartwise_token', accessToken)
    setToken(accessToken)
    
    // Fetch user info
    await fetchUserInfo(accessToken)
  }

  const signup = async (email: string, password: string, name: string) => {
    const response = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password, name })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Signup failed')
    }

    const data = await response.json()
    const accessToken = data.access_token
    
    // Store token
    localStorage.setItem('chartwise_token', accessToken)
    setToken(accessToken)
    
    // Fetch user info
    await fetchUserInfo(accessToken)
  }

  const logout = async () => {
    // Call logout endpoint if token exists
    if (token) {
      try {
        await fetch(`${API_BASE}/api/auth/logout`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
    
    // Clear local state
    localStorage.removeItem('chartwise_token')
    setToken(null)
    setUser(null)
  }

  const getToken = () => token

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      signup,
      logout,
      getToken
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
