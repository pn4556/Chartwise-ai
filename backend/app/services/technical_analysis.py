"""
Technical Analysis Service
Integrates quant-trading-signals skill for indicator calculations
"""

import yfinance as yf
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TechnicalIndicators:
    """Container for technical indicator values"""
    symbol: str
    current_price: float
    rsi: float
    macd_dif: float
    macd_dea: float
    macd_histogram: float
    ma5: float
    ma10: float
    ma20: float
    ma50: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    volume: float
    avg_volume: float

@dataclass
class SignalScore:
    """Container for calculated signal scores"""
    symbol: str
    bullish_score: float  # 0-100
    confidence: float  # 0-100
    technical_score: float
    trend_score: float
    volume_score: float
    signals: Dict[str, str]
    recommendation: str

class TechnicalAnalysisService:
    """
    Technical analysis service based on quant-trading-signals skill
    Calculates indicators and generates trading signals
    """
    
    @staticmethod
    def get_data(symbol: str, days: int = 60) -> Optional[List[Dict]]:
        """Fetch historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f'{days}d')
            if hist is None or len(hist) < 30:
                return None
            
            data = []
            for _, row in hist.iterrows():
                data.append({
                    'close': float(row['Close']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'volume': float(row['Volume']),
                    'date': row.name
                })
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        ema = []
        mult = 2 / (period + 1)
        sma = sum(prices[:period]) / period
        ema.append(sma)
        
        for p in prices[period:]:
            ema.append((p - ema[-1]) * mult + ema[-1])
        return ema
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Dict[str, float]:
        """Calculate MACD indicator"""
        ema12 = TechnicalAnalysisService.calculate_ema(prices, 12)
        ema26 = TechnicalAnalysisService.calculate_ema(prices, 26)
        
        # Align arrays
        diff = len(ema12) - len(ema26)
        ema12 = ema12[diff:]
        
        dif = [ema12[i] - ema26[i] for i in range(len(ema26))]
        dea = TechnicalAnalysisService.calculate_ema(dif, 9)
        
        # Align again
        diff2 = len(dif) - len(dea)
        dif = dif[diff2:]
        
        macd = [(dif[i] - dea[i]) * 2 for i in range(len(dea))]
        
        return {
            'dif': dif[-1] if dif else 0,
            'dea': dea[-1] if dea else 0,
            'macd': macd[-1] if macd else 0
        }
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_g = sum(gains[:period]) / period
        avg_l = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            avg_g = (avg_g * (period - 1) + gains[i]) / period
            avg_l = (avg_l * (period - 1) + losses[i]) / period
        
        if avg_l == 0:
            return 100
        
        return 100 - (100 / (1 + avg_g / avg_l))
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        ma = sum(prices[-period:]) / period
        std = np.std(prices[-period:])
        return (ma + 2 * std, ma, ma - 2 * std)
    
    @classmethod
    def analyze(cls, symbol: str) -> Optional[SignalScore]:
        """
        Complete technical analysis for a symbol
        Returns SignalScore with bullish/bearish rating
        """
        data = cls.get_data(symbol)
        if not data:
            return None
        
        prices = [d['close'] for d in data]
        volumes = [d['volume'] for d in data]
        current_price = prices[-1]
        
        # Calculate indicators
        rsi = cls.calculate_rsi(prices)
        macd = cls.calculate_macd(prices)
        ma5 = cls.calculate_sma(prices, 5)
        ma10 = cls.calculate_sma(prices, 10)
        ma20 = cls.calculate_sma(prices, 20)
        ma50 = cls.calculate_sma(prices, 50)
        bb_upper, bb_middle, bb_lower = cls.calculate_bollinger_bands(prices)
        
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[-20:])
        
        # Create indicators object
        indicators = TechnicalIndicators(
            symbol=symbol,
            current_price=current_price,
            rsi=rsi,
            macd_dif=macd['dif'],
            macd_dea=macd['dea'],
            macd_histogram=macd['macd'],
            ma5=ma5,
            ma10=ma10,
            ma20=ma20,
            ma50=ma50,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            volume=current_volume,
            avg_volume=avg_volume
        )
        
        # Calculate signals
        return cls.calculate_signals(indicators)
    
    @classmethod
    def calculate_signals(cls, ind: TechnicalIndicators) -> SignalScore:
        """
        Calculate composite signal score from indicators
        Based on quant-trading-signals scoring methodology
        """
        bullish_points = 0
        total_points = 0
        signals = {}
        
        # 1. MACD Signal (25% weight)
        if ind.macd_dif > ind.macd_dea:
            bullish_points += 25
            signals['macd'] = 'bullish'
        else:
            signals['macd'] = 'bearish'
        total_points += 25
        
        # 2. RSI Signal (20% weight)
        if ind.rsi < 30:  # Oversold - bullish
            bullish_points += 20
            signals['rsi'] = 'oversold_bullish'
        elif ind.rsi > 70:  # Overbought - bearish
            signals['rsi'] = 'overbought_bearish'
        elif ind.rsi > 50:
            bullish_points += 10
            signals['rsi'] = 'neutral_bullish'
        else:
            signals['rsi'] = 'neutral_bearish'
        total_points += 20
        
        # 3. Moving Average Trend (25% weight)
        ma_bullish = 0
        if ind.current_price > ind.ma5:
            ma_bullish += 1
        if ind.ma5 > ind.ma10:
            ma_bullish += 1
        if ind.ma10 > ind.ma20:
            ma_bullish += 1
        if ind.ma20 > ind.ma50:
            ma_bullish += 1
        
        ma_score = (ma_bullish / 4) * 25
        bullish_points += ma_score
        
        if ma_bullish >= 3:
            signals['ma'] = 'strong_bullish'
        elif ma_bullish >= 2:
            signals['ma'] = 'bullish'
        elif ma_bullish >= 1:
            signals['ma'] = 'weak_bullish'
        else:
            signals['ma'] = 'bearish'
        total_points += 25
        
        # 4. Bollinger Bands (15% weight)
        if ind.current_price < ind.bb_lower:  # Below lower band - bullish reversal
            bullish_points += 15
            signals['bb'] = 'below_lower_bullish'
        elif ind.current_price > ind.bb_upper:  # Above upper band - bearish
            signals['bb'] = 'above_upper_bearish'
        elif ind.current_price > ind.bb_middle:
            bullish_points += 7.5
            signals['bb'] = 'above_middle'
        else:
            signals['bb'] = 'below_middle'
        total_points += 15
        
        # 5. Volume (15% weight)
        if ind.volume > ind.avg_volume * 1.5:  # High volume
            bullish_points += 15
            signals['volume'] = 'high'
        elif ind.volume > ind.avg_volume:
            bullish_points += 7.5
            signals['volume'] = 'above_average'
        else:
            signals['volume'] = 'low'
        total_points += 15
        
        # Calculate final scores
        bullish_score = (bullish_points / total_points) * 100
        
        # Calculate confidence based on signal agreement
        signal_values = list(signals.values())
        bullish_signals = sum(1 for s in signal_values if 'bullish' in s)
        bearish_signals = sum(1 for s in signal_values if 'bearish' in s)
        
        if bullish_signals >= 4 or bearish_signals >= 4:
            confidence = 85
        elif bullish_signals >= 3 or bearish_signals >= 3:
            confidence = 70
        elif bullish_signals >= 2 or bearish_signals >= 2:
            confidence = 55
        else:
            confidence = 40
        
        # Individual component scores
        technical_score = min(100, max(0, bullish_score))
        trend_score = (ma_bullish / 4) * 100
        volume_score = 100 if ind.volume > ind.avg_volume * 1.5 else (50 if ind.volume > ind.avg_volume else 25)
        
        # Recommendation
        if bullish_score >= 80:
            recommendation = "Strong Buy"
        elif bullish_score >= 60:
            recommendation = "Buy"
        elif bullish_score >= 40:
            recommendation = "Hold"
        elif bullish_score >= 20:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"
        
        return SignalScore(
            symbol=ind.symbol,
            bullish_score=round(bullish_score, 1),
            confidence=confidence,
            technical_score=round(technical_score, 1),
            trend_score=round(trend_score, 1),
            volume_score=round(volume_score, 1),
            signals=signals,
            recommendation=recommendation
        )
    
    @classmethod
    def scan_multiple(cls, symbols: List[str]) -> List[SignalScore]:
        """Scan multiple symbols and return sorted results"""
        results = []
        for symbol in symbols:
            score = cls.analyze(symbol)
            if score:
                results.append(score)
        
        # Sort by bullish score (descending)
        results.sort(key=lambda x: x.bullish_score, reverse=True)
        return results
