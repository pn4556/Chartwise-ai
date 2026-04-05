"""
Enhanced Technical Analysis Service
Incorporates Clive's algorithm with probability output and confidence scoring
"""

import yfinance as yf
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class TechnicalIndicators:
    """Container for technical indicator values"""
    symbol: str
    current_price: float
    rsi: float
    stoch_rsi: float
    macd_dif: float
    macd_dea: float
    macd_histogram: float
    cci: float
    adx: float
    plus_di: float
    minus_di: float
    mfi: float
    obv: float
    cmf: float
    ma5: float
    ma10: float
    ma20: float
    ma50: float
    ma200: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    bb_width: float  # Bollinger Band width for squeeze detection
    volume: float
    avg_volume: float
    atr: float
    # New advanced indicators
    vwap: float  # Volume Weighted Average Price
    williams_r: float  # Williams %R
    roc: float  # Rate of Change
    ichimoku_tenkan: float  # Ichimoku Tenkan-sen
    ichimoku_kijun: float  # Ichimoku Kijun-sen
    ichimoku_cloud_top: float  # Ichimoku Senkou Span A
    ichimoku_cloud_bottom: float  # Ichimoku Senkou Span B
    psar: float  # Parabolic SAR
    fib_38_2: float  # Fibonacci 38.2% level
    fib_50: float  # Fibonacci 50% level
    fib_61_8: float  # Fibonacci 61.8% level
    support_level: float  # Key support
    resistance_level: float  # Key resistance
    # Candlestick patterns
    candlestick_pattern: str  # Pattern name or 'none'
    pattern_strength: float  # 0-1 strength score
    # Additional signals
    volume_trend: str  # 'increasing', 'decreasing', 'neutral'
    price_vs_vwap: str  # 'above', 'below', 'at'
    trend_strength_score: float  # 0-100 composite trend score

@dataclass
class TimeframeAnalysis:
    """Analysis for a specific timeframe"""
    timeframe: str
    bullish_score: float
    probabilities: Dict[str, float]
    confidence: float
    signals: Dict[str, str]
    primary_trend: str

@dataclass
class PredictionResult:
    """Complete prediction result with probabilities"""
    symbol: str
    current_price: float
    probabilities: Dict[str, float]
    confidence: float
    confidence_level: str
    momentum_score: float
    trend_score: float
    volume_score: float
    volatility_score: float
    timeframe_alignment: float
    timeframe_consensus: str
    timeframe_analyses: List[TimeframeAnalysis]
    divergences: List[Dict]
    recommendation: str
    action: str
    signals: Dict[str, str]
    reasoning: str
    key_levels: Dict[str, float]
    calculated_at: str
    algorithm_version: str = "3.0-ai-enhanced"


