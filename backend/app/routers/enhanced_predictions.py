"""
Enhanced Predictions Router
API endpoints for the advanced probability-based algorithm
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.services.enhanced_analysis import EnhancedTechnicalAnalysis, PredictionResult

router = APIRouter(prefix="/api/v2", tags=["enhanced-predictions"])


@router.get("/predictions/{symbol}")
async def get_enhanced_prediction(
    symbol: str,
    timeframe: str = Query('1d', enum=['1h', '4h', '1d', '1w']),
    multi_timeframe: bool = Query(False, description="Analyze multiple timeframes")
):
    """
    Get enhanced prediction with probability distribution
    
    Returns:
    - Probabilities for up/down/sideways
    - Confidence score and level
    - Component scores (momentum, trend, volume, volatility)
    - Human-readable reasoning
    - Key support/resistance levels
    """
    try:
        if multi_timeframe:
            result = EnhancedTechnicalAnalysis.analyze_multiple_timeframes(symbol)
        else:
            result = EnhancedTechnicalAnalysis.analyze(symbol, interval=timeframe)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Could not analyze symbol: {symbol}")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{symbol}/probabilities")
async def get_probabilities(symbol: str):
    """
    Get simplified probability distribution only
    
    Quick endpoint for lightweight probability data
    """
    try:
        result = EnhancedTechnicalAnalysis.analyze(symbol)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Could not analyze symbol: {symbol}")
        
        return {
            "symbol": result.symbol,
            "current_price": result.current_price,
            "probabilities": result.probabilities,
            "confidence": result.confidence,
            "recommendation": result.recommendation,
            "timestamp": result.calculated_at
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/top-picks/enhanced")
async def get_enhanced_top_picks(
    limit: int = Query(10, ge=1, le=50),
    min_confidence: float = Query(50.0, ge=0, le=100),
    timeframe: str = Query('1d', enum=['1h', '4h', '1d'])
):
    """
    Get top picks using enhanced algorithm with probability scoring
    
    Ranks stocks by bullish probability with confidence filtering
    """
    # Default universe of stocks
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
        'AMD', 'INTC', 'CRM', 'ADBE', 'PYPL', 'UBER', 'COIN', 'ROKU',
        'AXON', 'SHOP', 'ZM', 'DOCU', 'PLTR', 'SNOW', 'CRWD', 'NET'
    ]
    
    results = []
    
    for symbol in symbols:
        try:
            analysis = EnhancedTechnicalAnalysis.analyze(symbol, interval=timeframe)
            if analysis and analysis.confidence >= min_confidence:
                results.append({
                    "rank": 0,  # Will be assigned after sorting
                    "symbol": analysis.symbol,
                    "current_price": analysis.current_price,
                    "bullish_score": analysis.probabilities['up'],
                    "confidence": analysis.confidence,
                    "probabilities": analysis.probabilities,
                    "recommendation": analysis.recommendation,
                    "reasoning": analysis.reasoning[:100] + "..." if len(analysis.reasoning) > 100 else analysis.reasoning
                })
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            continue
    
    # Sort by bullish probability (descending)
    results.sort(key=lambda x: x['bullish_score'], reverse=True)
    
    # Assign ranks
    for i, result in enumerate(results[:limit], 1):
        result['rank'] = i
    
    return results[:limit]


@router.get("/predictions/compare/{symbol}")
async def compare_algorithms(symbol: str):
    """
    Compare old algorithm vs new enhanced algorithm
    
    Useful for validation and A/B testing
    """
    from app.services.technical_analysis import TechnicalAnalysisService
    
    # Get old algorithm result
    old_result = TechnicalAnalysisService.analyze(symbol)
    
    # Get new algorithm result
    new_result = EnhancedTechnicalAnalysis.analyze(symbol)
    
    if not old_result or not new_result:
        raise HTTPException(status_code=404, detail=f"Could not analyze symbol: {symbol}")
    
    return {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "old_algorithm": {
            "bullish_score": old_result.bullish_score,
            "recommendation": old_result.recommendation,
            "confidence": old_result.confidence
        },
        "new_algorithm": {
            "bullish_score": new_result.probabilities['up'],
            "probabilities": new_result.probabilities,
            "recommendation": new_result.recommendation,
            "confidence": new_result.confidence,
            "confidence_level": new_result.confidence_level
        },
        "comparison": {
            "score_difference": round(new_result.probabilities['up'] - old_result.bullish_score, 1),
            "recommendation_match": old_result.recommendation == new_result.recommendation
        }
    }


@router.get("/market/regime")
async def get_market_regime():
    """
    Detect current market regime (bull/bear/sideways)
    
    Analyzes SPY (S&P 500) to determine overall market conditions
    """
    try:
        spy_analysis = EnhancedTechnicalAnalysis.analyze('SPY')
        
        if not spy_analysis:
            raise HTTPException(status_code=500, detail="Could not analyze market")
        
        # Determine regime
        up_prob = spy_analysis.probabilities['up']
        down_prob = spy_analysis.probabilities['down']
        
        if up_prob > 60:
            regime = "bullish"
            description = "Market showing strong bullish momentum"
        elif up_prob > 50:
            regime = "weak_bullish"
            description = "Market moderately bullish with caution"
        elif down_prob > 60:
            regime = "bearish"
            description = "Market showing bearish pressure"
        elif down_prob > 50:
            regime = "weak_bearish"
            description = "Market moderately bearish with caution"
        else:
            regime = "sideways"
            description = "Market in consolidation phase"
        
        return {
            "regime": regime,
            "description": description,
            "spy_analysis": {
                "price": spy_analysis.current_price,
                "probabilities": spy_analysis.probabilities,
                "confidence": spy_analysis.confidence
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
