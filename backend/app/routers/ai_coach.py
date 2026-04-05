"""
AI Coach Router
Endpoints for AI-powered trading insights and coaching
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.database import get_db
from app.services.ai_coach_service import AICoachService, AIInsight, SectorAIAnalysis
from app.services.enhanced_analysis import EnhancedTechnicalAnalysis
from app.routers.predictions import DEFAULT_STOCKS, DEFAULT_CRYPTOS, SECTOR_MAPPING

router = APIRouter(prefix="/api/ai-coach", tags=["ai-coach"])


@router.get("/insights")
async def get_ai_insights(
    limit: int = Query(20, ge=1, le=50),
    min_confidence: float = Query(40, ge=0, le=100),
    sector: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated insights for top trading opportunities
    """
    insights = []
    
    # Get stocks to analyze
    stocks_to_analyze = DEFAULT_STOCKS[:30]  # Top 30 for speed
    
    # Filter by sector if specified
    if sector:
        stocks_to_analyze = [s for s in stocks_to_analyze if SECTOR_MAPPING.get(s) == sector]
    
    for symbol in stocks_to_analyze[:limit]:
        try:
            # Get analysis
            result = EnhancedTechnicalAnalysis.analyze(symbol)
            if not result:
                continue
            
            # Skip if confidence too low
            if result.confidence < min_confidence:
                continue
            
            # Generate AI insight
            prediction_data = {
                'probabilities': result.probabilities,
                'confidence': result.confidence,
                'bullish_score': result.momentum_score
            }
            
            insight = AICoachService.generate_asset_insight(
                symbol=symbol,
                indicators=result.timeframe_analyses[0] if result.timeframe_analyses else None,
                prediction_data=prediction_data
            )
            
            insights.append({
                'type': insight.type,
                'asset': insight.asset,
                'message': insight.message,
                'confidence': insight.confidence,
                'action': insight.action,
                'timeframe': insight.timeframe,
                'reasoning': insight.reasoning,
                'risk_level': insight.risk_level,
                'timestamp': insight.timestamp,
                'price': result.current_price,
                'probabilities': result.probabilities
            })
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            continue
    
    # Sort by confidence descending
    insights.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        'insights': insights[:limit],
        'count': len(insights),
        'generated_at': datetime.now().isoformat()
    }


@router.get("/sectors")
async def get_sector_ai_analysis(
    db: Session = Depends(get_db)
):
    """
    Get AI analysis for all sectors
    """
    sector_analyses = []
    
    # Get unique sectors
    sectors = list(set(SECTOR_MAPPING.values()))
    
    for sector in sectors:
        # Get stocks in this sector
        sector_stocks = [s for s, sec in SECTOR_MAPPING.items() if sec == sector]
        
        stocks_data = []
        for symbol in sector_stocks[:15]:  # Top 15 per sector
            try:
                result = EnhancedTechnicalAnalysis.analyze(symbol)
                if result:
                    stocks_data.append({
                        'symbol': symbol,
                        'score': result.momentum_score,
                        'confidence': result.confidence,
                        'probabilities': result.probabilities
                    })
            except:
                continue
        
        # Generate sector analysis
        analysis = AICoachService.analyze_sector(sector, stocks_data)
        
        sector_analyses.append({
            'sector': analysis.sector,
            'outlook': analysis.outlook,
            'confidence': analysis.confidence,
            'ai_score': analysis.ai_score,
            'top_picks': analysis.top_picks,
            'avoid': analysis.avoid,
            'insight': analysis.insight,
            'catalysts': analysis.catalysts,
            'risks': analysis.risks,
            'stocks_analyzed': len(stocks_data)
        })
    
    # Sort by AI score
    sector_analyses.sort(key=lambda x: x['ai_score'], reverse=True)
    
    return {
        'sectors': sector_analyses,
        'generated_at': datetime.now().isoformat()
    }