class EnhancedTechnicalAnalysis:
    """Enhanced technical analysis with probability output"""
    
    # Weight configuration (optimized)
    WEIGHTS = {
        'momentum': 0.30,
        'trend': 0.25,
        'support_resistance': 0.20,
        'volume': 0.15,
        'volatility': 0.10
    }
    
    # Momentum indicator weights within category
    MOMENTUM_WEIGHTS = {
        'rsi': 0.25,
        'stoch_rsi': 0.20,
        'macd': 0.25,
        'cci': 0.10,
        'williams_r': 0.12,
        'roc': 0.08
    }
    
    # Trend indicator weights
    TREND_WEIGHTS = {
        'ma_alignment': 0.35,
        'adx_strength': 0.25,
        'ichimoku': 0.25,
        'psar': 0.15
    }
    
    @staticmethod
    def get_data(symbol: str, period: str = '60d', interval: str = '1d') -> Optional[List[Dict]]:
        """Fetch historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            if hist is None or len(hist) < 30:
                return None
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                })
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gains = sum(gains[:period]) / period
        avg_losses = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            avg_gains = (avg_gains * (period - 1) + gains[i]) / period
            avg_losses = (avg_losses * (period - 1) + losses[i]) / period
        
        if avg_losses == 0:
            return 100.0
        
        rs = avg_gains / avg_losses
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_stoch_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Stochastic RSI"""
        if len(prices) < period * 2:
            return 50.0
        
        rsi_values = []
        for i in range(period, len(prices)):
            window = prices[i-period:i]
            rsi = EnhancedTechnicalAnalysis.calculate_rsi(window, period)
            rsi_values.append(rsi)
        
        if len(rsi_values) < period:
            return 50.0
        
        min_rsi = min(rsi_values[-period:])
        max_rsi = max(rsi_values[-period:])
        
        if max_rsi == min_rsi:
            return 50.0
        
        current_rsi = rsi_values[-1]
        return (current_rsi - min_rsi) / (max_rsi - min_rsi) * 100
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate EMA"""
        if len(prices) < period:
            return prices
        
        ema = []
        mult = 2 / (period + 1)
        sma = sum(prices[:period]) / period
        ema.append(sma)
        
        for p in prices[period:]:
            ema.append((p - ema[-1]) * mult + ema[-1])
        return ema
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Dict:
        """Calculate MACD"""
        if len(prices) < 35:
            return {'dif': 0, 'dea': 0, 'histogram': 0, 'signal': 'neutral'}
        
        ema12 = EnhancedTechnicalAnalysis.calculate_ema(prices, 12)
        ema26 = EnhancedTechnicalAnalysis.calculate_ema(prices, 26)
        
        ema12_aligned = ema12[-len(ema26):]
        dif = [ema12_aligned[i] - ema26[i] for i in range(len(ema26))]
        dea = EnhancedTechnicalAnalysis.calculate_ema(dif, 9)
        
        dif_aligned = dif[-len(dea):]
        histogram = [(dif_aligned[i] - dea[i]) for i in range(len(dea))]
        
        current_dif = dif_aligned[-1] if dif_aligned else 0
        current_dea = dea[-1] if dea else 0
        current_hist = histogram[-1] if histogram else 0
        
        # Determine signal
        if len(histogram) >= 2:
            prev_hist = histogram[-2]
            if current_dif > current_dea and prev_hist < 0 < current_hist:
                signal = 'bullish_crossover'
            elif current_dif < current_dea and prev_hist > 0 > current_hist:
                signal = 'bearish_crossover'
            elif current_dif > current_dea:
                signal = 'bullish'
            elif current_dif < current_dea:
                signal = 'bearish'
            else:
                signal = 'neutral'
        else:
            signal = 'neutral'
        
        return {
            'dif': current_dif,
            'dea': current_dea,
            'histogram': current_hist,
            'signal': signal
        }
    
    @staticmethod
    def calculate_cci(highs: List[float], lows: List[float], closes: List[float], period: int = 20) -> float:
        """Calculate CCI"""
        if len(closes) < period:
            return 0.0
        
        tp = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        sma_tp = sum(tp[-period:]) / period
        mean_dev = sum(abs(x - sma_tp) for x in tp[-period:]) / period
        
        if mean_dev == 0:
            return 0.0
        
        return (tp[-1] - sma_tp) / (0.015 * mean_dev)
    
    @staticmethod
    def calculate_adx(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Dict:
        """Calculate ADX with +DI and -DI"""
        if len(closes) < period + 1:
            return {'adx': 25, 'plus_di': 25, 'minus_di': 25, 'trend_strength': 'moderate'}
        
        tr_list = []
        plus_dm_list = []
        minus_dm_list = []
        
        for i in range(1, len(highs)):
            high = highs[i]
            low = lows[i]
            prev_high = highs[i-1]
            prev_low = lows[i-1]
            prev_close = closes[i-1]
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)
            
            plus_dm = max(0, high - prev_high) if (high - prev_high) > (prev_low - low) else 0
            minus_dm = max(0, prev_low - low) if (prev_low - low) > (high - prev_high) else 0
            
            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)
        
        atr = sum(tr_list[-period:]) / period
        plus_di = 100 * (sum(plus_dm_list[-period:]) / period) / atr if atr > 0 else 25
        minus_di = 100 * (sum(minus_dm_list[-period:]) / period) / atr if atr > 0 else 25
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
        
        if dx > 40:
            trend_strength = 'strong'
        elif dx > 25:
            trend_strength = 'moderate'
        elif dx > 15:
            trend_strength = 'weak'
        else:
            trend_strength = 'none'
        
        return {
            'adx': dx,
            'plus_di': plus_di,
            'minus_di': minus_di,
            'trend_strength': trend_strength
        }
    
    @staticmethod
    def calculate_mfi(highs: List[float], lows: List[float], closes: List[float], volumes: List[float], period: int = 14) -> float:
        """Calculate MFI"""
        if len(closes) < period + 1:
            return 50.0
        
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        raw_money_flows = [tp * v for tp, v in zip(typical_prices, volumes)]
        
        positive_flows = []
        negative_flows = []
        
        for i in range(1, len(typical_prices)):
            if typical_prices[i] > typical_prices[i-1]:
                positive_flows.append(raw_money_flows[i])
                negative_flows.append(0)
            else:
                positive_flows.append(0)
                negative_flows.append(raw_money_flows[i])
        
        if len(positive_flows) < period:
            return 50.0
        
        positive_sum = sum(positive_flows[-period:])
        negative_sum = sum(negative_flows[-period:])
        
        if negative_sum == 0:
            return 100.0
        
        money_ratio = positive_sum / negative_sum
        return 100 - (100 / (1 + money_ratio))
    
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate ATR"""
        if len(closes) < period + 1:
            return 0.0
        
        tr_list = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
        
        return sum(tr_list[-period:]) / period
    
    @staticmethod
    def calculate_vwap(highs: List[float], lows: List[float], closes: List[float], volumes: List[float]) -> float:
        """Calculate Volume Weighted Average Price"""
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        total_vol = sum(volumes)
        if total_vol == 0:
            return closes[-1]
        vwap = sum(tp * vol for tp, vol in zip(typical_prices, volumes)) / total_vol
        return vwap
    
    @staticmethod
    def calculate_williams_r(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Williams %R"""
        if len(closes) < period:
            return -50
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        if highest_high == lowest_low:
            return -50
        williams_r = -100 * (highest_high - closes[-1]) / (highest_high - lowest_low)
        return williams_r
    
    @staticmethod
    def calculate_roc(prices: List[float], period: int = 12) -> float:
        """Calculate Rate of Change"""
        if len(prices) < period + 1:
            return 0
        roc = ((prices[-1] - prices[-period - 1]) / prices[-period - 1]) * 100
        return roc
    
    @staticmethod
    def calculate_ichimoku(highs: List[float], lows: List[float], closes: List[float]) -> Dict:
        """Calculate Ichimoku Cloud components"""
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        tenkan_high = max(highs[-9:]) if len(highs) >= 9 else max(highs)
        tenkan_low = min(lows[-9:]) if len(lows) >= 9 else min(lows)
        tenkan = (tenkan_high + tenkan_low) / 2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        kijun_high = max(highs[-26:]) if len(highs) >= 26 else max(highs)
        kijun_low = min(lows[-26:]) if len(lows) >= 26 else min(lows)
        kijun = (kijun_high + kijun_low) / 2
        
        # Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2
        senkou_a = (tenkan + kijun) / 2
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2
        senkou_b_high = max(highs[-52:]) if len(highs) >= 52 else max(highs)
        senkou_b_low = min(lows[-52:]) if len(lows) >= 52 else min(lows)
        senkou_b = (senkou_b_high + senkou_b_low) / 2
        
        return {
            'tenkan': tenkan,
            'kijun': kijun,
            'senkou_a': senkou_a,
            'senkou_b': senkou_b
        }
    
    @staticmethod
    def calculate_parabolic_sar(highs: List[float], lows: List[float], closes: List[float], 
                                af: float = 0.02, max_af: float = 0.2) -> float:
        """Calculate Parabolic SAR"""
        if len(closes) < 2:
            return closes[-1] if closes else 0
        
        # Simplified PSAR calculation
        length = len(closes)
        sar = lows[0]
        ep = highs[0]
        trend = 1  # 1 for uptrend, -1 for downtrend
        
        for i in range(1, min(length, 10)):
            if trend == 1:
                sar = sar + af * (ep - sar)
                if lows[i] < sar:
                    trend = -1
                    sar = ep
                    ep = lows[i]
                    af = 0.02
                elif highs[i] > ep:
                    ep = highs[i]
                    af = min(af + 0.02, max_af)
            else:
                sar = sar + af * (ep - sar)
                if highs[i] > sar:
                    trend = 1
                    sar = ep
                    ep = highs[i]
                    af = 0.02
                elif lows[i] < ep:
                    ep = lows[i]
                    af = min(af + 0.02, max_af)
        
        return sar
    
    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        return {
            '38_2': high - 0.382 * diff,
            '50': high - 0.5 * diff,
            '61_8': high - 0.618 * diff
        }
    
    @staticmethod
    def detect_support_resistance(closes: List[float], highs: List[float], 
                                   lows: List[float], window: int = 10) -> Dict[str, float]:
        """Detect key support and resistance levels using local minima/maxima"""
        if len(closes) < window * 2:
            return {'support': min(closes), 'resistance': max(closes)}
        
        # Find local minima (support)
        supports = []
        for i in range(window, len(lows) - window):
            if all(lows[i] <= lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, window+1)):
                supports.append(lows[i])
        
        # Find local maxima (resistance)
        resistances = []
        for i in range(window, len(highs) - window):
            if all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1)):
                resistances.append(highs[i])
        
        support = max(supports[-3:]) if supports else min(closes)
        resistance = min(resistances[-3:]) if resistances else max(closes)
        
        return {'support': support, 'resistance': resistance}
    
    @staticmethod
    def detect_candlestick_patterns(opens: List[float], highs: List[float], 
                                     lows: List[float], closes: List[float]) -> Dict:
        """Detect common candlestick patterns"""
        if len(closes) < 3:
            return {'pattern': 'none', 'strength': 0}
        
        o, h, l, c = opens[-1], highs[-1], lows[-1], closes[-1]
        prev_o, prev_h, prev_l, prev_c = opens[-2], highs[-2], lows[-2], closes[-2]
        
        body = abs(c - o)
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        total_range = h - l
        
        # Bullish patterns
        # Hammer
        if lower_shadow > 2 * body and upper_shadow < body and c > o:
            return {'pattern': 'hammer_bullish', 'strength': 0.7}
        
        # Bullish Engulfing
        if prev_c < prev_o and c > o and o < prev_c and c > prev_o:
            return {'pattern': 'engulfing_bullish', 'strength': 0.8}
        
        # Morning Star (simplified)
        if len(closes) >= 3:
            prev2_c = closes[-3]
            if prev2_c > opens[-3] and abs(prev_c - prev_o) < 0.3 * abs(prev2_c - opens[-3]) and c > o:
                return {'pattern': 'morning_star', 'strength': 0.85}
        
        # Bearish patterns
        # Shooting Star
        if upper_shadow > 2 * body and lower_shadow < body and c < o:
            return {'pattern': 'shooting_star_bearish', 'strength': 0.7}
        
        # Bearish Engulfing
        if prev_c > prev_o and c < o and o > prev_c and c < prev_o:
            return {'pattern': 'engulfing_bearish', 'strength': 0.8}
        
        # Doji
        if body < 0.1 * total_range:
            return {'pattern': 'doji', 'strength': 0.5}
        
        return {'pattern': 'none', 'strength': 0}
    
    @classmethod
    def calculate_indicators(cls, data: List[Dict]) -> Optional[TechnicalIndicators]:
        """Calculate all technical indicators"""
        if not data or len(data) < 50:
            return None
        
        closes = [d['close'] for d in data]
        highs = [d['high'] for d in data]
        lows = [d['low'] for d in data]
        volumes = [d['volume'] for d in data]
        
        current_price = closes[-1]
        
        rsi = cls.calculate_rsi(closes)
        stoch_rsi = cls.calculate_stoch_rsi(closes)
        macd = cls.calculate_macd(closes)
        cci = cls.calculate_cci(highs, lows, closes)
        adx_data = cls.calculate_adx(highs, lows, closes)
        mfi = cls.calculate_mfi(highs, lows, closes, volumes)
        atr = cls.calculate_atr(highs, lows, closes)
        
        # Moving averages
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        ma50 = sum(closes[-50:]) / 50
        ma200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else ma50
        
        # Bollinger Bands
        bb_middle = ma20
        bb_std = np.std(closes[-20:])
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std
        bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0
        
        current_volume = volumes[-1]
        avg_volume = sum(volumes[-20:]) / 20
        
        # Volume trend
        recent_vol = sum(volumes[-5:]) / 5
        volume_trend = 'increasing' if recent_vol > avg_volume * 1.1 else 'decreasing' if recent_vol < avg_volume * 0.9 else 'neutral'
        
        # OBV calculation
        obv = 0
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]
        
        # Normalize OBV
        avg_vol = sum(volumes) / len(volumes)
        obv_normalized = np.clip(obv / (avg_vol * len(volumes)), -1, 1)
        
        # New advanced indicators
        opens = [d['open'] for d in data]
        
        # VWAP
        vwap = cls.calculate_vwap(highs, lows, closes, volumes)
        price_vs_vwap = 'above' if current_price > vwap else 'below' if current_price < vwap else 'at'
        
        # Williams %R
        williams_r = cls.calculate_williams_r(highs, lows, closes)
        
        # Rate of Change
        roc = cls.calculate_roc(closes)
        
        # Ichimoku Cloud
        ichimoku = cls.calculate_ichimoku(highs, lows, closes)
        
        # Parabolic SAR
        psar = cls.calculate_parabolic_sar(highs, lows, closes)
        
        # Fibonacci levels
        recent_high = max(highs[-20:])
        recent_low = min(lows[-20:])
        fib_levels = cls.calculate_fibonacci_levels(recent_high, recent_low)
        
        # Support/Resistance
        sr_levels = cls.detect_support_resistance(closes, highs, lows)
        
        # Candlestick patterns
        patterns = cls.detect_candlestick_patterns(opens, highs, lows, closes)
        
        # Trend strength composite
        trend_strength_score = (adx_data['adx'] + 
                               (100 if current_price > ma50 else 0) + 
                               (50 if ichimoku['tenkan'] > ichimoku['kijun'] else 0)) / 3
        
        return TechnicalIndicators(
            symbol=data[0].get('symbol', 'UNKNOWN'),
            current_price=current_price,
            rsi=rsi,
            stoch_rsi=stoch_rsi,
            macd_dif=macd['dif'],
            macd_dea=macd['dea'],
            macd_histogram=macd['histogram'],
            cci=cci,
            adx=adx_data['adx'],
            plus_di=adx_data['plus_di'],
            minus_di=adx_data['minus_di'],
            mfi=mfi,
            obv=obv_normalized,
            cmf=0.0,
            ma5=ma5,
            ma10=ma10,
            ma20=ma20,
            ma50=ma50,
            ma200=ma200,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            bb_width=bb_width,
            volume=current_volume,
            avg_volume=avg_volume,
            atr=atr,
            vwap=vwap,
            williams_r=williams_r,
            roc=roc,
            ichimoku_tenkan=ichimoku['tenkan'],
            ichimoku_kijun=ichimoku['kijun'],
            ichimoku_cloud_top=ichimoku['senkou_a'],
            ichimoku_cloud_bottom=ichimoku['senkou_b'],
            psar=psar,
            fib_38_2=fib_levels['38_2'],
            fib_50=fib_levels['50'],
            fib_61_8=fib_levels['61_8'],
            support_level=sr_levels['support'],
            resistance_level=sr_levels['resistance'],
            candlestick_pattern=patterns['pattern'],
            pattern_strength=patterns['strength'],
            volume_trend=volume_trend,
            price_vs_vwap=price_vs_vwap,
            trend_strength_score=trend_strength_score
        )
    
    @staticmethod
    def normalize_indicator(value: float, indicator_type: str) -> float:
        """Normalize indicator to -1 to +1 scale"""
        if indicator_type == 'rsi':
            # RSI 0-100 -> -1 to +1, center at 50
            return (value - 50) / 50
        elif indicator_type == 'stoch_rsi':
            return (value - 50) / 50
        elif indicator_type == 'cci':
            # CCI typically -300 to +300
            return np.clip(value / 200, -1, 1)
        elif indicator_type == 'mfi':
            return (value - 50) / 50
        elif indicator_type == 'macd':
            # MACD unbounded, normalize by recent volatility
            return np.clip(value / 5, -1, 1)
        else:
            return np.clip(value, -1, 1)
    
    @classmethod
    def calculate_momentum_score(cls, ind: TechnicalIndicators) -> Tuple[float, Dict]:
        """Calculate momentum component score"""
        signals = {}
        
        # RSI score
        rsi_normalized = cls.normalize_indicator(ind.rsi, 'rsi')
        if ind.rsi < 30:
            signals['rsi'] = 'oversold_bullish'
        elif ind.rsi > 70:
            signals['rsi'] = 'overbought_bearish'
        elif ind.rsi > 50:
            signals['rsi'] = 'neutral_bullish'
        else:
            signals['rsi'] = 'neutral_bearish'
        
        # Stoch RSI score
        stoch_rsi_normalized = cls.normalize_indicator(ind.stoch_rsi, 'stoch_rsi')
        if ind.stoch_rsi < 20:
            signals['stoch_rsi'] = 'oversold_bullish'
        elif ind.stoch_rsi > 80:
            signals['stoch_rsi'] = 'overbought_bearish'
        elif ind.stoch_rsi > 50:
            signals['stoch_rsi'] = 'neutral_bullish'
        else:
            signals['stoch_rsi'] = 'neutral_bearish'
        
        # MACD score
        macd_signal = 0
        if 'bullish' in ind.macd_histogram:
            macd_signal = 1
        elif 'bearish' in ind.macd_histogram:
            macd_signal = -1
        else:
            macd_normalized = cls.normalize_indicator(ind.macd_histogram, 'macd')
            macd_signal = macd_normalized
        
        if ind.macd_dif > ind.macd_dea:
            signals['macd'] = 'bullish'
        else:
            signals['macd'] = 'bearish'
        
        # CCI score
        cci_normalized = cls.normalize_indicator(ind.cci, 'cci')
        if ind.cci < -100:
            signals['cci'] = 'oversold_bullish'
        elif ind.cci > 100:
            signals['cci'] = 'overbought_bearish'
        else:
            signals['cci'] = 'neutral'
        
        # Williams %R score (range -100 to 0)
        williams_normalized = (ind.williams_r + 50) / 50  # Normalize to -1 to 1
        if ind.williams_r < -80:
            signals['williams_r'] = 'oversold_bullish'
        elif ind.williams_r > -20:
            signals['williams_r'] = 'overbought_bearish'
        elif ind.williams_r > -50:
            signals['williams_r'] = 'neutral_bearish'
        else:
            signals['williams_r'] = 'neutral_bullish'
        
        # Rate of Change score
        roc_normalized = np.clip(ind.roc / 20, -1, 1)  # Normalize ±20% to ±1
        if ind.roc > 10:
            signals['roc'] = 'strong_momentum_bullish'
        elif ind.roc > 5:
            signals['roc'] = 'moderate_momentum_bullish'
        elif ind.roc < -10:
            signals['roc'] = 'strong_momentum_bearish'
        elif ind.roc < -5:
            signals['roc'] = 'moderate_momentum_bearish'
        else:
            signals['roc'] = 'low_momentum'
        
        # Weighted average with new indicators
        momentum_score = (
            rsi_normalized * cls.MOMENTUM_WEIGHTS['rsi'] +
            stoch_rsi_normalized * cls.MOMENTUM_WEIGHTS['stoch_rsi'] +
            macd_signal * cls.MOMENTUM_WEIGHTS['macd'] +
            cci_normalized * cls.MOMENTUM_WEIGHTS['cci'] +
            williams_normalized * cls.MOMENTUM_WEIGHTS['williams_r'] +
            roc_normalized * cls.MOMENTUM_WEIGHTS['roc']
        )
        
        return momentum_score, signals
    
    @classmethod
    def calculate_trend_score(cls, ind: TechnicalIndicators) -> Tuple[float, Dict]:
        """Calculate trend strength and direction"""
        signals = {}
        
        # ADX-based trend strength (FIXED: ADX shows strength, not direction)
        if ind.adx > 40:
            trend_strength = 1.0
            signals['adx'] = 'strong_trend'
        elif ind.adx > 25:
            trend_strength = 0.7
            signals['adx'] = 'moderate_trend'
        elif ind.adx > 15:
            trend_strength = 0.4
            signals['adx'] = 'weak_trend'
        else:
            trend_strength = 0.2
            signals['adx'] = 'no_trend'
        
        # Trend direction from DI
        if ind.plus_di > ind.minus_di:
            trend_direction = 1  # Bullish
            signals['di'] = 'bullish'
        else:
            trend_direction = -1  # Bearish
            signals['di'] = 'bearish'
        
        # Moving average alignment
        ma_bullish = 0
        if ind.current_price > ind.ma5:
            ma_bullish += 1
        if ind.ma5 > ind.ma10:
            ma_bullish += 1
        if ind.ma10 > ind.ma20:
            ma_bullish += 1
        if ind.ma20 > ind.ma50:
            ma_bullish += 1
        if ind.ma50 > ind.ma200:
            ma_bullish += 1
        
        ma_score = (ma_bullish / 5) * 2 - 1  # Normalize to -1 to 1
        
        if ma_bullish >= 4:
            signals['ma'] = 'strong_bullish'
        elif ma_bullish >= 3:
            signals['ma'] = 'bullish'
        elif ma_bullish >= 2:
            signals['ma'] = 'weak_bullish'
        else:
            signals['ma'] = 'bearish'
        
        # Ichimoku Cloud analysis
        ichimoku_bullish = 0
        if ind.current_price > ind.ichimoku_cloud_top:
            ichimoku_bullish += 1
            signals['ichimoku'] = 'above_cloud_bullish'
        elif ind.current_price < ind.ichimoku_cloud_bottom:
            ichimoku_bullish -= 1
            signals['ichimoku'] = 'below_cloud_bearish'
        else:
            signals['ichimoku'] = 'in_cloud_neutral'
        
        if ind.ichimoku_tenkan > ind.ichimoku_kijun:
            ichimoku_bullish += 1
        else:
            ichimoku_bullish -= 1
        
        ichimoku_score = ichimoku_bullish / 2  # -1 to 1
        
        # Parabolic SAR
        if ind.psar < ind.current_price:
            psar_bullish = 1
            signals['psar'] = 'below_price_bullish'
        else:
            psar_bullish = -1
            signals['psar'] = 'above_price_bearish'
        
        # Combine: direction * strength with new indicators
        trend_score = (
            trend_direction * trend_strength * cls.TREND_WEIGHTS['adx_strength'] +
            ma_score * cls.TREND_WEIGHTS['ma_alignment'] +
            ichimoku_score * cls.TREND_WEIGHTS['ichimoku'] +
            psar_bullish * cls.TREND_WEIGHTS['psar']
        )
        
        return trend_score, signals
    
    @classmethod
    def calculate_volume_score(cls, ind: TechnicalIndicators) -> Tuple[float, Dict]:
        """Calculate volume-based score"""
        signals = {}
        
        # Volume intensity
        if ind.volume > ind.avg_volume * 1.5:
            volume_intensity = 1.0
            signals['volume'] = 'very_high'
        elif ind.volume > ind.avg_volume:
            volume_intensity = 0.5
            signals['volume'] = 'above_average'
        elif ind.volume > ind.avg_volume * 0.7:
            volume_intensity = 0.0
            signals['volume'] = 'average'
        else:
            volume_intensity = -0.5
            signals['volume'] = 'low'
        
        # OBV trend
        obv_score = ind.obv  # Already normalized -1 to 1
        signals['obv'] = 'bullish' if obv_score > 0 else 'bearish'
        
        # MFI confirmation
        mfi_normalized = cls.normalize_indicator(ind.mfi, 'mfi')
        if ind.mfi < 20:
            signals['mfi'] = 'oversold_bullish'
        elif ind.mfi > 80:
            signals['mfi'] = 'overbought_bearish'
        else:
            signals['mfi'] = 'neutral'
        
        volume_score = volume_intensity * 0.4 + obv_score * 0.4 + mfi_normalized * 0.2
        
        return volume_score, signals
    
    @classmethod
    def calculate_volatility_score(cls, ind: TechnicalIndicators) -> Tuple[float, Dict]:
        """Calculate volatility-based opportunities"""
        signals = {}
        
        # Bollinger Band position
        bb_range = ind.bb_upper - ind.bb_lower
        if bb_range == 0:
            bb_position = 0.5
        else:
            bb_position = (ind.current_price - ind.bb_lower) / bb_range
        
        # Normalize to -1 to 1 (below middle = negative/bearish, above = positive/bullish)
        bb_score = (bb_position - 0.5) * 2
        
        if ind.current_price < ind.bb_lower:
            signals['bollinger'] = 'below_lower_bullish'
        elif ind.current_price > ind.bb_upper:
            signals['bollinger'] = 'above_upper_bearish'
        elif ind.current_price > ind.bb_middle:
            signals['bollinger'] = 'above_middle'
        else:
            signals['bollinger'] = 'below_middle'
        
        # ATR-based volatility regime
        atr_pct = (ind.atr / ind.current_price) * 100
        if atr_pct > 5:
            volatility_regime = 'high'
            vol_score = -0.3  # High volatility = caution
        elif atr_pct > 2.5:
            volatility_regime = 'moderate'
            vol_score = 0.0
        else:
            volatility_regime = 'low'
            vol_score = 0.2  # Low volatility = potential breakout
        
        signals['volatility'] = volatility_regime
        
        volatility_score = bb_score * 0.7 + vol_score * 0.3
        
        return volatility_score, signals
    
    @classmethod
    def calculate_probabilities(cls, bullish_score: float) -> Dict[str, float]:
        """
        Convert bullish score to probability distribution
        Uses softmax-like transformation with realistic market assumptions
        """
        # Base probabilities (markets chop 70% of time)
        base_sideways = 30
        
        # Adjust based on bullish score
        if bullish_score > 60:
            # Bullish bias
            prob_up = min(80, 50 + (bullish_score - 50) * 1.5)
            prob_down = max(5, 20 - (bullish_score - 50) * 0.5)
            prob_sideways = 100 - prob_up - prob_down
        elif bullish_score < 40:
            # Bearish bias
            prob_down = min(80, 50 + (40 - bullish_score) * 1.5)
            prob_up = max(5, 20 - (40 - bullish_score) * 0.5)
            prob_sideways = 100 - prob_up - prob_down
        else:
            # Neutral zone
            prob_up = 30 + (bullish_score - 50) * 0.5
            prob_down = 30 - (bullish_score - 50) * 0.5
            prob_sideways = 100 - prob_up - prob_down
        
        return {
            'up': round(prob_up, 1),
            'down': round(prob_down, 1),
            'sideways': round(prob_sideways, 1)
        }
    
    @classmethod
    def calculate_confidence(cls, signals: Dict[str, str], indicators: TechnicalIndicators) -> Tuple[float, str]:
        """
        Calculate confidence level based on signal agreement and data quality
        Enhanced with multi-factor validation including trend alignment, volume confirmation,
        pattern recognition, and indicator convergence
        """
        # Count signal types
        bullish_signals = sum(1 for s in signals.values() if 'bullish' in s)
        bearish_signals = sum(1 for s in signals.values() if 'bearish' in s)
        neutral_signals = sum(1 for s in signals.values() if 'neutral' in s)
        total_signals = len(signals)
        
        # Agreement score (highest when most signals align)
        max_agreement = max(bullish_signals, bearish_signals)
        agreement_ratio = max_agreement / total_signals if total_signals > 0 else 0
        base_confidence = agreement_ratio * 100
        
        # Multi-factor confidence modifiers
        modifiers = []
        
        # 1. Trend strength modifier (ADX)
        if indicators.adx > 40:
            modifiers.append(1.15)
        elif indicators.adx > 25:
            modifiers.append(1.08)
        elif indicators.adx > 15:
            modifiers.append(0.95)
        else:
            modifiers.append(0.8)
        
        # 2. Volume confirmation modifier
        if indicators.volume > indicators.avg_volume * 1.5:
            modifiers.append(1.12)
        elif indicators.volume > indicators.avg_volume * 1.2:
            modifiers.append(1.05)
        elif indicators.volume > indicators.avg_volume:
            modifiers.append(1.0)
        else:
            modifiers.append(0.92)
        
        # 3. VWAP confirmation modifier
        price_above_vwap = indicators.current_price > indicators.vwap
        trend_bullish = indicators.trend_strength_score > 50
        if price_above_vwap == trend_bullish:
            modifiers.append(1.08)  # Price aligned with trend vs VWAP
        else:
            modifiers.append(0.95)
        
        # 4. Ichimoku Cloud modifier
        above_cloud = indicators.current_price > indicators.ichimoku_cloud_top
        below_cloud = indicators.current_price < indicators.ichimoku_cloud_bottom
        tenkan_above_kijun = indicators.ichimoku_tenkan > indicators.ichimoku_kijun
        
        if (above_cloud and tenkan_above_kijun) or (below_cloud and not tenkan_above_kijun):
            modifiers.append(1.1)  # Strong cloud signal
        elif above_cloud or below_cloud:
            modifiers.append(1.02)
        else:
            modifiers.append(0.95)  # Price in cloud = uncertainty
        
        # 5. Candlestick pattern modifier
        if indicators.candlestick_pattern != 'none':
            if 'bullish' in indicators.candlestick_pattern and bullish_signals > bearish_signals:
                modifiers.append(1 + indicators.pattern_strength * 0.1)
            elif 'bearish' in indicators.candlestick_pattern and bearish_signals > bullish_signals:
                modifiers.append(1 + indicators.pattern_strength * 0.1)
            else:
                modifiers.append(0.95)  # Pattern contradicts other signals
        
        # 6. Bollinger Band squeeze modifier (potential breakout)
        if indicators.bb_width < 0.05:  # Squeeze
            modifiers.append(0.9)  # Low volatility = waiting for breakout
        elif indicators.bb_width > 0.1:  # Expansion
            modifiers.append(1.05)  # Volatility expansion = confirmation
        
        # 7. Support/Resistance proximity modifier
        near_support = abs(indicators.current_price - indicators.support_level) / indicators.current_price < 0.02
        near_resistance = abs(indicators.current_price - indicators.resistance_level) / indicators.current_price < 0.02
        if near_support and bullish_signals > bearish_signals:
            modifiers.append(1.08)  # Bounce from support
        elif near_resistance and bearish_signals > bullish_signals:
            modifiers.append(1.08)  # Rejection at resistance
        
        # 8. Williams %R confirmation
        williams_bullish = indicators.williams_r > -20  # Overbought but strong
        williams_bearish = indicators.williams_r < -80  # Oversold
        if williams_bearish and bullish_signals > bearish_signals:
            modifiers.append(1.05)  # Oversold + bullish signals
        elif williams_bullish and bearish_signals > bullish_signals:
            modifiers.append(1.05)  # Overbought + bearish signals
        
        # 9. Rate of Change momentum modifier
        if abs(indicators.roc) > 10:  # Strong momentum
            modifiers.append(1.05)
        elif abs(indicators.roc) < 2:  # Weak momentum
            modifiers.append(0.95)
        
        # 10. Multi-timeframe trend alignment (if available)
        if indicators.trend_strength_score > 70:
            modifiers.append(1.08)
        elif indicators.trend_strength_score < 30:
            modifiers.append(0.95)
        
        # Calculate composite modifier (weighted average)
        composite_modifier = sum(modifiers) / len(modifiers) if modifiers else 1.0
        
        # Apply all modifiers
        confidence = min(100, base_confidence * composite_modifier)
        
        # Additional signal diversity bonus (having multiple confirming indicators)
        signal_diversity = len(set(signals.values()))
        if signal_diversity >= 4 and max_agreement >= 3:
            confidence = min(100, confidence * 1.05)
        
        # Classify confidence level
        if confidence >= 80:
            confidence_level = 'very_high'
        elif confidence >= 65:
            confidence_level = 'high'
        elif confidence >= 50:
            confidence_level = 'medium'
        elif confidence >= 35:
            confidence_level = 'low'
        else:
            confidence_level = 'very_low'
        
        return round(confidence, 1), confidence_level
    
    @classmethod
    def generate_reasoning(cls, ind: TechnicalIndicators, signals: Dict, probabilities: Dict) -> str:
        """Generate human-readable explanation"""
        reasons = []
        
        # Primary signal
        if probabilities['up'] > 60:
            primary = f"Strong bullish bias ({probabilities['up']}% probability up)"
        elif probabilities['down'] > 60:
            primary = f"Strong bearish bias ({probabilities['down']}% probability down)"
        elif probabilities['sideways'] > 50:
            primary = f"Sideways consolidation likely ({probabilities['sideways']}% probability)"
        else:
            primary = "Mixed signals - uncertainty in direction"
        
        # Key technical factors
        if 'oversold_bullish' in signals.get('rsi', ''):
            reasons.append("RSI indicates oversold conditions (potential reversal)")
        elif 'overbought_bearish' in signals.get('rsi', ''):
            reasons.append("RSI indicates overbought conditions (potential reversal)")
        
        if 'bullish' in signals.get('macd', ''):
            reasons.append("MACD shows bullish momentum")
        elif 'bearish' in signals.get('macd', ''):
            reasons.append("MACD shows bearish momentum")
        
        if 'strong' in signals.get('adx', ''):
            reasons.append("Strong trend detected (high conviction)")
        elif 'weak' in signals.get('adx', ''):
            reasons.append("Weak trend - range-bound conditions likely")
        
        if signals.get('volume') == 'very_high':
            reasons.append("High volume confirms price action")
        
        # New indicator reasoning
        if ind.candlestick_pattern != 'none':
            pattern_name = ind.candlestick_pattern.replace('_', ' ').title()
            reasons.append(f"{pattern_name} pattern detected (strength: {ind.pattern_strength:.0%})")
        
        if ind.price_vs_vwap == 'above':
            reasons.append("Price above VWAP - bullish institutional flow")
        elif ind.price_vs_vwap == 'below':
            reasons.append("Price below VWAP - bearish institutional flow")
        
        if ind.current_price > ind.ichimoku_cloud_top:
            reasons.append("Price above Ichimoku Cloud - strong bullish structure")
        elif ind.current_price < ind.ichimoku_cloud_bottom:
            reasons.append("Price below Ichimoku Cloud - strong bearish structure")
        
        # Williams %R signal
        if ind.williams_r < -80:
            reasons.append("Williams %R shows oversold conditions")
        elif ind.williams_r > -20:
            reasons.append("Williams %R shows overbought conditions")
        
        # ROC momentum
        if ind.roc > 10:
            reasons.append("Strong positive momentum (ROC)")
        elif ind.roc < -10:
            reasons.append("Strong negative momentum (ROC)")
        
        # Support/Resistance proximity
        price = ind.current_price
        near_support = abs(price - ind.support_level) / price < 0.02
        near_resistance = abs(price - ind.resistance_level) / price < 0.02
        if near_support:
            reasons.append("Price near support level")
        if near_resistance:
            reasons.append("Price near resistance level")
        
        # Combine
        reasoning = primary + ". " + " ".join(reasons[:4])  # Top 4 reasons
        
        return reasoning
    
    @classmethod
    def analyze(cls, symbol: str, interval: str = '1d') -> Optional[PredictionResult]:
        """
        Main analysis function - enhanced with probability output
        """
        # Fetch data
        data = cls.get_data(symbol, period='120d', interval=interval)
        if not data:
            return None
        
        # Calculate indicators
        ind = cls.calculate_indicators(data)
        if not ind:
            return None
        
        # Calculate component scores
        momentum_score, momentum_signals = cls.calculate_momentum_score(ind)
        trend_score, trend_signals = cls.calculate_trend_score(ind)
        volume_score, volume_signals = cls.calculate_volume_score(ind)
        volatility_score, volatility_signals = cls.calculate_volatility_score(ind)
        
        # Combine all signals
        all_signals = {**momentum_signals, **trend_signals, **volume_signals, **volatility_signals}
        
        # Calculate weighted bullish score (-1 to +1)
        bullish_score = (
            momentum_score * cls.WEIGHTS['momentum'] +
            trend_score * cls.WEIGHTS['trend'] +
            volume_score * cls.WEIGHTS['volume'] +
            volatility_score * cls.WEIGHTS['volatility']
        )
        
        # Convert to 0-100 scale
        bullish_score_100 = (bullish_score + 1) * 50
        
        # Calculate probabilities (THE KEY ENHANCEMENT!)
        probabilities = cls.calculate_probabilities(bullish_score_100)
        
        # Calculate confidence
        confidence, confidence_level = cls.calculate_confidence(all_signals, ind)
        
        # Determine recommendation
        if bullish_score_100 >= 80:
            recommendation = "Strong Buy"
            action = "strong_buy"
        elif bullish_score_100 >= 60:
            recommendation = "Buy"
            action = "buy"
        elif bullish_score_100 >= 40:
            recommendation = "Hold"
            action = "hold"
        elif bullish_score_100 >= 20:
            recommendation = "Sell"
            action = "sell"
        else:
            recommendation = "Strong Sell"
            action = "strong_sell"
        
        # Generate reasoning
        reasoning = cls.generate_reasoning(ind, all_signals, probabilities)
        
        # Key levels
        key_levels = {
            'support': round(ind.bb_lower, 2),
            'resistance': round(ind.bb_upper, 2),
            'middle': round(ind.bb_middle, 2),
            'ma50': round(ind.ma50, 2),
            'ma200': round(ind.ma200, 2)
        }
        
        # Create timeframe analysis (simplified - single timeframe for now)
        timeframe_analysis = TimeframeAnalysis(
            timeframe=interval,
            bullish_score=round(bullish_score_100, 1),
            probabilities=probabilities,
            confidence=confidence,
            signals=all_signals,
            primary_trend='bullish' if bullish_score > 0 else 'bearish'
        )
        
        return PredictionResult(
            symbol=symbol,
            current_price=round(ind.current_price, 2),
            probabilities=probabilities,
            confidence=confidence,
            confidence_level=confidence_level,
            momentum_score=round((momentum_score + 1) * 50, 1),
            trend_score=round((trend_score + 1) * 50, 1),
            volume_score=round((volume_score + 1) * 50, 1),
            volatility_score=round((volatility_score + 1) * 50, 1),
            timeframe_alignment=confidence,  # Simplified
            timeframe_consensus=action,
            timeframe_analyses=[timeframe_analysis],
            divergences=[],  # Placeholder for future enhancement
            recommendation=recommendation,
            action=action,
            signals=all_signals,
            reasoning=reasoning,
            key_levels=key_levels,
            calculated_at=datetime.now().isoformat()
        )
    
    @classmethod
    def analyze_multiple_timeframes(cls, symbol: str) -> Optional[PredictionResult]:
        """
        Analyze multiple timeframes and aggregate results
        """
        timeframes = ['1h', '4h', '1d']
        analyses = []
        
        for tf in timeframes:
            analysis = cls.analyze(symbol, interval=tf)
            if analysis:
                analyses.append(analysis)
        
        if not analyses:
            return None
        
        # Weight timeframes (higher weight for longer timeframes)
        weights = {'1h': 0.2, '4h': 0.3, '1d': 0.5}
        
        weighted_bullish = sum(
            a.timeframe_analyses[0].bullish_score * weights.get(a.timeframe_analyses[0].timeframe, 0.33)
            for a in analyses
        )
        
        weighted_confidence = sum(
            a.confidence * weights.get(a.timeframe_analyses[0].timeframe, 0.33)
            for a in analyses
        )
        
        # Check for divergences
        divergences = []
        bullish_count = sum(1 for a in analyses if a.probabilities['up'] > 50)
        bearish_count = sum(1 for a in analyses if a.probabilities['down'] > 50)
        
        if bullish_count > 0 and bearish_count > 0:
            divergences.append({
                'type': 'timeframe_divergence',
                'description': f'Mixed signals across timeframes ({bullish_count} bullish, {bearish_count} bearish)',
                'severity': 'medium' if abs(bullish_count - bearish_count) <= 1 else 'high'
            })
        
        # Use daily analysis as base, update with multi-timeframe data
        base_analysis = analyses[-1]  # Daily
        base_analysis.timeframe_alignment = weighted_confidence
        base_analysis.timeframe_analyses = [a.timeframe_analyses[0] for a in analyses]
        base_analysis.divergences = divergences
        
        # Recalculate probabilities with multi-timeframe weighting
        base_analysis.probabilities = cls.calculate_probabilities(weighted_bullish)
        
        return base_analysis
