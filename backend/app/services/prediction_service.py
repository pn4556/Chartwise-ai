"""
Prediction Service
Manages prediction caching and scheduling
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Prediction
from app.services.technical_analysis import TechnicalAnalysisService, SignalScore

class PredictionService:
    """Service for managing predictions"""
    
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = timedelta(minutes=15)
    
    @classmethod
    def get_top_picks(cls, symbols: List[str], db: Session = None, limit: int = 10) -> List[Dict]:
        """Get top picks with caching"""
        cache_key = f"top_picks_{','.join(sorted(symbols))}"
        
        # Check cache
        if cache_key in cls._cache:
            cached_time = cls._cache_time.get(cache_key)
            if cached_time and datetime.now() - cached_time < cls.CACHE_DURATION:
                return cls._cache[cache_key][:limit]
        
        # Generate new predictions
        results = TechnicalAnalysisService.scan_multiple(symbols)
        
        # Format results
        formatted = []
        for i, score in enumerate(results[:limit], 1):
            data = TechnicalAnalysisService.get_data(score.symbol, days=1)
            current_price = data[-1]['close'] if data else 0
            
            formatted.append({
                'rank': i,
                'symbol': score.symbol,
                'bullish_score': score.bullish_score,
                'confidence': score.confidence,
                'recommendation': score.recommendation,
                'current_price': current_price,
                'signals': score.signals
            })
        
        # Update cache
        cls._cache[cache_key] = formatted
        cls._cache_time[cache_key] = datetime.now()
        
        return formatted
    
    @classmethod
    def get_prediction(cls, symbol: str, db: Session = None) -> Optional[Dict]:
        """Get prediction for a single symbol with caching"""
        cache_key = f"prediction_{symbol.upper()}"
        
        # Check cache
        if cache_key in cls._cache:
            cached_time = cls._cache_time.get(cache_key)
            if cached_time and datetime.now() - cached_time < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        # Generate new prediction
        score = TechnicalAnalysisService.analyze(symbol)
        if not score:
            return None
        
        # Get additional data
        data = TechnicalAnalysisService.get_data(symbol, days=1)
        current_price = data[-1]['close'] if data else 0
        
        result = {
            'symbol': score.symbol,
            'bullish_score': score.bullish_score,
            'confidence': score.confidence,
            'recommendation': score.recommendation,
            'current_price': current_price,
            'signals': score.signals,
            'technical_score': score.technical_score,
            'trend_score': score.trend_score,
            'volume_score': score.volume_score
        }
        
        # Update cache
        cls._cache[cache_key] = result
        cls._cache_time[cache_key] = datetime.now()
        
        return result
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached predictions"""
        cls._cache.clear()
        cls._cache_time.clear()
    
    @classmethod
    def get_cache_status(cls) -> Dict:
        """Get cache status for monitoring"""
        return {
            'cached_items': len(cls._cache),
            'cache_keys': list(cls._cache.keys())
        }