@router.get("/asset/{symbol}")
async def get_asset_ai_insight(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed AI insight for a specific asset
    """
    try:
        result = EnhancedTechnicalAnalysis.analyze(symbol)
        if not result:
            raise HTTPException(status_code=404, detail=f"Could not analyze {symbol}")
        
        prediction_data = {
            'probabilities': result.probabilities,
            'confidence': result.confidence,
            'bullish_score': result.momentum_score
        }
        
        # Get indicators from first timeframe
        indicators = result.timeframe_analyses[0] if result.timeframe_analyses else None
        
        insight = AICoachService.generate_asset_insight(
            symbol=symbol,
            indicators=indicators,
            prediction_data=prediction_data
        )
        
        # Get coaching advice
        coach_advice = AICoachService.get_coach_advice(symbol)
        
        return {
            'asset': symbol,
            'price': result.current_price,
            'insight': {
                'type': insight.type,
                'message': insight.message,
                'confidence': insight.confidence,
                'action': insight.action,
                'timeframe': insight.timeframe,
                'reasoning': insight.reasoning,
                'risk_level': insight.risk_level
            },
            'probabilities': result.probabilities,
            'scores': {
                'momentum': result.momentum_score,
                'trend': result.trend_score,
                'volume': result.volume_score,
                'volatility': result.volatility_score,
                'confidence': result.confidence
            },
            'key_levels': result.key_levels,
            'coach_advice': coach_advice,
            'generated_at': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-summary")
async def get_market_summary(
    db: Session = Depends(get_db)
):
    """
    Get overall AI market summary and top opportunities
    """
    insights = []
    
    # Analyze top stocks
    for symbol in DEFAULT_STOCKS[:20]:
        try:
            result = EnhancedTechnicalAnalysis.analyze(symbol)
            if result and result.confidence >= 50:
                prediction_data = {
                    'probabilities': result.probabilities,
                    'confidence': result.confidence,
                    'bullish_score': result.momentum_score
                }
                
                indicators = result.timeframe_analyses[0] if result.timeframe_analyses else None
                
                insight = AICoachService.generate_asset_insight(
                    symbol=symbol,
                    indicators=indicators,
                    prediction_data=prediction_data
                )
                insights.append(insight)
        except:
            continue
    
    # Generate market summary
    summary = AICoachService.generate_market_summary(insights)
    
    # Get top opportunities
    buy_opportunities = [i for i in insights if i.action == 'buy']
    buy_opportunities.sort(key=lambda x: x.confidence, reverse=True)
    
    warnings = [i for i in insights if i.action == 'sell']
    warnings.sort(key=lambda x: x.confidence, reverse=True)
    
    return {
        'summary': summary,
        'market_conditions': {
            'bullish_setups': len(buy_opportunities),
            'bearish_warnings': len(warnings),
            'neutral': len([i for i in insights if i.action == 'hold']),
            'avg_confidence': sum(i.confidence for i in insights) / len(insights) if insights else 0
        },
        'top_opportunities': [
            {
                'symbol': i.asset,
                'action': i.action,
                'confidence': i.confidence,
                'message': i.message,
                'risk_level': i.risk_level
            }
            for i in buy_opportunities[:5]
        ],
        'warnings': [
            {
                'symbol': i.asset,
                'confidence': i.confidence,
                'message': i.message
            }
            for i in warnings[:5]
        ],
        'generated_at': datetime.now().isoformat()
    }


@router.get("/coach-tip")
async def get_daily_coach_tip():
    """
    Get a daily trading tip from the AI coach
    """
    return AICoachService.get_coach_advice()


@router.get("/predictions")
async def get_ai_predictions(
    type: str = Query("all", regex="^(all|stocks|crypto)$"),
    limit: int = Query(10, ge=1, le=30)
):
    """
    Get AI predictions with up/down forecasts and confidence levels
    """
    predictions = []
    
    symbols = DEFAULT_STOCKS[:20] if type in ['all', 'stocks'] else []
    if type in ['all', 'crypto']:
        symbols.extend(DEFAULT_CRYPTOS[:10])
    
    for symbol in symbols[:limit]:
        try:
            result = EnhancedTechnicalAnalysis.analyze(symbol)
            if not result:
                continue
            
            prob_up = result.probabilities.get('up', 33)
            prob_down = result.probabilities.get('down', 33)
            
            # Determine prediction
            if prob_up > 60:
                prediction = 'UP ⬆️'
                strength = 'Strong' if prob_up > 70 else 'Moderate'
            elif prob_down > 60:
                prediction = 'DOWN ⬇️'
                strength = 'Strong' if prob_down > 70 else 'Moderate'
            else:
                prediction = 'SIDEWAYS ↔️'
                strength = 'Consolidation'
            
            predictions.append({
                'symbol': symbol,
                'prediction': prediction,
                'direction': 'up' if prob_up > prob_down else 'down' if prob_down > prob_up else 'sideways',
                'confidence': result.confidence,
                'probability_up': prob_up,
                'probability_down': prob_down,
                'strength': strength,
                'timeframe': '1-5 days',
                'price': result.current_price
            })
        except:
            continue
    
    # Sort by confidence
    predictions.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        'predictions': predictions,
        'summary': {
            'bullish': len([p for p in predictions if p['direction'] == 'up']),
            'bearish': len([p for p in predictions if p['direction'] == 'down']),
            'neutral': len([p for p in predictions if p['direction'] == 'sideways']),
            'avg_confidence': sum(p['confidence'] for p in predictions) / len(predictions) if predictions else 0
        },
        'generated_at': datetime.now().isoformat()
    }
