'use client'

import { useEffect, useRef, useState } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, HistogramData } from 'lightweight-charts'
import { useSymbolUpdates } from '@/lib/websocket'

interface ChartData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface StockChartProps {
  data: ChartData[]
  symbol: string
}

export default function StockChart({ data, symbol }: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const [timeframe, setTimeframe] = useState('1Y')
  const [livePrice, setLivePrice] = useState<number | null>(null)
  
  // Subscribe to real-time updates for this symbol
  const { predictionData, priceData, isConnected, lastUpdate } = useSymbolUpdates(symbol)

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#0f172a' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#1e293b' },
        horzLines: { color: '#1e293b' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: '#38bdf8',
          labelBackgroundColor: '#38bdf8',
        },
        horzLine: {
          color: '#38bdf8',
          labelBackgroundColor: '#38bdf8',
        },
      },
      rightPriceScale: {
        borderColor: '#334155',
      },
      timeScale: {
        borderColor: '#334155',
        timeVisible: true,
      },
    })

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#3b82f6',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    })

    // Format data for lightweight-charts
    const candleData: CandlestickData[] = data.map(d => ({
      time: d.date,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }))

    const volumeData: HistogramData[] = data.map(d => ({
      time: d.date,
      value: d.volume,
      color: d.close >= d.open ? '#22c55e40' : '#ef444440',
    }))

    candlestickSeries.setData(candleData)
    volumeSeries.setData(volumeData)

    // Scale volume to bottom 20%
    chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    })

    // Fit content
    chart.timeScale().fitContent()

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: 400,
        })
      }
    }

    window.addEventListener('resize', handleResize)
    handleResize()

    // Save refs
    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries
    volumeSeriesRef.current = volumeSeries

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [data])
  
  // Handle real-time price updates
  useEffect(() => {
    if (priceData && candlestickSeriesRef.current && data.length > 0) {
      const currentPrice = priceData.current_price || priceData.price
      if (currentPrice) {
        setLivePrice(currentPrice)
        
        // Update the last candle with new price
        const lastCandle = data[data.length - 1]
        const updatedCandle: CandlestickData = {
          time: lastCandle.date,
          open: lastCandle.open,
          high: Math.max(lastCandle.high, currentPrice),
          low: Math.min(lastCandle.low, currentPrice),
          close: currentPrice,
        }
        candlestickSeriesRef.current.update(updatedCandle)
      }
    }
  }, [priceData, data])
  
  // Handle prediction updates
  useEffect(() => {
    if (predictionData) {
      console.log('Received prediction update:', predictionData)
      // Prediction data can be used to update indicators or show alerts
    }
  }, [predictionData])

  const timeframes = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y']

  return (
    <div className="w-full">
      {/* Timeframe selector */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-white">{symbol} Chart</h3>
          {isConnected && (
            <span className="flex items-center gap-1 text-xs text-success-400">
              <span className="w-2 h-2 bg-success-400 rounded-full animate-pulse" />
              Live
            </span>
          )}
          {livePrice && (
            <span className="text-sm text-slate-400">
              ${livePrice.toFixed(2)}
            </span>
          )}
          {lastUpdate && (
            <span className="text-xs text-slate-500">
              Updated {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className="flex gap-1">
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                timeframe === tf
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Chart container */}
      <div
        ref={chartContainerRef}
        className="w-full h-[400px] bg-slate-900 rounded-lg"
      />

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-success-400 rounded-sm" />
          <span className="text-slate-400">Bullish</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-danger-400 rounded-sm" />
          <span className="text-slate-400">Bearish</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500/50 rounded-sm" />
          <span className="text-slate-400">Volume</span>
        </div>
      </div>
    </div>
  )
}
