'use client'

import { getScoreColor } from '@/lib/utils'

interface ScoreBadgeProps {
  score: number
  confidence?: number
  size?: 'sm' | 'md' | 'lg'
}

export default function ScoreBadge({ score, confidence, size = 'md' }: ScoreBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2',
  }

  return (
    <div className={`inline-flex flex-col items-center ${getScoreColor(score)} rounded-lg font-bold ${sizeClasses[size]}`}>
      <span>{score.toFixed(0)}%</span>
      {confidence && (
        <span className="text-xs font-normal opacity-70">conf: {confidence}%</span>
      )}
    </div>
  )
}
