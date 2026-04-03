"""
Data Service - Manages data fetching and caching
"""

import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os

class DataService:
    """Service for fetching and managing market data"""
    
    _cache = {}
    _cache_expiry = {}
    CACHE_DURATION = timedelta(minutes=15)  # 15-minute cache
    
    @classmethod
    def initialize(cls):
        """Initialize the data service"""
        print("✅ DataService initialized")
    
    @classmethod
    def get_popular_stocks(cls) -> List[Dict]:
        """Get list of popular stocks with basic info"""
        popular_symbols = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
        ]
        
        stocks = []
        for stock_info in popular_symbols:
            try:
                ticker = yf.Ticker(stock_info['symbol'])
                info = ticker.info
                hist = ticker.history(period='2d')
                
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    change = current - previous
                    change_pct = (change / previous) * 100
                else:
                    current = info.get('currentPrice', 0)
                    change = 0
                    change_pct = 0
                
                stocks.append({
                    'symbol': stock_info['symbol'],
                    'name': stock_info['name'],
                    'price': round(current, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_pct, 2),
                    'volume': info.get('volume', 0),
                    'market_cap': info.get('marketCap', None)
                })
            except Exception as e:
                print(f"Error fetching {stock_info['symbol']}: {e}")
                continue
        
        return stocks
    
    @classmethod
    def get_stock_detail(cls, symbol: str) -> Optional[Dict]:
        """Get detailed stock information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='2d')
            
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change = current - previous
                change_pct = (change / previous) * 100
            else:
                current = info.get('currentPrice', 0)
                change = 0
                change_pct = 0
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'price': round(current, 2),
                'change': round(change, 2),
                'change_percent': round(change_pct, 2),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', None),
                'pe_ratio': info.get('trailingPE', None),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),
                'avg_volume': info.get('averageVolume', None)
            }
        except Exception as e:
            print(f"Error fetching detail for {symbol}: {e}")
            return None
    
    @classmethod
    def get_price_history(cls, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[List[Dict]]:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            history = []
            for date, row in hist.iterrows():
                history.append({
                    'date': date.isoformat(),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume'])
                })
            
            return history
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return None
    
    @classmethod
    def search_stocks(cls, query: str) -> List[Dict]:
        """Search for stocks by symbol or name"""
        # This is a simplified implementation
        # In production, you'd use a proper search API
        popular_stocks = cls.get_popular_stocks()
        query = query.upper()
        
        results = [
            stock for stock in popular_stocks
            if query in stock['symbol'] or query in stock['name'].upper()
        ]
        
        return results[:10]  # Limit to 10 results
