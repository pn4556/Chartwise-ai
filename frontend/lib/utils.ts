import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price)
}

export function formatPercentage(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}

export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-success-400 bg-success-500/20'
  if (score >= 60) return 'text-success-300 bg-success-500/10'
  if (score >= 40) return 'text-yellow-400 bg-yellow-500/10'
  if (score >= 20) return 'text-danger-300 bg-danger-500/10'
  return 'text-danger-400 bg-danger-500/20'
}

export function getRecommendationColor(rec: string): string {
  if (rec.includes('Strong Buy')) return 'text-success-400'
  if (rec.includes('Buy')) return 'text-success-300'
  if (rec.includes('Hold')) return 'text-yellow-400'
  if (rec.includes('Strong Sell')) return 'text-danger-400'
  return 'text-danger-300'
}
